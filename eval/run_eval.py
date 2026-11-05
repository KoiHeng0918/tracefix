"""
TraceFix 评测脚本骨架。

P1/P2 真正要做的事：
1. 读取 eval/golden/cases.jsonl
2. 调 /diagnosis/analyze 或直接调 Python 诊断函数
3. 计算 Recall@5、MRR、根因准确率、引用正确率、abstain 准确率
4. 输出 JSON/Markdown 报告
5. CI 对比基线，回归就失败

现在只是骨架，不插入数据，也不调用模型。
"""

import argparse
import json
from pathlib import Path

GOLDEN_DIR = Path(__file__).parent / "golden"


def load_cases(split: str):
    path = GOLDEN_DIR / "cases.jsonl"
    if not path.exists():
        return []
    cases = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if split == "all" or item.get("split") == split:
                cases.append(item)
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=["retrieval", "full"], default="retrieval")
    parser.add_argument("--split", choices=["dev", "test", "holdout", "all"], default="test")
    args = parser.parse_args()

    cases = load_cases(args.split)
    print(f"suite={args.suite} split={args.split} cases={len(cases)}")
    if not cases:
        print("golden/cases.jsonl 为空：先准备真实评测用例，再跑指标。")
        return

    # TODO: 调诊断服务，计算真实指标。
    print("骨架阶段：尚未调用诊断服务，指标未计算。")


if __name__ == "__main__":
    main()
