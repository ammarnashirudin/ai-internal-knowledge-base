import json
import time
from pathlib import Path

import requests


API_URL = "http://127.0.0.1:8000/ask"

DATASET_PATH = (
    Path(__file__).parent / "dataset.json"
)

OUTPUT_PATH = (
    Path(__file__).parent / "results.json"
)


def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def normalize(text: str) -> str:
    return (
        text
        .lower()
        .strip()
        .replace(".", "")
        .replace(",", "")
    )


def answer_contains_expected(
    answer: str,
    expected: str,
) -> bool:

    if expected.lower() == "not found":
        not_found_phrases = [
            "not found",
            "not available",
            "does not contain",
            "not in the knowledge base",
            "information not found",
            "tidak ditemukan",
            "tidak tersedia",
        ]

        answer_normalized = normalize(answer)

        return any(
            phrase in answer_normalized
            for phrase in not_found_phrases
        )

    return (
        normalize(expected)
        in normalize(answer)
    )


def source_matches(
    sources: list,
    expected_source: str | None,
) -> bool:

    if expected_source is None:
        return len(sources) == 0

    for source in sources:
        title = (
            source
            .get("title", "")
            .lower()
        )

        if expected_source.lower() in title:
            return True

    return False


def evaluate_question(item):

    start = time.perf_counter()

    response = requests.post(
        API_URL,
        json={
            "question": item["question"],
            "match_count": 5,
            "match_threshold": 0.70,
        },
        timeout=90,
    )

    latency = (
        time.perf_counter()
        - start
    )

    response.raise_for_status()

    result = response.json()

    answer = result.get(
        "answer",
        "",
    )

    sources = result.get(
        "sources",
        [],
    )

    retrieval = result.get(
        "retrieval",
        {},
    )

    answer_correct = (
        answer_contains_expected(
            answer,
            item["expected_answer"],
        )
    )

    source_correct = (
        source_matches(
            sources,
            item["expected_source"],
        )
    )

    return {
        "id": item["id"],
        "question": item["question"],
        "expected_answer": item["expected_answer"],
        "expected_source": item["expected_source"],
        "answer": answer,
        "answer_correct": answer_correct,
        "source_correct": source_correct,
        "retrieval_status": retrieval.get(
            "status"
        ),
        "best_similarity": retrieval.get(
            "best_similarity"
        ),
        "chunks_retrieved": retrieval.get(
            "chunks_retrieved"
        ),
        "latency_seconds": round(
            latency,
            3,
        ),
        "rag_success": True,
    }


def main():

    dataset = load_dataset()

    results = []

    for item in dataset:

        print(
            f"Evaluating {item['id']}..."
        )

        try:

            result = evaluate_question(
                item
            )

            results.append(result)

        except Exception as error:

            results.append(
                {
                    "id": item["id"],
                    "question": item["question"],
                    "rag_success": False,
                    "error": str(error),
                }
            )

            print(
                f"RAG ERROR: {error}"
            )

    # ======================================
    # Successful RAG requests
    # ======================================

    successful = [
        result
        for result in results
        if result.get("rag_success") is True
    ]

    # ======================================
    # Metrics
    # ======================================

    if successful:

        answer_accuracy = (
            sum(
                r["answer_correct"]
                for r in successful
            )
            / len(successful)
        )

        source_accuracy = (
            sum(
                r["source_correct"]
                for r in successful
            )
            / len(successful)
        )

        avg_latency = (
            sum(
                r["latency_seconds"]
                for r in successful
            )
            / len(successful)
        )

        similarities = [
            r["best_similarity"]
            for r in successful
            if r["best_similarity"]
            is not None
        ]

        avg_similarity = (
            sum(similarities)
            / len(similarities)
            if similarities
            else 0
        )

    else:

        answer_accuracy = 0
        source_accuracy = 0
        avg_latency = 0
        avg_similarity = 0

    # ======================================
    # Report
    # ======================================

    report = {

        "total_questions":
            len(dataset),

        "successful_rag_questions":
            len(successful),

        "failed_rag_questions":
            len(dataset) - len(successful),

        "answer_accuracy":
            round(
                answer_accuracy * 100,
                2,
            ),

        "source_accuracy":
            round(
                source_accuracy * 100,
                2,
            ),

        "average_latency_seconds":
            round(
                avg_latency,
                3,
            ),

        "average_best_similarity":
            round(
                avg_similarity,
                4,
            ),

        "results":
            results,
    }

    # ======================================
    # Save results
    # ======================================

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # ======================================
    # Terminal report
    # ======================================

    print()
    print(
        "=== RAG BASELINE EVALUATION ==="
    )

    print(
        f"Questions: "
        f"{report['total_questions']}"
    )

    print(
        f"Successful RAG: "
        f"{report['successful_rag_questions']}"
    )

    print(
        f"Failed RAG: "
        f"{report['failed_rag_questions']}"
    )

    print(
        f"Answer accuracy: "
        f"{report['answer_accuracy']}%"
    )

    print(
        f"Source accuracy: "
        f"{report['source_accuracy']}%"
    )

    print(
        f"Average best similarity: "
        f"{report['average_best_similarity']}"
    )

    print(
        f"Average latency: "
        f"{report['average_latency_seconds']}s"
    )


if __name__ == "__main__":
    main()