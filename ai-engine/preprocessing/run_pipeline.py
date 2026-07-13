"""
Amen Bank Knowledge Base — Preprocessing Pipeline Orchestrator

Pipeline:
  Raw JSON datasets
    → Cleaning (HTML/noise/PII guards/dedup)
    → Normalization (canonical retrieval text)
    → Chunking (500 tokens / 100 overlap)
    → Metadata catalog
    → processed/documents.json + processed/chunks.json + metadata/sources.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

from chunk_documents import DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP, chunk_document
from clean_documents import clean_document_record, deduplicate_records
from generate_metadata import build_dataset_metadata, write_json
from normalize_text import normalize_record

AI_ENGINE_ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = AI_ENGINE_ROOT / "datasets"
RAW_ROOT = DATASETS_ROOT / "raw"
PROCESSED_ROOT = DATASETS_ROOT / "processed"
METADATA_ROOT = DATASETS_ROOT / "metadata"


def load_raw_records() -> tuple[list[dict], list[str]]:
    """Load all JSON arrays / objects from datasets/raw recursively."""
    records: list[dict] = []
    files: list[str] = []

    for path in sorted(RAW_ROOT.rglob("*.json")):
        relative = str(path.relative_to(DATASETS_ROOT)).replace("\\", "/")
        files.append(relative)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    item = dict(item)
                    item.setdefault("_raw_file", relative)
                    records.append(item)
        elif isinstance(payload, dict):
            payload = dict(payload)
            payload.setdefault("_raw_file", relative)
            records.append(payload)

    return records, files


def run_pipeline(
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> dict:
    """Execute the full data-preparation pipeline and persist outputs."""
    raw_records, raw_files = load_raw_records()
    if not raw_records:
        raise RuntimeError(f"No raw JSON records found under {RAW_ROOT}")

    cleaned: list[dict] = []
    rejected = 0
    for record in raw_records:
        result = clean_document_record(record)
        if result is None:
            rejected += 1
            continue
        cleaned.append(result)

    unique = deduplicate_records(cleaned)

    # Pandas quality report for auditability.
    frame = pd.DataFrame(
        [
            {
                "id": r.get("id"),
                "category": r.get("category"),
                "language": r.get("language"),
                "source": r.get("source"),
                "raw_file": r.get("_raw_file"),
                "content_len": len(str(r.get("content") or r.get("description") or r.get("answer") or "")),
            }
            for r in unique
        ]
    )

    documents = [normalize_record(r) for r in unique]
    # Ensure stable unique IDs after normalization.
    seen_ids: set[str] = set()
    for index, doc in enumerate(documents):
        base_id = str(doc["id"])
        if base_id in seen_ids:
            doc["id"] = f"{base_id}_{index}"
            doc["metadata"]["document_id"] = doc["id"]
        seen_ids.add(doc["id"])

    chunks: list[dict] = []
    for doc in documents:
        chunks.extend(chunk_document(doc, chunk_size=chunk_size, overlap=overlap))

    metadata = build_dataset_metadata(documents, chunks, raw_files)
    metadata["pipeline"] = {
        "raw_loaded": len(raw_records),
        "rejected_privacy_or_empty": rejected,
        "after_dedup": len(unique),
        "documents_written": len(documents),
        "chunks_written": len(chunks),
        "chunk_size": chunk_size,
        "overlap": overlap,
    }

    write_json(PROCESSED_ROOT / "documents.json", documents)
    write_json(PROCESSED_ROOT / "chunks.json", chunks)
    write_json(METADATA_ROOT / "sources.json", metadata)

    quality_path = METADATA_ROOT / "quality_report.csv"
    frame.to_csv(quality_path, index=False, encoding="utf-8")

    summary = {
        "documents": len(documents),
        "chunks": len(chunks),
        "rejected": rejected,
        "raw_files": len(raw_files),
        "documents_path": str(PROCESSED_ROOT / "documents.json"),
        "chunks_path": str(PROCESSED_ROOT / "chunks.json"),
        "sources_path": str(METADATA_ROOT / "sources.json"),
        "quality_report_path": str(quality_path),
    }
    return summary


def main() -> int:
    summary = run_pipeline()
    print("Amen Bank Knowledge Base preprocessing completed.")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
