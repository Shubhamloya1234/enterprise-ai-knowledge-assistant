
from pathlib import Path

import pytest

from app.rag.loader import load_pdf, load_txt, load_document


def test_load_txt_reads_utf8_content(tmp_path):
    file_path = tmp_path / "sample.txt"
    expected = "Company leave policy: employees receive 20 days of leave."
    file_path.write_text(expected, encoding="utf-8")

    assert load_txt(str(file_path)) == expected


def test_load_txt_supports_unicode(tmp_path):
    file_path = tmp_path / "unicode.txt"
    expected = "Employee policy — नमस्ते"
    file_path.write_text(expected, encoding="utf-8")

    assert load_txt(str(file_path)) == expected


def test_load_txt_missing_file_raises_error(tmp_path):
    file_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        load_txt(str(file_path))


def test_load_pdf_missing_file_raises_error(tmp_path):
    file_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        load_pdf(str(file_path))


def test_load_document_accepts_txt_extension_case_insensitively(tmp_path):
    file_path = tmp_path / "sample.TXT"
    expected = "Testing document loading."
    file_path.write_text(expected, encoding="utf-8")

    assert load_document(str(file_path)) == expected


def test_load_document_rejects_unsupported_extension(tmp_path):
    file_path = tmp_path / "sample.docx"
    file_path.write_text("test", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file type"):
        load_document(str(file_path))


def test_load_pdf_extracts_text(tmp_path):
    # Create a small, valid PDF using pypdf's PDF writer.
    from pypdf import PdfWriter

    file_path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    with file_path.open("wb") as pdf_file:
        writer.write(pdf_file)

    # A blank PDF is valid, but has no extractable text.
    assert load_pdf(str(file_path)) == ""
