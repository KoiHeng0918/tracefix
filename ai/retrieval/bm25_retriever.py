import math
import re

from retrieval.case_repository import list_active_cases

# 英文开头的包含英文数字与_.$的为一段
# 纯数字为一段
# 中文连续片段为一段
TOKEN_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_.$]*|\d+|[一-鿿]+")

# 只认"纯汉字串"，混杂任何非汉字（英文、数字、空格、标点、生僻字）都不匹配
CHINESE_RE = re.compile(r"^[一-鿿]+$")

#
def tokenize(text: str) -> list[str]:
    """英文按词，中文按单字 + 二元组切分。
    中文单字保障召回，二元组保障精确度"""
    tokens = []
    # text or ""：防止 None。
    # .lower()：统一小写。
    # findall：把文本切成英文、数字、中文片段
    for part in TOKEN_RE.findall((text or "").lower()):
        # append(x)	一个元素	把 x 整体作为一个元素塞进去	[].append("ab") → ["ab"]
        # extend(it)	一个可迭代对象	把 it 拆开，逐个元素追加	[].extend("ab") → ["a","b"]
        if CHINESE_RE.match(part):


            # 中文单字
            tokens.extend(part)
            # 中文二元组：数据、据库、库连...
            tokens.extend(part[i:i + 2] for i in range(len(part) - 1))
        else:
            tokens.append(part)
    return tokens


class BM25Retriever:
    """在 ACTIVE 案例上做 BM25 关键词检索。"""

    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.cases = list_active_cases()
        # 存放案例分割出的tokens
        self.doc_tokens = []
        # 计算tokens长度
        self.doc_lengths = []
        # 用来计算IDF的原料
        # 计算token出现在了几个案例中
        document_frequency = {}

        for case in self.cases:
            text = "\n".join([
                case.get("title") or "",
                case.get("message_pattern") or "",
                case.get("root_cause") or "",
                case.get("category") or "",
                case.get("exception_type") or "",
            ])
            tokens = tokenize(text)
            self.doc_tokens.append(tokens)
            self.doc_lengths.append(len(tokens))

            # 对tokens去重
            # 计算每个token出现在几个案例中
            for token in set(tokens):
                document_frequency[token] = document_frequency.get(token, 0) + 1

        # 用于IDF的原料
        # 案例的总数
        self.total_docs = len(self.cases)
        # 计算平均tokens长度
        # sum(self.doc_lengths)：所有tokens长度加起来
        # 如果 total_docs 不为 0 → 算平均值；否则 → 直接给 0.0
        self.avg_doc_length = (
            sum(self.doc_lengths) / self.total_docs if self.total_docs else 0.0
        )

        # BM25 的 IDF：词越稀有，权重越高
        self.idf = {}
        for token, df in document_frequency.items():
            self.idf[token] = math.log(
                1 + (self.total_docs - df + 0.5) / (df + 0.5)
            )

    def _score(self, query_tokens, doc_index):
        tokens = self.doc_tokens[doc_index]
        doc_length = self.doc_lengths[doc_index]
        score = 0.0

        for token in set(query_tokens):
            if token not in self.idf:
                continue

            tf = tokens.count(token)
            if tf == 0:
                continue


            # 计算BM25的分母
            denominator = tf + self.k1 * (
                1 - self.b + self.b * doc_length / self.avg_doc_length
            )
            # 最终BM25分数
            score += self.idf[token] * tf * (self.k1 + 1) / denominator

        return score

    def retrieve(self, query: str, top_k=5):
        query_tokens = tokenize(query)
        if not query_tokens or not self.cases:
            return []

        results = []
        for index, case in enumerate(self.cases):
            score = self._score(query_tokens, index)
            if score <= 0:
                continue

            results.append({
                "case_no": case["case_no"],
                "title": case.get("title"),
                "score": score,
                "message_pattern": case.get("message_pattern"),
                "root_cause": case.get("root_cause"),
                "fix_steps": case.get("fix_steps"),
                "verification": case.get("verification"),
            })

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]
