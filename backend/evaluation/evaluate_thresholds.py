import json

from pathlib import Path

from app.rag import answer_question


DATASET_PATH = Path(__file__).parent / "dataset.json"

THRESHOLDS = [
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.78,
]


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_threshold(threshold, dataset):

    results = []

    for item in dataset:

        question = item["question"]
        expected_answer = item["expected_answer"]
        expected_source = item["expected_source"]

        try:
            result = answer_question(
                question=question,
                match_threshold=threshold,
                match_count=5,
            )

            answer = result.get("answer", "")
            sources = result.get("sources", [])

            source_titles = [
                source.get("title")
                for source in sources
            ]

            answer_match = (
                expected_answer.lower()
                in answer.lower()
            )

            source_match = (
                expected_source in source_titles
                if expected_source
                else len(sources) == 0
            )

            results.append(
                {
                    "answer_match": answer_match,
                    "source_match": source_match,
                }
            )

        except Exception as e:

            print(f"ERROR: {question}")
            print(e)

            results.append(
                {
                    "answer_match": False,
                    "source_match": False,
                }
            )

    total = len(results)

    answer_accuracy = (
        sum(
            result["answer_match"]
            for result in results
        ) / total
        if total
        else 0
    )

    source_accuracy = (
        sum(
            result["source_match"]
            for result in results
        ) / total
        if total
        else 0
    )

    return answer_accuracy, source_accuracy


def main():

    dataset = load_dataset()

    print("=" * 70)
    print("THRESHOLD EVALUATION")
    print("=" * 70)

    print(
        f"{'Threshold':<12}"
        f"{'Answer Accuracy':<20}"
        f"{'Source Accuracy':<20}"
    )

    print("-" * 70)

    for threshold in THRESHOLDS:

        answer_accuracy, source_accuracy = (
            evaluate_threshold(
                threshold,
                dataset,
            )
        )

        print(
            f"{threshold:<12.2f}"
            f"{answer_accuracy * 100:<20.2f}%"
            f"{source_accuracy * 100:<20.2f}%"
        )


if __name__ == "__main__":
    main()