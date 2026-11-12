from retrieval.bm25_retriever import BM25Retriever
from retrieval.case_retriever import CaseRetriever
from retrieval.vector_retriever import VectorRetriever


def rrf_merge(candidate_lists, top_k=5, k=60):
    """把任意多组候选列表按 RRF 合并。"""

    # case_no -> 合并后的候选案例
    merged = {}

    for candidates in candidate_lists:
        for rank, case in enumerate(candidates, start=1):
            case_no = case["case_no"]
            rrf_score = 1.0 / (k + rank)

            if case_no not in merged:
                merged[case_no] = dict(case)
                merged[case_no]["score"] = 0.0
            else:
                # 补齐另一个检索器带来的字段，不覆盖已有的非空字段
                for key, value in case.items():
                    if key != "score" and not merged[case_no].get(key):
                        merged[case_no][key] = value

            # 每个候选都累加本列表的 RRF 分数；
            # 同一案例在多个列表出现时，分数自然相加
            merged[case_no]["score"] += rrf_score

    results = sorted(
        merged.values(),
        key=lambda item: item["score"],
        reverse=True,
    )
    return results[:top_k]


class HybridRetriever:
    """关键词检索 + 向量检索的 RRF 融合。"""

    def __init__(self, keyword_retriever=None, vector_retriever=None, k=60):
        # 显式判断 None，避免依赖对象的真值判断
        if keyword_retriever is None:
            keyword_retriever = CaseRetriever()
        if vector_retriever is None:
            vector_retriever = VectorRetriever()

        self.keyword_retriever = keyword_retriever
        self.vector_retriever = vector_retriever
        # k：平滑常数
        # k 越大，分差被压缩；
        # k 越小，头部独大，后面几乎没分。
        self.k = k

    def retrieve(self, query, exception, message, top_k=5):
        keyword_candidates = self.keyword_retriever.retrieve(
            exception,
            message,
            top_k=top_k,
        )
        vector_candidates = self.vector_retriever.retrieve(
            query,
            top_k=top_k,
        )
        return rrf_merge(
            [keyword_candidates, vector_candidates],
            top_k=top_k,
            k=self.k,
        )


class BM25VectorHybridRetriever:
    """BM25 检索 + 向量检索的 RRF 融合。"""

    def __init__(self, bm25_retriever=None, vector_retriever=None, k=60):
        if bm25_retriever is None:
            bm25_retriever = BM25Retriever()
        if vector_retriever is None:
            vector_retriever = VectorRetriever()

        self.bm25_retriever = bm25_retriever
        self.vector_retriever = vector_retriever
        self.k = k

    def retrieve(self, query, top_k=5):
        bm25_candidates = self.bm25_retriever.retrieve(
            query,
            top_k=top_k,
        )
        vector_candidates = self.vector_retriever.retrieve(
            query,
            top_k=top_k,
        )
        return rrf_merge(
            [bm25_candidates, vector_candidates],
            top_k=top_k,
            k=self.k,
        )
