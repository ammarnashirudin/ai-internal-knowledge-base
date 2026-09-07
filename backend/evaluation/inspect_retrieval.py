import json

from pathlib import Path

from app.embeddings import embeddings
from app.retrieval import similarity_search


DATASET_PATH = Path(__file__).parent / "dataset.json"


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def main():

    dataset = load_dataset()

    print("=" * 70)
    print("RETRIEVAL INSPECTION")
    print("=" * 70)

    for item in dataset:

        question = item["question"]

        print("\n" + "=" * 70)
        print(f"Question: {question}")

        query_embedding = embeddings.embed_query(question)

        chunks = similarity_search(
            query_embedding=query_embedding,
            match_threshold=0.0,
            match_count=5,
            department="Finance", 
        )

        if not chunks:
            print("No chunks retrieved.")
            continue

        for index, chunk in enumerate(chunks, start=1):

            metadata = chunk.get("metadata", {})

            print(f"\nRank: {index}")
            print(
                f"Similarity: "
                f"{chunk['similarity']:.4f}"
            )
            print(
                f"Title: "
                f"{metadata.get('title')}"
            )
            print(
                f"Department: "
                f"{metadata.get('department')}"
            )
            print(
                f"Category: "
                f"{metadata.get('category')}"
            )
            print(
                f"Content: "
                f"{chunk['content'][:300]}"
            )


if __name__ == "__main__":
    main()