import json
import sys
from pathlib import Path

import faiss
import numpy as np

# 让脚本在 ai/scripts 下运行时，也能 import ai/retrieval 下的模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from retrieval.case_repository import list_active_cases
from retrieval.embedding_client import embed_texts

# 索引目录：ai/retrieval/index
INDEX_DIR = Path(__file__).resolve().parents[1] / "retrieval" / "index"
INDEX_FILE = INDEX_DIR / "faiss.index"
CASE_IDS_FILE = INDEX_DIR / "case_ids.json"

def build_case_text(case : dict):

    return "\n".join([
        case.get("title", ""),
        case.get("message_pattern", ""),
        case.get("root_cause", ""),
        case.get("category", ""),
    ])

def build_faiss_index():
    cases = list_active_cases()
    if not cases:
        raise RuntimeError("没有 ACTIVE 案例")
    texts = [build_case_text(case) for case in cases]

    # 索引内部 ID 按加入顺序从 0 开始，所以这里保持同样的 cases 顺序
    # 检索出 ID 后，用 case_ids[ID] 就能拿回 case_no
    case_ids = [case["case_no"] for case in cases]
    vectors = embed_texts(texts)
    matrix = np.array(vectors, dtype=np.float32)
    # 原地 L2 归一化：每个向量除以自己的长度，长度变成 1
    faiss.normalize_L2(matrix)
    # 验证第一条向量长度是否接近 1.0
    print("first_vector_norm:", np.linalg.norm(matrix[0]))

    # matrix.shape 是 (案例数, 向量维度)，shape[1] 就是向量维度
    dimension = matrix.shape[1]
    # 创建精确内积索引；向量已归一化，所以内积等价于余弦相似度
    index = faiss.IndexFlatIP(dimension)
    # 把每一条案例向量加入索引，内部 ID 从 0 开始，顺序和 cases 一致
    index.add(matrix)

    print("cases:", len(cases))
    print("dimension:", dimension)
    # ntotal 表示索引里实际有多少条向量，应该等于 len(cases)
    print("index.ntotal:", index.ntotal)

    # 创建索引目录；parents=True 会创建多级目录，exist_ok=True 允许目录已存在
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    # 使用 FAISS 自己的方法保存二进制索引文件
    # 把index写入str(INDEX_FILE)位置文件
    faiss.write_index(index, str(INDEX_FILE))
    print("index_saved:", INDEX_FILE)

    # 保存 FAISS 内部 ID -> case_no 的映射；列表下标就是内部 ID
    # 写模式打开文件CASE_IDS_FILE，作为f使用
    # 然后把case_ids写入文件f以json格式
    with CASE_IDS_FILE.open("w", encoding="utf-8") as f:
        json.dump(case_ids, f, ensure_ascii=False, indent=2)
    print("case_ids_saved:", CASE_IDS_FILE)
    print("first_case_ids:", case_ids[:3])

    return index, cases


# 只有直接运行这个文件时才执行；被其他文件 import 时不会自动执行
if __name__ == "__main__":
    build_faiss_index()