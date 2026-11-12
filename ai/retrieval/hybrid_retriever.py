from retrieval.case_retriever import CaseRetriever
from retrieval.vector_retriever import VectorRetriever


class HybridRetriever:
    """关键词检索 + 向量检索的 RRF 融合。"""

    def __init__(self, keyword_retriever=None, vector_retriever=None, k=60):
        # 复用外部已经创建好的检索器，避免重复加载索引/数据库
        self.keyword_retriever = keyword_retriever or CaseRetriever()
        self.vector_retriever = vector_retriever or VectorRetriever()
        # RRF 的平滑常数，常用默认值 60
        self.k = k

    def retrieve(self, query, exception, message, top_k=5):
        # 关键词检索使用解析后的 exception/message
        keyword_candidates = self.keyword_retriever.retrieve(
            exception,
            message,
            top_k=top_k,
        )

        # 向量检索使用原始用户输入
        vector_candidates = self.vector_retriever.retrieve(
            query,
            top_k=top_k,
        )

        # case_no -> 合并后的候选案例
        merged = {}

        def add_candidates(candidates):
            rank = 1
            for case in candidates:
                case_no = case["case_no"]
                rrf_score = 1.0 / (self.k + rank)

                if case_no not in merged:
                    merged[case_no] = dict(case)
                    merged[case_no]["score"] = 0.0
                else:
                    # 遍历案例的每个字段
                    # 如果是 score，跳过，不要覆盖 RRF 分数
                    # 如果 merged 里这个字段还没有值，就从当前案例补上
                    for key, value in case.items():
                        if key != "score" and not merged[case_no].get(key):
                            merged[case_no][key] = value

                # 每个候选都累加本列表的 RRF 分数；
                # 同一案例第二次出现时，就自然形成两路分数相加
                merged[case_no]["score"] += rrf_score
                rank += 1



        add_candidates(keyword_candidates)
        add_candidates(vector_candidates)

        results = sorted(
            merged.values(),
            key=lambda item: item["score"],
            reverse=True,
        )
        return results[:top_k]
