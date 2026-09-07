import json
from pathlib import Path


BASE_DIR = Path(__file__).parent

RESULTS_PATH = BASE_DIR / "results.json"
JUDGE_RESULTS_PATH = BASE_DIR / "judge_results.json"
OUTPUT_PATH = BASE_DIR / "final_report.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():

    baseline = load_json(RESULTS_PATH)
    judge = load_json(JUDGE_RESULTS_PATH)

    baseline_results = baseline.get("results", [])
    judge_results = judge.get("results", [])

    judge_by_id = {
        result["id"]: result
        for result in judge_results
    }

    questions = []

    for result in baseline_results:

        judge_result = judge_by_id.get(
            result["id"]
        )

        questions.append(
            {
                "id": result["id"],
                "question": result["question"],
                "answer_accuracy": result.get(
                    "answer_correct"
                ),
                "source_accuracy": result.get(
                    "source_correct"
                ),
                "retrieval_status": result.get(
                    "retrieval_status"
                ),
                "best_similarity": result.get(
                    "best_similarity"
                ),
                "chunks_retrieved": result.get(
                    "chunks_retrieved"
                ),
                "latency_seconds": result.get(
                    "latency_seconds"
                ),
                "judge_correct": (
                    judge_result.get(
                        "judge_correct"
                    )
                    if judge_result
                    else None
                ),
                "judge_score": (
                    judge_result.get(
                        "judge_score"
                    )
                    if judge_result
                    else None
                ),
                "grounded": (
                    judge_result.get(
                        "judge_correct"
                    )
                    and result.get(
                        "source_correct"
                    )
                    if judge_result
                    else None
                ),
            }
        )

    final_report = {
        "project": (
            "AI Internal Knowledge Base"
        ),
        "evaluation_summary": {
            "total_questions": baseline.get(
                "total_questions"
            ),
            "successful_rag_questions": baseline.get(
                "successful_rag_questions"
            ),
            "failed_rag_questions": baseline.get(
                "failed_rag_questions"
            ),
            "successful_judge_questions": judge.get(
                "successful_judge_questions"
            ),
            "failed_judge_questions": judge.get(
                "failed_judge_questions"
            ),
        },
        "rag_metrics": {
            "answer_accuracy": baseline.get(
                "answer_accuracy"
            ),
            "source_accuracy": baseline.get(
                "source_accuracy"
            ),
            "average_best_similarity": baseline.get(
                "average_best_similarity"
            ),
            "average_latency_seconds": baseline.get(
                "average_latency_seconds"
            ),
        },
        "judge_metrics": {
            "judge_accuracy": judge.get(
                "judge_accuracy"
            ),
            "average_judge_score": judge.get(
                "average_judge_score"
            ),
            "groundedness": judge.get(
                "groundedness"
            ),
        },
        "questions": questions,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            final_report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        "=== FINAL EVALUATION REPORT ==="
    )

    print(
        f"Total questions: "
        f"{final_report['evaluation_summary']['total_questions']}"
    )

    print(
        f"RAG success: "
        f"{final_report['evaluation_summary']['successful_rag_questions']}/"
        f"{final_report['evaluation_summary']['total_questions']}"
    )

    print(
        f"Answer accuracy: "
        f"{final_report['rag_metrics']['answer_accuracy']}%"
    )

    print(
        f"Source accuracy: "
        f"{final_report['rag_metrics']['source_accuracy']}%"
    )

    print(
        f"Average similarity: "
        f"{final_report['rag_metrics']['average_best_similarity']}"
    )

    print(
        f"Average latency: "
        f"{final_report['rag_metrics']['average_latency_seconds']}s"
    )

    print(
        f"Judge accuracy: "
        f"{final_report['judge_metrics']['judge_accuracy']}%"
    )

    print(
        f"Average Judge score: "
        f"{final_report['judge_metrics']['average_judge_score']}"
    )

    print(
        f"Groundedness: "
        f"{final_report['judge_metrics']['groundedness']}%"
    )

    print()
    print(
        f"Saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()