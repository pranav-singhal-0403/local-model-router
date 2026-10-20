import math


def recall_at_k(retrieved, relevant, k):
    relevant = set(relevant)

    if not relevant:
        return 0.0

    retrieved_at_k = set(retrieved[:k])

    return len(retrieved_at_k & relevant) / len(relevant)


def reciprocal_rank(retrieved, relevant):
    relevant = set(relevant)

    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank

    return 0.0


def dcg_at_k(retrieved, relevant, k):
    relevant = set(relevant)
    score = 0.0

    for rank, item in enumerate(retrieved[:k], start=1):
        if item in relevant:
            score += 1.0 / math.log2(rank + 1)

    return score


def ndcg_at_k(retrieved, relevant, k):
    relevant = set(relevant)

    if not relevant:
        return 0.0

    ideal_count = min(len(relevant), k)
    ideal_dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, ideal_count + 1)
    )

    if ideal_dcg == 0:
        return 0.0

    return dcg_at_k(retrieved, relevant, k) / ideal_dcg


def evaluate_retrieval(retrieved, relevant):
    return {
        "recall_at_5": recall_at_k(retrieved, relevant, 5),
        "recall_at_10": recall_at_k(retrieved, relevant, 10),
        "mrr": reciprocal_rank(retrieved, relevant),
        "ndcg_at_5": ndcg_at_k(retrieved, relevant, 5),
    }


def aggregate_metrics(results):
    if not results:
        return {}

    metric_names = results[0].keys()

    return {
        metric: sum(row[metric] for row in results) / len(results)
        for metric in metric_names
    }