from pathlib import Path

from app.rag.ingestion import ingest_document


SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def ingest_folder(folder_path: str):
    """
    Ingest all supported documents from a folder.
    """

    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(
            f"Folder not found: {folder_path}"
        )

    results = []

    for file_path in folder.iterdir():

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        result = ingest_document(
            str(file_path)
        )

        results.append(result)

    return results