from sentence_transformers import SentenceTransformer # type: ignore


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def generate_embeddings(texts: list[str]):
    """
    Convert text chunks into numerical vectors.
    """

    if not texts:
        return []

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )

    return embeddings.tolist()