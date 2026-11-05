"""
第一版关键词检索。

目标：从 MySQL 的 ACTIVE 案例里，找出和当前报错最相似的案例。
这一版不做 embedding，也不做 FAISS，先把检索链路跑通。
"""

from retrieval.case_repository import list_active_cases


def tokenize(text):

    # 把文本转小写并分割为单词然后去重
    return set((text or "").lower().split())


class CaseRetriever:
    def retrieve(self, exception, message, top_k=5):
        """按异常类型和消息关键词给案例打分，返回前 top_k 条。"""

        # 获取与用户输入匹配的案例集
        cases = list_active_cases()

        # 把用户输入的message_pattern的单词去重设为集合
        query_words = tokenize(message)


        results = []

        for case in cases:
            score = 0

            # 1. 异常类型完全一样，加 5 分
            if case["exception_type"] == exception:
                score += 5

            # 2. 消息里相同单词越多，分数越高
            case_words = tokenize(case.get("message_pattern"))

            # query_words & case_words取交集，返回集合
            # len()计算交集长度
            score += len(query_words & case_words)

            # 3. 有分数才加入结果
            if score > 0:
                item = {
                    "case_no": case["case_no"],
                    "title": case["title"],
                    "score": score,
                    "message_pattern": case.get("message_pattern"),
                }
                # 高分时把案例答案也带出来
                if score >= 5:
                    item["root_cause"] = case.get("root_cause")
                    item["fix_steps"] = case.get("fix_steps")
                    item["verification"] = case.get("verification")
                results.append(item)

        # 4. 按分数从高到低排序，并取前 top_k 条
        # lambda  参数  :  表达式
        # 把 每个字典的score作为排序规则
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]
