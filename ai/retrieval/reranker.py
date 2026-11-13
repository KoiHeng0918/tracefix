import json
import re

from langchain_core.messages import HumanMessage, SystemMessage


SYSTEM_PROMPT = """
你是 Java 报错诊断系统的检索重排器。
根据用户报错，把候选案例按相关性从高到低排序。
只能使用给定的 case_no，不能新增、遗漏或重复。
只输出 JSON，格式为：{"order": ["case_no1", "case_no2", ...]}。
不要输出解释、Markdown 或代码块。
""".strip()

# 解析 LLM 输出 + 严格校验
def parse_order(content, valid_ids):
    text = (content or "").strip()
    #  LLM 输出外面裹的 Markdown 壳剥掉
    #  露出里面干净的 JSON，好让 json.loads 能解析
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except Exception:
        # 降级操作，LLM返回格式异常尝试找其中包含的JSON
        # 在 text 里找到"从 { 到 } 的整段内容"并返回
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            return None

        # 最终兜底，降级后依旧无法加载返回None
        try:
            data = json.loads(match.group(0))
        except Exception:
            return None

    order = data.get("order") if isinstance(data, dict) else None
    # 校验order是否合法
    if not isinstance(order, list):
        return None
    if len(order) != len(valid_ids) or set(order) != set(valid_ids):
        return None
    return order

# 把候选列表压成一段"给 LLM 看的精简 JSON 文本
def build_candidate_text(candidates):
    compact = [
        {
            "case_no": item["case_no"],
            "title": item.get("title") or "",
            "message_pattern": item.get("message_pattern") or "",
            "root_cause": item.get("root_cause") or "",
        }
        for item in candidates
    ]
    return json.dumps(compact, ensure_ascii=False)


def rerank_candidates(model, query, candidates):
    """返回 (重排后的候选, 是否得到合法排序)；失败时保留原顺序。"""

    # 候选太少（0 或 1 个），排序没意义，直接返回
    if len(candidates) <= 1:
        return candidates, True

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"用户报错：\n{query}\n\n"
                f"候选案例：\n{build_candidate_text(candidates)}\n\n"
                "请只返回 JSON 排序。"
            )
        ),
    ]
    response = model.invoke(messages)

    content = response.content if isinstance(response.content, str) else str(response.content)

    order = parse_order(content, {item["case_no"] for item in candidates})
    if order is None:
        return candidates, False

    by_id = {item["case_no"]: item for item in candidates}
    
    return [by_id[case_no] for case_no in order], True
