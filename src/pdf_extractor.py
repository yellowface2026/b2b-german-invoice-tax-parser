"""Extract existing text from PDF documents using PyMuPDF."""

from pathlib import Path

import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:
    """Return all page text in document order, or an empty string if none.

    Raises:
        FileNotFoundError: If the path does not exist.
        IsADirectoryError: If the path is a directory.
        ValueError: If the file is invalid, is not a PDF, or requires a password.

    A blank PDF returns an empty string; a zero-byte file is invalid.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file does not exist: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Expected a PDF file, but found a directory: {path}")

    try:
        with pymupdf.open(str(path)) as document:
            if not document.is_pdf:
                raise ValueError(f"File is not a PDF: {path}")
            if document.needs_pass:
                raise ValueError(f"PDF requires a password: {path}")
            return "".join(page.get_text() for page in document)
    except pymupdf.FileDataError as exc:
        raise ValueError(f"Invalid or empty PDF file: {path}") from exc
