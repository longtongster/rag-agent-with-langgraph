"""Tests for the PDF ingestion pipeline."""

import hashlib
from unittest.mock import Mock

import pytest
from langchain_core.documents import Document

from rag_agent.ingest import pipeline


def test_load_pdf_returns_pages_with_stable_metadata(tmp_path, monkeypatch):
    """A valid PDF should return pages with provenance metadata."""
    pdf_content = b"fake PDF content used only for hashing"
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(pdf_content)

    pages = [
        Document(page_content="First page", metadata={"page": 0}),
        Document(page_content="Second page", metadata={"page": 1}),
    ]
    loader = Mock()
    loader.load.return_value = pages
    loader_class = Mock(return_value=loader)
    monkeypatch.setattr(pipeline, "PyPDFLoader", loader_class)

    result = pipeline.load_pdf(pdf_path)

    expected_hash = hashlib.sha256(pdf_content).hexdigest()
    loader_class.assert_called_once_with(pdf_path)
    assert result == pages
    assert [doc.metadata["page"] for doc in result] == [0, 1]
    assert all(doc.metadata["filename"] == "paper.pdf" for doc in result)
    assert all(doc.metadata["document_id"] == expected_hash for doc in result)
    assert all(doc.metadata["document_hash"] == expected_hash for doc in result)


def test_load_pdf_rejects_missing_file(tmp_path):
    """A missing source path should produce a descriptive error."""
    missing_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError, match="PDF file not found"):
        pipeline.load_pdf(missing_path)


def test_load_pdf_rejects_non_pdf_file(tmp_path):
    """An existing file without a PDF extension should be rejected."""
    text_path = tmp_path / "paper.txt"
    text_path.write_text("not a PDF", encoding="utf-8")

    with pytest.raises(ValueError, match="Expected a PDF file"):
        pipeline.load_pdf(text_path)


@pytest.mark.parametrize(
    "extracted_pages",
    [
        [],
        [Document(page_content="  \n", metadata={"page": 0})],
    ],
    ids=["no-pages", "blank-page"],
)
def test_load_pdf_rejects_unusable_extraction(
    tmp_path, monkeypatch, extracted_pages
):
    """An extraction with no substantive text should be rejected."""
    pdf_path = tmp_path / "scanned.pdf"
    pdf_path.write_bytes(b"fake PDF content")

    loader = Mock()
    loader.load.return_value = extracted_pages
    monkeypatch.setattr(pipeline, "PyPDFLoader", Mock(return_value=loader))

    with pytest.raises(ValueError, match="No usable text extracted"):
        pipeline.load_pdf(pdf_path)


def test_clean_document_safely_normalizes_text_without_mutating_input():
    """Safe cleaning should preserve paragraphs, metadata, and the input object."""
    original = Document(
        page_content="  First\tline\r\n\r\n\r\nSecond ﬁle\x00  ",
        metadata={"page": 1, "document_id": "paper-1"},
    )

    cleaned = pipeline.clean_document(original)

    assert cleaned is not original
    assert cleaned.metadata == original.metadata
    assert cleaned.metadata is not original.metadata
    assert original.page_content == "  First\tline\r\n\r\n\r\nSecond ﬁle\x00  "
    assert cleaned.page_content == "First line\n\nSecond file"


def test_clean_document_rejects_non_document_input():
    """Calling the cleaner with another type should fail clearly."""
    with pytest.raises(TypeError, match="Expected document to be a Document"):
        pipeline.clean_document("not a document")
