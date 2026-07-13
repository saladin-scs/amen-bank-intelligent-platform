"""
Amen Bank Knowledge Base — Metadata Generation Module

Produces dataset-level source catalog and provenance metadata for
governance, auditability, and future vector-store indexing.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def collect_source_stats(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate documents by source URL / file reference."""
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for doc in documents:
        source = str(doc.get("source") or "unknown")
        by_source[source].append(doc)

    catalog: list[dict[str, Any]] = []
    for source, docs in sorted(by_source.items(), key=lambda x: x[0]):
        languages = sorted({d.get("language", "fr") for d in docs})
        categories = sorted({d.get("category", "general") for d in docs})
        catalog.append(
            {
                "source": source,
                "document_count": len(docs),
                "categories": categories,
                "languages": languages,
                "document_ids": [d.get("id") for d in docs],
                "license_note": "Public corporate information for educational RAG use. No customer PII.",
                "privacy_note": "Excludes account numbers, balances, transactions, and login credentials.",
            }
        )
    return catalog


def build_dataset_metadata(
    documents: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    raw_files: list[str],
) -> dict[str, Any]:
    """Build a full metadata payload for sources.json and pipeline audits."""
    category_counts = Counter(d.get("category", "general") for d in documents)
    language_counts = Counter(d.get("language", "fr") for d in documents)
    doc_type_counts = Counter(d.get("document_type", "unknown") for d in documents)

    return {
        "dataset_name": "Amen Bank Intelligent Digital Banking — Knowledge Base",
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "crisp_dm_phase": "Data Preparation",
        "purpose": [
            "RAG chatbot",
            "Semantic search",
            "Banking assistant",
            "Product recommendation",
            "Document question answering",
            "Multilingual AI assistant",
        ],
        "privacy_policy": {
            "stores_customer_pii": False,
            "stores_account_numbers": False,
            "stores_balances": False,
            "stores_transaction_amounts": False,
            "stores_login_information": False,
            "content_scope": "Generic banking functionalities and public corporate services only",
        },
        "chunking": {
            "chunk_size_tokens": 500,
            "overlap_tokens": 100,
            "tokenizer": "approximate_whitespace_french_english",
        },
        "statistics": {
            "raw_files": len(raw_files),
            "documents": len(documents),
            "chunks": len(chunks),
            "categories": dict(category_counts),
            "languages": dict(language_counts),
            "document_types": dict(doc_type_counts),
            "avg_tokens_per_chunk": (
                round(sum(c.get("token_count", 0) for c in chunks) / len(chunks), 2) if chunks else 0
            ),
        },
        "raw_files": raw_files,
        "sources": collect_source_stats(documents),
        "downstream_targets": [
            "embedding generation",
            "ChromaDB indexing",
            "semantic retrieval",
            "RAG answer generation",
            "recommendation feature store (segments/products)",
        ],
    }


def write_json(path: Path, payload: Any) -> None:
    """Write UTF-8 JSON with stable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
