import json
import sys
from pathlib import Path

import faiss
import numpy as np

# 让脚本在 ai/scripts 下直接运行时，也能 import ai/retrieval 下的模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from retrieval.embedding_client import embed_texts

# 索引目录：ai/retrieval/index
INDEX_DIR = Path(__file__).resolve().parents[1] / "retrieval" / "index"
INDEX_FILE = INDEX_DIR / "faiss.index"
CASE_IDS_FILE = INDEX_DIR / "case_ids.json"


def search(query: str, top_k: int = 5):
    # faiss.read_index 的参数：
    # 1. 索引文件路径，必须是 str 类型，不能直接传 Path
    index = faiss.read_index(str(INDEX_FILE))

    # read_text 的参数：
    # encoding="utf-8" 保证读取中文内容时不乱码
    # json.loads 把 JSON 字符串转回 Python list
    case_ids = json.loads(CASE_IDS_FILE.read_text(encoding="utf-8"))

    # embed_texts 的参数：
    # 1. texts：list[str]，这里只传一条用户问题
    # 返回值：list[list[float]]，外层每个元素对应一条文本的向量
    query_vector = np.array(embed_texts([query]), dtype=np.float32)

    # faiss.normalize_L2 的参数：
    # 1. 二维 float32 矩阵，这里是 1 行 × 1024 列的查询向量
    # 作用：把向量长度归一化成 1，和建索引时的向量保持一致
    faiss.normalize_L2(query_vector)

    # index.search 的参数：
    # 1. query_vector：查询向量矩阵
    # 2. top_k：返回最相似的案例数量
    # 返回值 scores 和 ids 的形状都是 (1, top_k)
    # scores[0] 是第一条查询的分数，ids[0] 是对应的 FAISS 内部 ID
    scores, ids = index.search(query_vector, top_k)

    for score, internal_id in zip(scores[0], ids[0]):
        # int(...) 转成普通 Python 整数，因为列表下标必须是 int
        # case_ids[internal_id] 就是 FAISS ID -> case_no 的映射
        case_no = case_ids[int(internal_id)]
        print(f"score={score:.4f} id={int(internal_id)} case_no={case_no}")


if __name__ == "__main__":
    # sys.argv[1] 是命令行传入的第一个参数
    # 没有传参数时，使用默认问题，方便直接运行
    query = sys.argv[1] if len(sys.argv) > 1 else "数据库连接被拒绝，不知道是不是配置错了"
    search(query, top_k=5)
