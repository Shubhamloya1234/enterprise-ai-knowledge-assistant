from pathlib import Path
from pypdf import PdfReader # type: ignore


def load_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def load_txt(file_path: str) -> str:
    """
    Read text from a TXT file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    return path.read_text(
        encoding="utf-8"
    )


def load_document(file_path: str) -> str:
    """
    Load a PDF or TXT document automatically
    based on its file extension.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path)

    elif extension == ".txt":
        return load_txt(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )