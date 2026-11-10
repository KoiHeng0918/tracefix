import json
import sys
from pathlib import Path
# 让程序在直接运行时，也能 import ai/*的模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import faiss
import numpy as np
from retrieval.case_repository import list_active_cases
from retrieval.embedding_client import embed_texts

# 索引目录：ai/retrieval/index
INDEX_DIR = Path(__file__).resolve().parents[1] / "retrieval" / "index"
INDEX_FILE = INDEX_DIR / "faiss.index"
CASE_IDS_FILE = INDEX_DIR / "case_ids.json"
class VectorRetriever:
    def __init__(self):
        # 只在这里读一次

        # 读建立faiss_index时维护的文件，faiss.write_index(index, str(INDEX_FILE))
        # 由于写入时维护的是二进制索引文件，因此使用read_index
        self.index = faiss.read_index(str(INDEX_FILE))

        # 读建立faiss_index时维护的文件
        # with CASE_IDS_FILE.open("w", encoding="utf-8") as f:
        # json.dump(case_ids, f, ensure_ascii=False, indent=2)
        # 使用对可读文件读的read_text，写回为json
        self.case_ids = json.loads(
            CASE_IDS_FILE.read_text(encoding="utf-8")
        )

        # 读取Mysql中的数据
        self.cases = list_active_cases()
        # [
        #     {"case_no": "ERR-A", "title": "案例 A"},
        #     {"case_no": "ERR-B", "title": "案例 B"},
        # ]


        #将案例集变为方便根据case_no读取的结构
        self.case_by_no = {}
        # {
        #     "ERR-A": {"case_no": "ERR-A", "title": "案例 A"},
        #     "ERR-B": {"case_no": "ERR-B", "title": "案例 B"},
        # }

        for case in self.cases:
            key = case["case_no"]
            value = case
            self.case_by_no[key] = value

    def retrieve(self,query: str, top_k: int = 5):
       
        top_k = min(top_k, self.index.ntotal)
        # 将用户query转为向量
        vectors = embed_texts([query])

        # 将向量转为faiss可读的矩阵
        matrix = np.array(vectors, dtype=np.float32)

        # L2归一化矩阵
        faiss.normalize_L2(matrix)

        # 查 TopK，结果是score二维数组和id二维数组
        # 只不过search方法查询的这个二维数组里分别只有一个score列表和id列表

        scores, ids = self.index.search(matrix, top_k)



        results = []
        # 用 case_ids[id] 映射成 case_no，然后与score组成结果字典放入列表
        # zip(scores[0], ids[0])把scores[0], ids[0]两个列表内容按顺序对应
        for score, internal_id in zip(scores[0], ids[0]):
            # int(...) 转成普通 Python 整数，因为列表下标必须是 int
            # case_ids[internal_id] 就是 FAISS ID -> case_no 的映射
            case_no = self.case_ids[int(internal_id)]
            case = self.case_by_no.get(case_no, {})

            results.append({
                "case_no": case_no,
                "title": case.get("title"),
                # 向量分数是 0~1，现有图按 0~10 设计，所以乘 10 统一尺度
                "score": float(score) * 10,
                "message_pattern": case.get("message_pattern"),
                "root_cause": case.get("root_cause"),
                "fix_steps": case.get("fix_steps"),
                "verification": case.get("verification"),
            })

        return results
