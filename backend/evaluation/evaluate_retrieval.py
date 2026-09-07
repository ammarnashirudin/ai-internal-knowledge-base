import json

from pathlib import Path

from app.embeddings import embeddings
from app.retrieval import similarity_search


DATASET_PATH = Path(__file__).parent / "dataset.json"


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate():

    dataset = load_dataset()

    results = []

    print("=" * 70)
    print("RETRIEVAL EVALUATION")
    print("=" * 70)

    for item in dataset:

        question = item["question"]
        expected_source = item["expected_source"]

        print("\n" + "=" * 70)
        print(f"Question: {question}")

        try:

            query_embedding = embeddings.embed_query(
                question
            )

            chunks = similarity_search(
                query_embedding=query_embedding,
                match_threshold=0.0,
                match_count=5,
                department="Finance",
            )

            source_titles = [
                chunk.get("metadata", {}).get("title")
                for chunk in chunks
            ]

            similarities = [
                chunk["similarity"]
                for chunk in chunks
            ]

            best_similarity = (
                max(similarities)
                if similarities
                else 0
            )

            # --------------------------------
            # SOURCE RETRIEVAL
            # --------------------------------

            if expected_source is not None:

                source_found = (
                    expected_source
                    in source_titles
                )

            else:

                # Untuk Not Found, kita tidak
                # mengharapkan source tertentu.
                source_found = True

            # --------------------------------
            # RANK
            # --------------------------------

            source_rank = None

            if expected_source is not None:

                for index, title in enumerate(
                    source_titles,
                    start=1,
                ):
                    if title == expected_source:
                        source_rank = index
                        break

            # --------------------------------
            # RESULT
            # --------------------------------

            results.append(
                {
                    "question": question,
                    "expected_source": expected_source,
                    "source_found": source_found,
                    "source_rank": source_rank,
                    "best_similarity": best_similarity,
                    "chunks_retrieved": len(chunks),
                }
            )

            print(
                f"Expected source : "
                f"{expected_source}"
            )

            print(
                f"Retrieved sources: "
                f"{source_titles}"
            )

            print(
                f"Best similarity  : "
                f"{best_similarity:.4f}"
            )

            print(
                f"Chunks retrieved : "
                f"{len(chunks)}"
            )

            print(
                f"Source found     : "
                f"{source_found}"
            )

            print(
                f"Source rank      : "
                f"{source_rank}"
            )

        except Exception as e:

            print(f"ERROR: {e}")

            results.append(
                {
                    "question": question,
                    "expected_source": expected_source,
                    "source_found": False,
                    "source_rank": None,
                    "best_similarity": 0,
                    "chunks_retrieved": 0,
                    "error": str(e),
                }
            )

    # ==========================================
    # METRICS
    # ==========================================

    total = len(results)

    source_retrieval_accuracy = (
        sum(
            result["source_found"]
            for result in results
            if result["expected_source"] is not None
        )
        / sum(
            1
            for result in results
            if result["expected_source"] is not None
        )
        if any(
            result["expected_source"] is not None
            for result in results
        )
        else 0
    )

    ranked_results = [
        result
        for result in results
        if result["source_rank"] is not None
    ]

    top_1_accuracy = (
        sum(
            result["source_rank"] == 1
            for result in ranked_results
        )
        / len(ranked_results)
        if ranked_results
        else 0
    )

    average_similarity = (
        sum(
            result["best_similarity"]
            for result in results
        )
        / total
        if total
        else 0
    )

    print("\n" + "=" * 70)
    print("RETRIEVAL EVALUATION RESULT")
    print("=" * 70)

    print(
        f"Total questions           : "
        f"{total}"
    )

    print(
        f"Source retrieval accuracy : "
        f"{source_retrieval_accuracy * 100:.2f}%"
    )

    print(
        f"Top-1 source accuracy     : "
        f"{top_1_accuracy * 100:.2f}%"
    )

    print(
        f"Average best similarity   : "
        f"{average_similarity:.4f}"
    )


if __name__ == "__main__":
    evaluate()