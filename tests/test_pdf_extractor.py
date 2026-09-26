"""PDF extraction tests using temporary, generated documents."""

import pymupdf
import pytest

from src.pdf_extractor import extract_text_from_pdf


@pytest.mark.parametrize(
    "page_texts, expected",
    [
        (["Rechnung 123"], "Rechnung 123\n"),
        (["First page", "Second page"], "First page\nSecond page\n"),
        (["", ""], ""),
        (["First page", "", "Last page"], "First page\nLast page\n"),
    ],
)
def test_extracts_all_pages_in_order(tmp_path, page_texts, expected):
    path = tmp_path / "invoice.pdf"
    with pymupdf.open() as document:
        for text in page_texts:
            page = document.new_page()
            if text:
                page.insert_text((72, 72), text)
        document.save(str(path))

    assert extract_text_from_pdf(str(path)) == expected


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="PDF file does not exist"):
        extract_text_from_pdf(str(tmp_path / "missing.pdf"))


def test_directory(tmp_path):
    with pytest.raises(IsADirectoryError, match="Expected a PDF file"):
        extract_text_from_pdf(str(tmp_path))


@pytest.mark.parametrize("content", [b"", b"This is not a PDF", b"%PDF-1.7\ninvalid"])
def test_invalid_pdf(tmp_path, content):
    path = tmp_path / "invalid.pdf"
    path.write_bytes(content)

    with pytest.raises(ValueError, match="Invalid or empty PDF file"):
        extract_text_from_pdf(str(path))


def test_non_pdf_document(tmp_path):
    path = tmp_path / "document.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
        '<rect width="100" height="100" fill="red"/></svg>'
    )

    with pytest.raises(ValueError, match="File is not a PDF"):
        extract_text_from_pdf(str(path))


def test_password_protected_pdf(tmp_path):
    path = tmp_path / "protected.pdf"
    with pymupdf.open() as document:
        document.new_page()
        document.save(
            str(path),
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
            owner_pw="owner-password",
            user_pw="user-password",
        )

    with pytest.raises(ValueError, match="PDF requires a password"):
        extract_text_from_pdf(str(path))
