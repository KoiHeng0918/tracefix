import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai"))
from retrieval.vector_retriever import VectorRetriever
from parsers.stack_parser import extract_exception, extract_message
from retrieval.case_retriever import CaseRetriever

GOLDEN_DIR = Path(__file__).parent / "golden"


def load_cases(split: str):
    # 题库文件：eval/golden/cases.jsonl
    path = GOLDEN_DIR / "cases.jsonl"
    # 文件不存在就返回空列表
    if not path.exists():
        return []
    # 用来装筛选后的题目
    cases = []
    # with 会自动关闭文件
    with path.open("r", encoding="utf-8") as f:
        # 一行就是一条 JSON
        for line in f:
            # 去掉行尾换行和空格
            line = line.strip()
            # 空行跳过
            if not line:
                continue
            # JSON 字符串 -> Python 字典
            item = json.loads(line)
            # 关键筛选条件
            if split == "all" or item.get("split") == split:
                cases.append(item)

    return cases


def main():
    # 这个脚本支持哪些命令行选项
    parser = argparse.ArgumentParser()
    # --split          命令行选项名
    # choices          只允许这四个值
    # default          不传时默认用 test
    parser.add_argument("--suite", choices=["retrieval", "full"], default="retrieval")
    parser.add_argument("--split", choices=["dev", "test", "holdout", "all"], default="test")

    # 读取命令行，把结果放进一个对象
    args = parser.parse_args()

    cases = load_cases(args.split)
    print(f"suite={args.suite} split={args.split} cases={len(cases)}")
    if not cases:
        print("golden/cases.jsonl 为空：先准备真实评测用例，再跑指标。")
        return

    keyword_retriever = CaseRetriever()
    vector_retriever = VectorRetriever()
    keyword_hits = 0
    vector_hits = 0

    for item in cases:
        query = item["query"]
        expected_case_no = item["expectedCaseNo"]

        exception = extract_exception(query)
        message = extract_message(query)

        keyword_candidates = keyword_retriever.retrieve(
            exception,
            message,
            top_k=5,
        )

        vector_candidates = vector_retriever.retrieve(
            query,
            top_k=5,
        )

        keyword_ids = [case["case_no"] for case in keyword_candidates]
        vector_ids = [case["case_no"] for case in vector_candidates]

        if expected_case_no in vector_ids:
            # list.index 返回从 0 开始的下标，所以 +1 才是名次
            vector_rank = vector_ids.index(expected_case_no) + 1
        else:
            vector_rank = None

        print(
            f"query={query!r} "
            f"vector_rank={vector_rank} "
            f"vector_top5={vector_ids}"
        )

        keyword_hit = expected_case_no in keyword_ids
        vector_hit = expected_case_no in vector_ids

        if keyword_hit:
            keyword_hits += 1

        if vector_hit:
            vector_hits += 1




    print(f"cases={len(cases)} keyword_recall@5={keyword_hits / len(cases):.2f}")
    print(f"cases={len(cases)} vector_recall@5={vector_hits / len(cases):.2f}")


if __name__ == "__main__":
    main()
