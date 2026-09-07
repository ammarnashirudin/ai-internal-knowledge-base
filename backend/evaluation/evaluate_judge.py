import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).parent.parent)
)

from judge import judge_answer


RESULTS_PATH = (
    Path(__file__).parent / "results.json"
)

OUTPUT_PATH = (
    Path(__file__).parent / "judge_results.json"
)


def load_results():
    with open(
        RESULTS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():

    report = load_results()

    results = report.get(
        "results",
        [],
    )

    successful_rag = [
        result
        for result in results
        if result.get("rag_success") is True
    ]

    judge_results = []

    for result in successful_rag:

        print(
            f"Judging {result['id']}..."
        )

        try:

            judgment = judge_answer(
                question=result["question"],
                expected_answer=result["expected_answer"],
                actual_answer=result["answer"],
            )

            judge_correct = bool(
                judgment.get("correct", False)
            )

            judge_score = float(
                judgment.get("score", 0)
            )

            judge_reason = judgment.get(
                "reason",
                "",
            )

            judge_results.append(
                {
                    "id": result["id"],
                    "question": result["question"],
                    "expected_answer": result[
                        "expected_answer"
                    ],
                    "actual_answer": result[
                        "answer"
                    ],
                    "source_correct": result[
                        "source_correct"
                    ],
                    "judge_correct": judge_correct,
                    "judge_score": judge_score,
                    "judge_reason": judge_reason,
                    "judge_success": True,
                }
            )

        except Exception as error:

            judge_results.append(
                {
                    "id": result["id"],
                    "question": result["question"],
                    "expected_answer": result[
                        "expected_answer"
                    ],
                    "actual_answer": result[
                        "answer"
                    ],
                    "source_correct": result[
                        "source_correct"
                    ],
                    "judge_correct": False,
                    "judge_score": 0,
                    "judge_reason": "",
                    "judge_success": False,
                    "judge_error": str(error),
                }
            )

            print(
                f"JUDGE ERROR: {error}"
            )

    successful_judge = [
        result
        for result in judge_results
        if result.get("judge_success") is True
    ]

    if successful_judge:

        judge_accuracy = (
            sum(
                result["judge_correct"]
                for result in successful_judge
            )
            / len(successful_judge)
        )

        average_judge_score = (
            sum(
                result["judge_score"]
                for result in successful_judge
            )
            / len(successful_judge)
        )

        grounded_results = [
            result
            for result in successful_judge
            if (
                result["judge_correct"]
                and result["source_correct"]
            )
        ]

        groundedness = (
            len(grounded_results)
            / len(successful_judge)
        )

    else:

        judge_accuracy = 0
        average_judge_score = 0
        groundedness = 0

    judge_report = {

        "total_rag_questions":
            len(results),

        "successful_rag_questions":
            len(successful_rag),

        "successful_judge_questions":
            len(successful_judge),

        "failed_judge_questions":
            len(judge_results)
            - len(successful_judge),

        "judge_accuracy":
            round(
                judge_accuracy * 100,
                2,
            ),

        "average_judge_score":
            round(
                average_judge_score,
                3,
            ),

        "groundedness":
            round(
                groundedness * 100,
                2,
            ),

        "results":
            judge_results,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            judge_report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        "=== LLM JUDGE EVALUATION ==="
    )

    print(
        f"RAG questions: "
        f"{judge_report['total_rag_questions']}"
    )

    print(
        f"Successful Judge: "
        f"{judge_report['successful_judge_questions']}"
    )

    print(
        f"Failed Judge: "
        f"{judge_report['failed_judge_questions']}"
    )

    print(
        f"Judge accuracy: "
        f"{judge_report['judge_accuracy']}%"
    )

    print(
        f"Average Judge score: "
        f"{judge_report['average_judge_score']}"
    )

    print(
        f"Groundedness: "
        f"{judge_report['groundedness']}%"
    )


if __name__ == "__main__":
    main()