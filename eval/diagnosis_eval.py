import argparse
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai"))
sys.path.insert(0, str(Path(__file__).parent))

from graph.diagnosis_graph import build_graph
from parsers.stack_parser import (
    extract_exception,
    extract_message,
    fingerprint as build_fingerprint,
)
from run_eval import load_cases


def p95(values):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * 0.95) - 1)
    return ordered[index]


def summarize(rows):
    if not rows:
        return {}
    total = len(rows)
    latencies = [row["latency_ms"] for row in rows]
    return {
        "cases": total,
        "diagnosed": sum(row["status"] == "DIAGNOSED" for row in rows) / total,
        "citation_hit": sum(row["citation_hit"] for row in rows) / total,
        "fields_complete": sum(row["fields_complete"] for row in rows) / total,
        "helpful": sum(row["helpful"] for row in rows) / total,
        "strict_success": sum(row["strict_success"] for row in rows) / total,
        "avg_latency_ms": sum(latencies) / total,
        "p95_latency_ms": p95(latencies),
        "errors": sum(bool(row["error"]) for row in rows),
    }


def print_summary(rows):
    print("\nsummary")
    print(
        "split     cases  DIAGNOSED  citation_hit  fields_ok  helpful  strict  "
        "avg_ms  p95_ms  errors"
    )
    for split in ["dev", "test", "holdout", "all"]:
        subset = rows if split == "all" else [row for row in rows if row["split"] == split]
        if not subset:
            continue
        stats = summarize(subset)
        print(
            f"{split:9} {stats['cases']:5}  "
            f"{stats['diagnosed']:.3f}      "
            f"{stats['citation_hit']:.3f}        "
            f"{stats['fields_complete']:.3f}     "
            f"{stats['helpful']:.3f}    "
            f"{stats['strict_success']:.3f}   "
            f"{stats['avg_latency_ms']:.0f}   "
            f"{stats['p95_latency_ms']:.0f}    "
            f"{stats['errors']}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "test", "holdout", "all"], default="dev")
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 条，用于 smoke test")
    parser.add_argument("--output", default="", help="可选的 JSON 结果输出路径")
    args = parser.parse_args()

    cases = load_cases(args.split)
    if args.limit:
        cases = cases[: args.limit]
    if not cases:
        print("没有评测数据")
        return

    graph = build_graph()
    rows = []

    for index, item in enumerate(cases, start=1):
        query = item["query"]
        expected = item["expectedCaseNo"]
        started = time.perf_counter()
        try:
            state = {
                "trace": query,
                "context": None,
                "exception": extract_exception(query),
                "message": extract_message(query),
                "fingerprint": build_fingerprint(
                    extract_exception(query),
                    extract_message(query),
                    "",
                ),
            }
            result = graph.invoke(state)
            elapsed_ms = (time.perf_counter() - started) * 1000
            diagnosis = result.get("diagnosis") or {}
            matched = result.get("matched_case_ids") or []
            fields_complete = all(
                bool(str(diagnosis.get(field) or "").strip())
                for field in ["rootCause", "fixSteps", "verification"]
            )
            row = {
                "split": item["split"],
                "query": query,
                "expected": expected,
                "status": result.get("status") or "UNKNOWN",
                "retrieval_source": result.get("retrieval_source") or "",
                "matched_case_ids": matched,
                "citation_hit": expected in matched,
                "fields_complete": fields_complete,
                "helpful": expected in matched and fields_complete,
                "strict_success": (
                    result.get("status") == "DIAGNOSED"
                    and expected in matched
                    and fields_complete
                ),
                "missing_info": result.get("missing_info") or [],
                "latency_ms": elapsed_ms,
                "error": "",
            }
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000
            row = {
                "split": item["split"],
                "query": query,
                "expected": expected,
                "status": "ERROR",
                "retrieval_source": "",
                "matched_case_ids": [],
                "citation_hit": False,
                "fields_complete": False,
                "helpful": False,
                "strict_success": False,
                "missing_info": [],
                "latency_ms": elapsed_ms,
                "error": f"{type(exc).__name__}: {exc}",
            }

        rows.append(row)
        print(
            f"[{index}/{len(cases)}] {row['split']} {expected} "
            f"status={row['status']} citation={row['citation_hit']} "
            f"fields={row['fields_complete']} helpful={row['helpful']} "
            f"strict={row['strict_success']} {row['latency_ms']:.0f}ms"
        )
        if row["error"]:
            print("  error:", row["error"])
        elif not row["helpful"]:
            print("  missing_info:", row["missing_info"])

    print_summary(rows)

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(
                {
                    "rows": rows,
                    "summary": summarize(rows),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print("output:", output)


if __name__ == "__main__":
    main()
