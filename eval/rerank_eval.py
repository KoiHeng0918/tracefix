import argparse
import sys
import time
from pathlib import Path

from langchain.chat_models import init_chat_model

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai"))
sys.path.insert(0, str(Path(__file__).parent))

from retrieval.reranker import rerank_candidates
from retrieval.vector_retriever import VectorRetriever
from run_eval import load_cases, rank_of


def metric_row(rows, key):
    total = len(rows) or 1
    ranks = [row[key] for row in rows]
    return {
        "recall5": sum(rank is not None for rank in ranks) / total,
        "hit1": sum(rank == 1 for rank in ranks) / total,
        "mrr": sum(1 / rank for rank in ranks if rank) / total,
    }


def print_metrics(rows):
    print("\nmetrics")
    print("split     cases  Recall@5  Hit@1   MRR")
    for split in ["dev", "test", "holdout", "all"]:
        subset = rows if split == "all" else [row for row in rows if row["split"] == split]
        if not subset:
            continue
        baseline = metric_row(subset, "baseline_rank")
        rerank = metric_row(subset, "rerank_rank")
        print(
            f"{split:9} {len(subset):5}  "
            f"{baseline['recall5']:.3f}    {baseline['hit1']:.3f}   {baseline['mrr']:.3f}  (baseline)"
        )
        print(
            f"{'':9} {'':5}  "
            f"{rerank['recall5']:.3f}    {rerank['hit1']:.3f}   {rerank['mrr']:.3f}  (rerank)"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "test", "holdout", "all"], default="dev")
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 条，用于 smoke test")
    args = parser.parse_args()

    cases = load_cases(args.split)
    if args.limit:
        cases = cases[: args.limit]
    if not cases:
        print("没有评测数据")
        return

    vector = VectorRetriever()
    model = init_chat_model(
        model="deepseek-chat",
        model_provider="deepseek",
        temperature=0,
    )

    rows = []
    for index, item in enumerate(cases, start=1):
        query = item["query"]
        expected = item["expectedCaseNo"]
        candidates = vector.retrieve(query, top_k=5)
        baseline_ids = [case["case_no"] for case in candidates]

        started = time.perf_counter()
        try:
            reranked, valid = rerank_candidates(model, query, candidates)
            error = ""
        except Exception as exc:
            reranked, valid = candidates, False
            error = f"{type(exc).__name__}: {exc}"
        latency_ms = (time.perf_counter() - started) * 1000

        rerank_ids = [case["case_no"] for case in reranked]
        row = {
            "split": item["split"],
            "query": query,
            "expected": expected,
            "baseline_rank": rank_of(expected, baseline_ids),
            "rerank_rank": rank_of(expected, rerank_ids),
            "valid": valid,
            "latency_ms": latency_ms,
            "error": error,
            "baseline_ids": baseline_ids,
            "rerank_ids": rerank_ids,
        }
        rows.append(row)
        print(
            f"[{index}/{len(cases)}] {item['split']} {expected} "
            f"baseline={row['baseline_rank']} rerank={row['rerank_rank']} "
            f"valid={valid} {latency_ms:.0f}ms"
        )
        if error:
            print("  error:", error)

    print_metrics(rows)
    invalid = sum(not row["valid"] for row in rows)
    avg_latency = sum(row["latency_ms"] for row in rows) / len(rows)
    print(f"\ninvalid_outputs: {invalid}/{len(rows)}")
    print(f"avg_rerank_latency_ms: {avg_latency:.0f}")

    changed = [
        row for row in rows
        if row["baseline_rank"] != row["rerank_rank"]
    ]
    if changed:
        print("\nrank_changes:")
        for row in changed:
            print(
                f"{row['split']} {row['expected']} "
                f"baseline={row['baseline_rank']} rerank={row['rerank_rank']}"
            )


if __name__ == "__main__":
    main()
