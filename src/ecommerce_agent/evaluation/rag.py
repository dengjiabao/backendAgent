from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievalReport:
    recall_at_k: float
    mrr: float
    cases: int


def evaluate_retrieval(cases: list[dict[str, Any]], top_k: int = 5) -> RetrievalReport:
    if not cases:
        return RetrievalReport(0.0, 0.0, 0)
    recalls = []
    reciprocal_ranks = []
    for case in cases:
        expected = set(case.get("expected_ids", []))
        retrieved = list(case.get("retrieved_ids", []))[:top_k]
        recalls.append(1.0 if expected.intersection(retrieved) else 0.0)
        rank = next((index for index, item in enumerate(retrieved, 1) if item in expected), 0)
        reciprocal_ranks.append(1.0 / rank if rank else 0.0)
    return RetrievalReport(sum(recalls) / len(recalls), sum(reciprocal_ranks) / len(reciprocal_ranks), len(cases))
