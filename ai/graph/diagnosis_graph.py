from typing import TypedDict
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import END, StateGraph
from retrieval.bm25_retriever import BM25Retriever
from retrieval.case_retriever import CaseRetriever
from retrieval.reranker import rerank_candidates
from retrieval.vector_retriever import VectorRetriever
import json

vector_retriever = VectorRetriever()
bm25_retriever = BM25Retriever()
case_retriever = CaseRetriever()

# 不同检索器的分数尺度不同，过滤阈值按来源配置。
SCORE_THRESHOLDS = {
    "vector": 5.0,
    "bm25": 6.0,
    "keyword": 5.0,
}

# 证据充分度门槛。vector 分数经过 0~10 缩放，
# 0.55 约等于 vector top1 score >= 5.5。
EVIDENCE_THRESHOLD = 0.55

# 先过滤候选，再用 DeepSeek 做 Top1 重排。
RERANK_ENABLED = True


class DiagnosisState(TypedDict, total=False):
    # 用户粘贴的报错
    trace: str
    # 补充信息：版本、代码片段、配置等
    context: str
    # 从报错中提取的异常全限定名
    exception: str
    # 归一化后的报错 信息
    message: str
    # 根据异常和归一化消息生成的指纹
    fingerprint: str
    # 检索到的完整候选案例列表
    candidates: list
    # 当前候选来自哪个检索器：vector / bm25 / keyword
    retrieval_source: str
    # 从候选案例中提取的案例编号
    matched_case_ids: list
    # 证据充分度分数（0-1），不是模型置信度
    evidence_score: float
    # 大模型生成的结构化诊断结果
    diagnosis: dict
    # 最终引用的案例编号，必须来自 candidates
    citations: list
    # 生成或校验失败后的重试次数
    retry_count: int
    # 用于判断是否信息不足需要补充
    missing_info: list
    # 当前流程状态，如 DIAGNOSED / NEED_INFO / ABSTAINED
    status: str

# 检索阶段节点，负责检索符合的案例集
# 处理状态中的candidates
def retrieve(state: DiagnosisState) -> DiagnosisState:
    candidates = []
    source = "vector"

    # 主路径：向量检索
    try:
        candidates = vector_retriever.retrieve(
            state["trace"],
            top_k=5,
        )
    except Exception:
        candidates = []

    # 第一次降级：BM25
    if not candidates:
        source = "bm25"
        try:
            candidates = bm25_retriever.retrieve(
                state["trace"],
                top_k=5,
            )
        except Exception:
            candidates = []

    # 最后兜底：原来的关键词检索
    if not candidates:
        source = "keyword"
        try:
            candidates = case_retriever.retrieve(
                state["exception"],
                state["message"],
                top_k=5,
            )
        except Exception:
            candidates = []

    return {
        "candidates": candidates,
        "retrieval_source": source,
    }

# 证据判断阶段节点，负责判断分数最高的案例集是否合格
# 处理了状态的evidence_score，missing_info
def assess_evidence(state: DiagnosisState) -> DiagnosisState:
    candidates = state.get("candidates", [])

    if candidates:
        source = state.get("retrieval_source", "vector")
        min_score = SCORE_THRESHOLDS.get(source, 5.0)
        top_candidate = candidates[0]
        top_score = top_candidate["score"]
        state["evidence_score"] = min(top_score / 10, 1.0)

        # 有匹配案例时
        # 对最高分案例过滤
        if state["evidence_score"] >= EVIDENCE_THRESHOLD and top_score >= min_score:
            state["missing_info"] = []
        else:
            state["missing_info"] = ["检索的案例证据不足"]
    else:
        state["evidence_score"] = 0.0
        state["missing_info"] = ["没有匹配到案例"]


    return state

# 生成节点generate，case_is_complete为generate用到的函数
# 涉及了状态里关于诊断的字段diagnosis,status,missing_info
def case_is_complete(case: dict) -> bool:
    for field in ["root_cause", "fix_steps", "verification"]:
        value = (case.get(field) or "").strip()
        if not value or value == "待补充":
            return False
    return True
