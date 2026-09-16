"""PDF ingestion pipeline for the football research corpus.

The functions in this module are intentionally left as exercises. Implement them
as small, deterministic transformations so they remain easy to test and reuse
from notebooks or command-line workflows.
"""

import hashlib
import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf.errors import PyPdfError


logger = logging.getLogger(__name__)


def load_pdf(path: Path) -> list[Document]:
    """Extract a PDF into page-level LangChain documents.

    Each returned document should contain the extracted text for one page and
    metadata identifying at least the source path, filename, stable document ID,
    page number, and document hash.

    Args:
        path: Path to the source PDF.

    Returns:
        Page-level documents in their original reading order.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        ValueError: If ``path`` is not a PDF or no usable text can be extracted.
    """
    
    path = Path(path)

    # check if path leads to valid file
    if not path.is_file():
        raise FileNotFoundError(f"PDF file not found: {path}")

    # check if the file endswith .pdf
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, received: {path}")

    # load the pdf in docs
    loader = PyPDFLoader(path)
    docs = loader.load()

    # check if all docs are empty
    if not docs or not any(doc.page_content.strip() for doc in docs):
        raise ValueError(f"No usable text extracted from PDF: {path}")

    # create hashes and add additional metadata to the documents
    with path.open("rb") as pdf_file:
        document_hash = hashlib.file_digest(pdf_file, "sha256").hexdigest()
    document_id = document_hash  # Content-based and stable

    for doc in docs:
        doc.metadata.update(
            {
                "filename": path.name,
                "document_id": document_id,
                "document_hash": document_hash,
            }
        )
    
    return docs
    

def clean_document(document: Document) -> Document:
    """Return a cleaned copy of an extracted document.

    Cleaning may normalize whitespace and common PDF extraction artifacts. It
    should not silently remove substantive content or perform chunking. The
    input document is not mutated, and its metadata is preserved.

    Args:
        document: Document containing raw text extracted from a PDF page.

    Returns:
        A new document containing deterministically cleaned text and a copy of
        the original metadata.

    Raises:
        TypeError: If ``document`` is not a ``Document`` instance.
    """
    if not isinstance(document, Document):
        raise TypeError(
            f"Expected document to be a Document, received: {type(document)}"
        )

    text = document.page_content

    # Normalize platform-specific line endings before other whitespace handling.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Normalize compatibility characters, including common PDF ligatures.
    text = unicodedata.normalize("NFKC", text)

    # Remove control/format characters while retaining line breaks and tabs.
    text = "".join(
        character
        for character in text
        if character in {"\n", "\t"}
        or not unicodedata.category(character).startswith("C")
    )

    # Collapse horizontal whitespace without destroying paragraph boundaries.
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)

    # Keep at most one empty line between text blocks.
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return document.model_copy(
        update={"page_content": text},
        deep=True,
    )


