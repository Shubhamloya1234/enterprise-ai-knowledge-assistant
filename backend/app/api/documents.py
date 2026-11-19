import re
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException
)

from app.core.dependencies import require_role
from app.rag.ingestion import ingest_document
from app.rag.vector_store import delete_document, collection


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = Path("uploads").resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def validate_filename(filename: str) -> str:
    """
    Reject unsafe filenames and path traversal attempts.
    """

    if (
        not filename
        or Path(filename).name != filename
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._ -]{0,119}", filename)
        or filename in {".", ".."}
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    return filename


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(require_role("ADMIN"))
):
    filename = validate_filename(file.filename or "")
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )

    file_path = UPLOAD_DIR / filename

    # Prevent overwriting an existing uploaded file.
    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail="A document with this filename already exists."
        )

    # Also prevent duplicate ChromaDB entries when the original
    # uploaded file is no longer present on disk.
    existing = collection.get(
        where={"source": filename}
    )

    if existing.get("ids"):
        raise HTTPException(
            status_code=409,
            detail="A document with this filename is already indexed."
        )

    contents = bytearray()

    while True:
        chunk = await file.read(1024 * 1024)

        if not chunk:
            break

        contents.extend(chunk)

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Maximum document size is 10 MB."
            )

    file_created = False

    try:
        with file_path.open("xb") as buffer:
            file_created = True
            buffer.write(contents)

        result = ingest_document(str(file_path))

    except HTTPException:
        if file_created:
            file_path.unlink(missing_ok=True)
        raise

    except Exception as exc:
        if file_created:
            file_path.unlink(missing_ok=True)

        delete_document(filename)

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed."
        ) from exc

    return {
        "message": "Document uploaded and indexed successfully",
        "filename": filename,
        "chunks": result["chunks"]
    }


@router.delete("/{filename}")
def delete_uploaded_document(
    filename: str,
    current_user=Depends(require_role("ADMIN"))
):
    filename = validate_filename(filename)
    file_path = UPLOAD_DIR / filename

    deleted_chunks = delete_document(filename)

    if deleted_chunks == 0 and not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    if file_path.exists():
        file_path.unlink()

    return {
        "message": "Document deleted successfully",
        "filename": filename,
        "deleted_chunks": deleted_chunks
    }


@router.get("/")
def list_documents(
    current_user=Depends(require_role("ADMIN"))
):
    documents = set()

    for file_path in UPLOAD_DIR.iterdir():
        if (
            file_path.is_file()
            and file_path.suffix.lower() in ALLOWED_EXTENSIONS
        ):
            documents.add(file_path.name)

    return {
        "documents": sorted(documents),
        "count": len(documents)
    }