def generate(state: DiagnosisState) -> DiagnosisState:
    candidates = state.get("candidates", [])
    if not candidates:
        state["status"] = "NEED_INFO"
        state["missing_info"] = ["没有候选案例"]
        state["diagnosis"] = {}
        return state

    model = init_chat_model(model="deepseek-chat", model_provider="deepseek")

    # 上一节点仅对最高分判定
    # 对所有候选案例都进一步过滤
    # 过滤出候选案例
    source = state.get("retrieval_source", "vector")
    min_score = SCORE_THRESHOLDS.get(source, 5.0)
    candidates_text = []
    for candidate in candidates:
        if candidate["score"] >= min_score:
            candidates_text.append(candidate)

    if not candidates_text:
        state["status"] = "NEED_INFO"
        state["missing_info"] = ["候选案例分数不足"]
        state["diagnosis"] = {}
        return state

    # 先按检索分数过滤，再对过滤后的候选做 Top1 重排。
    # 重排只改变顺序，不引入新案例；失败时保留原顺序。
    if RERANK_ENABLED and len(candidates_text) > 1:
        try:
            rerank_model = init_chat_model(
                model="deepseek-chat",
                model_provider="deepseek",
                temperature=0,
            )
            candidates_text, _ = rerank_candidates(
                rerank_model,
                state["trace"],
                candidates_text,
            )
        except Exception:
            pass

    # 数据类型转换为json
    final_text = json.dumps(candidates_text, ensure_ascii=False)
    message = [
        SystemMessage(content="""
            你是 Java 报错诊断助手。只能根据提供的候选案例回答。
            不能编造案例编号，不能编造不存在的修复步骤。
            证据不足时返回 missingInfo，不要硬答。
            必须只输出 JSON，字段为：
            title, rootCause, fixSteps, verification, citations, confidence, missingInfo。
            citations 只能从候选案例的 case_no 中选择。
            """
        ),
        HumanMessage(content=f"""
        报错类型：{state["exception"]}
        报错消息：{state["message"]}
        用户补充信息：{state.get("context") or "无"}
        候选案例：
        {final_text}
        请只输出 JSON。
        """)
    ]


    # 大模型的调用返回，主要涉及诊断内容
    # title，rootCause，fixSteps，verification，confidence
    response = model.invoke(message)
    content = response.content

    try:
        data = json.loads(content)
    except Exception:
        # 模型返回格式异常时，降级为 top1 模板
        top = candidates_text[0]

        # 降级前检查top1核心字段是否齐全

        if not case_is_complete(top):
            state["diagnosis"] = {}
            state["citations"] = [top["case_no"]]
            state["missing_info"] = ["top1 案例字段不完整"]
            state["status"] = "NEED_INFO"
            return state

        state["diagnosis"] = {
            "title": top.get("title", ""),
            "rootCause": top.get("root_cause", ""),
            "fixSteps": top.get("fix_steps", ""),
            "verification": top.get("verification", ""),
            "confidence": 0.8,
        }
        state["citations"] = [top["case_no"]]
        state["missing_info"] = []
        state["status"] = "DIAGNOSED"
        return state

    # 只有证据足够时，才要求核心答案字段完整
    if not data.get("missingInfo"):
        required_fields = ["rootCause", "fixSteps", "verification"]
        if any(not data.get(field) for field in required_fields):
            top = candidates_text[0]
            # 降级前检查top1核心字段是否齐全
            if not case_is_complete(top):
                state["diagnosis"] = {}
                state["citations"] = [top["case_no"]]
                state["missing_info"] = ["top1 案例字段不完整"]
                state["status"] = "NEED_INFO"
                return state
            state["diagnosis"] = {
                "title": top.get("title", ""),
                "rootCause": top.get("root_cause", ""),
                "fixSteps": top.get("fix_steps", ""),
                "verification": top.get("verification", ""),
                "confidence": 0.8,
            }
            state["citations"] = [top["case_no"]]
            state["missing_info"] = []
            state["status"] = "DIAGNOSED"
            return state

    state["diagnosis"] = {
        "title": data.get("title") or candidates_text[0].get("title", ""),
        "rootCause": data.get("rootCause") or "",
        "fixSteps": data.get("fixSteps") or "",
        "verification": data.get("verification") or "",
        "confidence": data.get("confidence", 0.8),
    }
    state["citations"] = data.get("citations") or []
    state["missing_info"] = data.get("missingInfo") or []
    state["status"] = "NEED_INFO" if state["missing_info"] else "DIAGNOSED"
    return state


# 校验阶段节点
# 处理match_case_ids
def validate_citations(state: DiagnosisState) -> DiagnosisState:

    candidates = state.get("candidates", [])
    # 有效编号
    valid_ids = {case["case_no"] for case in candidates}
    citations = state.get("citations", [])
    state["matched_case_ids"] = [
        case_id for case_id in citations
        if case_id in valid_ids
    ]
    if not state["matched_case_ids"]:
        state["status"] = "NEED_INFO"
        state["missing_info"] = ["引用校验失败或没有有效引用"]
    return state



def ask_or_abstain(state: DiagnosisState) -> DiagnosisState:
    state["status"] = "NEED_INFO"
    state["matched_case_ids"] = []
    return state


def build_graph():
    graph = StateGraph(DiagnosisState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("assess", assess_evidence)
    graph.add_node("generate", generate)
    graph.add_node("validate", validate_citations)
    graph.add_node("ask_or_abstain", ask_or_abstain)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "assess")

    def route_after_assess(state: DiagnosisState) -> str:
        if state.get("evidence_score", 0) >= EVIDENCE_THRESHOLD:
            return "generate"
        return "ask_or_abstain"

    graph.add_conditional_edges("assess", route_after_assess, {
        "generate": "generate",
        "ask_or_abstain": "ask_or_abstain",
    })
    graph.add_edge("generate", "validate")
    graph.add_edge("validate", END)
    graph.add_edge("ask_or_abstain", END)
    return graph.compile()
