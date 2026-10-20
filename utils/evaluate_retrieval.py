import json
import time
from datetime import datetime, timezone
from pathlib import Path

from backend.app_state import create_app_state
from utils.evaluation_metrics import evaluate_retrieval, aggregate_metrics

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
) 

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "utils" / "evaluation_dataset.json"
RESULTS_PATH = PROJECT_ROOT / "utils" / "evaluation_results.json"
RETRIEVAL_LIMIT = 30


def source_key(document_name, page_number):
    return (
        str(document_name).strip().casefold(),
        int(page_number),
    )


def unique_pages(chunks):
    pages = []
    seen = set()

    for chunk in chunks:
        key = source_key(chunk.document_name, chunk.page_number)

        if key not in seen:
            seen.add(key)
            pages.append(key)

    return pages


def main():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    state = create_app_state()
    results = []

    try:
        for case in dataset["cases"]:
            query = case["query"]

            relevant_pages = {
                source_key(
                    source["document_name"],
                    source["page_number"],
                )
                for source in case["relevant_sources"]
            }

            start = time.perf_counter()

            chunks = state.retriever.retrieve(
                query=query,
                top_k=RETRIEVAL_LIMIT,
            )

            retrieval_ms = (time.perf_counter() - start) * 1000
            retrieved_pages = unique_pages(chunks)

            metrics = evaluate_retrieval(
                retrieved=retrieved_pages,
                relevant=relevant_pages,
            )

            result = {
                "id": case["id"],
                "query": query,
                "category": case.get("category", "uncategorized"),
                "retrieval_latency_ms": round(retrieval_ms, 2),
                "relevant_pages": [
                    {
                        "document_name": name,
                        "page_number": page,
                    }
                    for name, page in sorted(relevant_pages)
                ],
                "retrieved_pages": [
                    {
                        "document_name": name,
                        "page_number": page,
                    }
                    for name, page in retrieved_pages
                ],
                "metrics": metrics,
            }

            results.append(result)

            print(
                f"{case['id']} | "
                f"Recall@5: {metrics['recall_at_5']:.3f} | "
                f"Recall@10: {metrics['recall_at_10']:.3f} | "
                f"MRR: {metrics['mrr']:.3f} | "
                f"nDCG@5: {metrics['ndcg_at_5']:.3f} | "
                f"Latency: {retrieval_ms:.2f} ms"
            )

    finally:
        state.qdrant.client.close()

    summary = aggregate_metrics(
        [result["metrics"] for result in results]
    )

    summary["average_retrieval_latency_ms"] = round(
        sum(result["retrieval_latency_ms"] for result in results)
        / len(results),
        2,
    ) if results else 0.0

    output = {
        "dataset_name": dataset.get("dataset_name"),
        "dataset_version": dataset.get("version"),
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(results),
        "retrieval_limit": RETRIEVAL_LIMIT,
        "summary": summary,
        "results": results,
    }

    with RESULTS_PATH.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print("\nAVERAGE METRICS")
    print(json.dumps(summary, indent=2))
    print(f"\nResults saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()