def chunk_documents(
    documents: list[Document],
    *,
    chunk_size: int,
    chunk_overlap: int,
    encoding_name: str = "cl100k_base",
) -> list[Document]:
    """Split page-level documents into smaller documents for retrieval.

    Preserve all source metadata on every chunk. Chunk boundaries and ordering
    must be deterministic for the same inputs and configuration.

    Args:
        documents: Cleaned, page-level documents to split.
        chunk_size: Maximum target size of a chunk, measured according to the
            selected text splitter.
        chunk_overlap: Target overlap between adjacent chunks.
        encoding_name: Tokenizer encoding used to measure chunk size and
            overlap.

    Returns:
        Chunk documents in deterministic source order.

    Raises:
        ValueError: If ``chunk_size`` is not positive, ``chunk_overlap`` is
            negative, or ``chunk_overlap`` is not smaller than ``chunk_size``.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be 0 or greater")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name=encoding_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = splitter.split_documents(documents)
    return chunks


def add_chunk_metadata(chunks: list[Document]) -> list[Document]:
    """Add stable retrieval and provenance metadata to every chunk.

    Add at least a chunk index, stable chunk ID, and chunk-text hash. Stable IDs
    should be reproducible when the source content and chunking configuration
    have not changed.

    Args:
        chunks: Chunk documents with their source metadata preserved.

    Returns:
        New documents containing the completed chunk metadata. Input documents
        are not mutated.

    Raises:
        TypeError: If an item in ``chunks`` is not a ``Document``.
        ValueError: If a chunk is missing its ``document_id`` metadata.
    """
    document_chunk_counts: dict[str, int] = {}
    annotated_chunks: list[Document] = []

    for chunk in chunks:
        if not isinstance(chunk, Document):
            raise TypeError(
                f"Expected every chunk to be a Document, received: {type(chunk)}"
            )

        document_id = chunk.metadata.get("document_id")
        if not document_id:
            raise ValueError("Chunk metadata must contain a document_id")

        chunk_index = document_chunk_counts.get(document_id, 0)
        document_chunk_counts[document_id] = chunk_index + 1

        chunk_text_hash = hashlib.sha256(
            chunk.page_content.encode("utf-8")
        ).hexdigest()
        chunk_identity = f"{document_id}:{chunk_index}:{chunk_text_hash}"
        chunk_id = hashlib.sha256(chunk_identity.encode("utf-8")).hexdigest()

        metadata = {
            **chunk.metadata,
            "chunk_index": chunk_index,
            "chunk_id": chunk_id,
            "chunk_text_hash": chunk_text_hash,
        }
        annotated_chunks.append(
            chunk.model_copy(update={"metadata": metadata}, deep=True)
        )

    return annotated_chunks


def validate_chunks(chunks: list[Document]) -> dict[str, Any]:
    """Check chunk quality and return a machine-readable validation report.

    Check for an empty result, invalid item types, blank text, missing required
    metadata, mismatched text hashes, and duplicate chunk IDs. Validation reports
    problems rather than silently discarding content.

    Args:
        chunks: Fully annotated chunk documents to validate.

    Returns:
        A report containing summary counts, warnings, and errors.
    """

    report: dict[str, Any] = {
        "valid": True,
        "total_chunks": len(chunks),
        "document_count": 0,
        "errors": [],
        "warnings": [],
    }

    if not chunks:
        report["errors"].append("No chunks found")

    required_metadata_fields = (
        "document_id",
        "document_hash",
        "filename",
        "page",
        "chunk_index",
        "chunk_id",
        "chunk_text_hash",
    )
    document_ids: set[str] = set()
    seen_chunk_ids: set[str] = set()

    for position, chunk in enumerate(chunks):
        if not isinstance(chunk, Document):
            report["errors"].append(
                f"Chunk at position {position} is not a Document"
            )
            continue

        if not chunk.page_content.strip():
            report["errors"].append(
                f"Chunk at position {position} contains blank text"
            )

        missing_fields = [
            field
            for field in required_metadata_fields
            if field not in chunk.metadata or chunk.metadata[field] in (None, "")
        ]
        if missing_fields:
            report["errors"].append(
                f"Chunk at position {position} is missing required metadata: "
                f"{', '.join(missing_fields)}"
            )

        document_id = chunk.metadata.get("document_id")
        if document_id:
            document_ids.add(document_id)

        stored_text_hash = chunk.metadata.get("chunk_text_hash")
        if stored_text_hash:
            actual_text_hash = hashlib.sha256(
                chunk.page_content.encode("utf-8")
            ).hexdigest()
            if stored_text_hash != actual_text_hash:
                report["errors"].append(
                    f"Chunk at position {position} has a mismatched text hash"
                )

        chunk_id = chunk.metadata.get("chunk_id")
        if chunk_id:
            if chunk_id in seen_chunk_ids:
                report["errors"].append(f"Duplicate chunk_id found: {chunk_id}")
            seen_chunk_ids.add(chunk_id)

    report["document_count"] = len(document_ids)
    report["valid"] = not report["errors"]

    return report


def save_chunks_jsonl(chunks: list[Document], output_path: Path) -> None:
    """Write processed chunks to a UTF-8 JSON Lines file.

    Write one JSON object per line with separate ``page_content`` and
    ``metadata`` fields. Produce deterministic output so repeated ingestion of
    unchanged inputs does not create meaningless diffs.

    Args:
        chunks: Validated documents to serialize.
        output_path: Destination ``.jsonl`` file.
    """
    output_path = Path(output_path)
    with output_path.open(mode="w", encoding="utf-8") as file:
        for chunk in chunks:
            data = {
                "metadata": chunk.metadata,
                "page_content": chunk.page_content,
            }

            file.write(json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n")


def ingest_documents(
    input_dir: Path,
    output_path: Path,
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> dict[str, Any]:
    """Run the complete ingestion pipeline for every PDF in a directory.

    Discover PDFs in deterministic order, extract and clean their pages, create
    chunks, add metadata, validate the result, and save it as JSONL. A failure in
    one document should be visible in the returned report rather than silently
    ignored.

    Args:
        input_dir: Directory containing source PDF files.
        output_path: Destination for the processed JSONL dataset.
        chunk_size: Maximum target chunk size passed to ``chunk_documents``.
        chunk_overlap: Chunk overlap passed to ``chunk_documents``.

    Returns:
        A report summarizing processed files, generated chunks, warnings,
        failures, and the output location.
    """

    input_path = Path(input_dir)
    output_path = Path(output_path)
    all_chunks = []
    processed_files = []
    failed_files = []

    for pdf_file in sorted(input_path.glob("*.pdf")):
        logger.info("Loading PDF: %s", pdf_file.name)
        try:
            docs = load_pdf(pdf_file)
        except (OSError, ValueError, PyPdfError) as error:
            logger.warning("Failed to load PDF %s: %s", pdf_file.name, error)
            failed_files.append(
                {
                    "filename": pdf_file.name,
                    "error": str(error),
                }
            )
            continue

        logger.debug("Loaded %d pages from %s", len(docs), pdf_file.name)

        logger.debug("Cleaning pages from %s", pdf_file.name)
        clean_docs = [clean_document(doc) for doc in docs]

        logger.debug("Chunking pages from %s", pdf_file.name)
        chunks = chunk_documents(
            clean_docs,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        logger.debug("Adding metadata to %d chunks", len(chunks))
        chunks_with_metadata = add_chunk_metadata(chunks)

        all_chunks.extend(chunks_with_metadata)
        processed_files.append(pdf_file.name)

    logger.info("Validating %d chunks", len(all_chunks))
    report = validate_chunks(all_chunks)
    for failure in failed_files:
        report["errors"].append(
            f"Failed to load {failure['filename']}: {failure['error']}"
        )

    report.update(
        {
            "processed_files": processed_files,
            "failed_files": failed_files,
            "output_path": str(output_path),
            "saved": False,
        }
    )
    report["valid"] = not report["errors"]

    if report["valid"]:
        logger.info("Saving chunks to %s", output_path)
        save_chunks_jsonl(all_chunks, output_path)
        report["saved"] = True
    else:
        logger.warning(
            "Ingestion validation failed with %d errors", len(report["errors"])
        )

    return report
