"""Tests for the PDF ingestion pipeline."""

import hashlib
import json
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


def test_add_chunk_metadata_adds_stable_ids_without_mutating_inputs():
    """Chunk metadata should be deterministic and indexed per document."""
    chunks = [
        Document(page_content="Alpha", metadata={"document_id": "paper-a"}),
        Document(page_content="Beta", metadata={"document_id": "paper-a"}),
        Document(page_content="Gamma", metadata={"document_id": "paper-b"}),
    ]

    first_result = pipeline.add_chunk_metadata(chunks)
    second_result = pipeline.add_chunk_metadata(chunks)

    assert [chunk.metadata["chunk_index"] for chunk in first_result] == [0, 1, 0]
    assert [chunk.metadata["chunk_id"] for chunk in first_result] == [
        chunk.metadata["chunk_id"] for chunk in second_result
    ]
    assert first_result[0].metadata["chunk_text_hash"] == hashlib.sha256(
        b"Alpha"
    ).hexdigest()
    assert len({chunk.metadata["chunk_id"] for chunk in first_result}) == 3
    assert all("chunk_id" not in chunk.metadata for chunk in chunks)
    assert all(result is not original for result, original in zip(first_result, chunks))


def test_add_chunk_metadata_requires_document_id():
    """A chunk without document provenance cannot receive a stable ID."""
    chunk = Document(page_content="No provenance", metadata={})

    with pytest.raises(ValueError, match="must contain a document_id"):
        pipeline.add_chunk_metadata([chunk])


def test_add_chunk_metadata_rejects_non_document_items():
    """Every item passed to the annotator must be a Document."""
    with pytest.raises(TypeError, match="every chunk to be a Document"):
        pipeline.add_chunk_metadata(["not a document"])


def make_valid_chunks() -> list[Document]:
    """Create fully annotated chunks for validator tests."""
    chunks = [
        Document(
            page_content="Alpha",
            metadata={
                "document_id": "paper-a",
                "document_hash": "hash-a",
                "filename": "a.pdf",
                "page": 0,
            },
        ),
        Document(
            page_content="Beta",
            metadata={
                "document_id": "paper-a",
                "document_hash": "hash-a",
                "filename": "a.pdf",
                "page": 1,
            },
        ),
        Document(
            page_content="Gamma",
            metadata={
                "document_id": "paper-b",
                "document_hash": "hash-b",
                "filename": "b.pdf",
                "page": 0,
            },
        ),
    ]
    return pipeline.add_chunk_metadata(chunks)


def test_validate_chunks_returns_valid_summary():
    """A valid collection should report its chunk and document counts."""
    report = pipeline.validate_chunks(make_valid_chunks())

    assert report == {
        "valid": True,
        "total_chunks": 3,
        "document_count": 2,
        "errors": [],
        "warnings": [],
    }


def test_validate_chunks_rejects_empty_input():
    """An empty collection should be invalid without raising an exception."""
    report = pipeline.validate_chunks([])

    assert report["valid"] is False
    assert report["total_chunks"] == 0
    assert "No chunks found" in report["errors"]


def test_validate_chunks_reports_wrong_item_type():
    """Invalid items should be reported without interrupting validation."""
    report = pipeline.validate_chunks(["not a document"])

    assert report["valid"] is False
    assert "not a Document" in report["errors"][0]


def test_validate_chunks_reports_missing_metadata():
    """All required provenance and identity fields should be present."""
    report = pipeline.validate_chunks(
        [Document(page_content="Text", metadata={"document_id": "paper-a"})]
    )

    assert report["valid"] is False
    assert "missing required metadata" in report["errors"][0]
    assert "chunk_id" in report["errors"][0]


def test_validate_chunks_reports_mismatched_text_hash():
    """Changed content should be detected when its stored hash is stale."""
    chunks = make_valid_chunks()
    chunks[0].page_content = "Changed after hashing"

    report = pipeline.validate_chunks(chunks)

    assert report["valid"] is False
    assert any("mismatched text hash" in error for error in report["errors"])


def test_validate_chunks_reports_duplicate_chunk_id():
    """Vector-store identifiers must be unique within an ingestion run."""
    chunks = make_valid_chunks()
    chunks[1].metadata["chunk_id"] = chunks[0].metadata["chunk_id"]

    report = pipeline.validate_chunks(chunks)

    assert report["valid"] is False
    assert any("Duplicate chunk_id" in error for error in report["errors"])


def test_validate_chunks_reports_blank_text():
    """A chunk containing only whitespace should be invalid."""
    chunks = make_valid_chunks()
    chunks[0].page_content = "   \n"

    report = pipeline.validate_chunks(chunks)

    assert report["valid"] is False
    assert any("blank text" in error for error in report["errors"])


def test_save_chunks_jsonl_writes_one_json_object_per_line(tmp_path):
    """Every chunk should be serialized as a separate JSONL record."""
    output_path = tmp_path / "chunks.jsonl"
    chunks = make_valid_chunks()

    pipeline.save_chunks_jsonl(chunks, output_path)

    lines = output_path.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]
    assert len(records) == len(chunks)
    assert records[0] == {
        "metadata": chunks[0].metadata,
        "page_content": chunks[0].page_content,
    }


def test_save_chunks_jsonl_preserves_unicode(tmp_path):
    """UTF-8 output should retain readable non-ASCII characters."""
    output_path = tmp_path / "unicode.jsonl"
    chunk = Document(page_content="Modèle voorspelling ⚽", metadata={"page": 0})

    pipeline.save_chunks_jsonl([chunk], output_path)

    saved_text = output_path.read_text(encoding="utf-8")
    assert "Modèle voorspelling ⚽" in saved_text
    assert json.loads(saved_text)["page_content"] == chunk.page_content


def test_save_chunks_jsonl_overwrites_deterministically(tmp_path):
    """Repeated writes of unchanged chunks should produce identical output."""
    output_path = tmp_path / "chunks.jsonl"
    output_path.write_text("stale content", encoding="utf-8")
    chunks = make_valid_chunks()

    pipeline.save_chunks_jsonl(chunks, output_path)
    first_output = output_path.read_bytes()
    pipeline.save_chunks_jsonl(chunks, output_path)

    assert output_path.read_bytes() == first_output
    assert b"stale content" not in first_output


def test_save_chunks_jsonl_accepts_string_path_and_empty_input(tmp_path):
    """An empty collection should create an empty file for either path type."""
    output_path = tmp_path / "empty.jsonl"

    pipeline.save_chunks_jsonl([], str(output_path))

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == ""
