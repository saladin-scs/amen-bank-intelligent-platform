"""Smoke tests for the Amen Bank knowledge-base preprocessing pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PREPROCESSING_ROOT = Path(__file__).resolve().parent
AI_ENGINE_ROOT = PREPROCESSING_ROOT.parent
sys.path.insert(0, str(PREPROCESSING_ROOT))

from clean_documents import clean_text, contains_sensitive_customer_data, clean_document_record
from chunk_documents import chunk_text, approximate_token_count
from normalize_text import normalize_record
from run_pipeline import run_pipeline


def test_clean_strips_html_and_nav() -> None:
    raw = "<nav>Accueil | Particuliers</nav><p>Consultation des comptes Amen Bank.</p><footer>Tous droits réservés</footer>"
    cleaned = clean_text(raw)
    assert "Consultation des comptes Amen Bank" in cleaned
    assert "<p>" not in cleaned


def test_privacy_guard_blocks_balance_dump() -> None:
    assert contains_sensitive_customer_data("solde: 12500 TND")
    assert not contains_sensitive_customer_data("La consultation du solde est disponible en temps réel.")


def test_agency_record_is_accepted() -> None:
    record = {
        "id": "agy-test",
        "category": "agencies",
        "agency_name": "Amen Bank Tunis Centre",
        "city": "Tunis",
        "address": "Avenue de la Liberté",
        "phone": "+216 71 000 000",
        "opening_hours": "Lundi-Vendredi",
        "services_available": ["Comptes", "Crédits"],
        "language": "fr",
        "source": "test",
        "document_type": "agency",
    }
    cleaned = clean_document_record(record)
    assert cleaned is not None
    assert cleaned.get("content")


def test_chunking_respects_size_and_overlap() -> None:
    words = ["Amen"] * 800
    text = " ".join(words) + "."
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    assert len(chunks) >= 2
    assert all(approximate_token_count(c) <= 650 for c in chunks)


def test_pipeline_outputs_exist() -> None:
    summary = run_pipeline()
    assert summary["documents"] >= 90
    assert summary["chunks"] >= 90
    assert summary["rejected"] == 0

    documents = json.loads(Path(summary["documents_path"]).read_text(encoding="utf-8"))
    chunks = json.loads(Path(summary["chunks_path"]).read_text(encoding="utf-8"))
    assert documents
    assert chunks
    assert "metadata" in chunks[0]
    assert set(chunks[0]["metadata"]) >= {"source", "category", "language", "document_type"}

    normalized = normalize_record(
        {
            "id": "x-1",
            "title": "Test",
            "content": "Contenu de test pour normalisation Amen Bank.",
            "category": "faq",
            "language": "fr",
            "source": "unit",
            "document_type": "faq",
        }
    )
    assert normalized["text"]
    assert normalized["metadata"]["category"] == "faq"
