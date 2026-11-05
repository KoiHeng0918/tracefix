from typing import TypedDict
from langgraph.graph import END, StateGraph
from retrieval.case_retriever import CaseRetriever


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
    candidates = CaseRetriever().retrieve(
        state["exception"],
        state["message"],
    )

    return {
        "candidates": candidates,
    }


def assess_evidence(state: DiagnosisState) -> DiagnosisState:
    candidates = state.get("candidates", [])

    if candidates:
        top_candidate = candidates[0]
        top_score = top_candidate["score"]
        state["evidence_score"] = min(top_score / 10, 1.0)
        if state["evidence_score"] >= 0.6:
            state["missing_info"] = []
        else:
            state["missing_info"] = ["检索的案例证据不足"]
    else:
        state["evidence_score"] = 0.0
        state["missing_info"] = ["没有匹配到案例"]


    return state


def generate(state: DiagnosisState) -> DiagnosisState:
    # TODO: 调 DeepSeek，生成结构化诊断
    top = state["candidates"][0]
    state["diagnosis"] = {
        "title": top.get("title", ""),
        "rootCause": top.get("root_cause", ""),
        "fixSteps": top.get("fix_steps", ""),
        "verification": top.get("verification", ""),
        "confidence": 0.8,
    }
    state["status"] = "DIAGNOSED"
    state["citations"] = [top["case_no"]]
    return state



def validate_citations(state: DiagnosisState) -> DiagnosisState:

    candidates = state.get("candidates", [])
    valid_ids = {case["case_no"] for case in candidates}
    citations = state.get("citations", [])
    state["matched_case_ids"] = [
        case_id for case_id in citations
        if case_id in valid_ids
    ]
    return state


def route_after_assess(state: DiagnosisState) -> str:
    if state.get("evidence_score", 0) >= 0.6:
        return "generate"
    return "ask_or_abstain"


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
    graph.add_conditional_edges("assess", route_after_assess, {
        "generate": "generate",
        "ask_or_abstain": "ask_or_abstain",
    })
    graph.add_edge("generate", "validate")
    graph.add_edge("validate", END)
    graph.add_edge("ask_or_abstain", END)
    return graph.compile()
