"""
Amen Bank Knowledge Base — Text Normalization Module

Produces consistent, retrieval-friendly text representations from
heterogeneous JSON knowledge records.
"""

from __future__ import annotations

import json
import re
from typing import Any


def flatten_list(values: list[Any], bullet: str = "- ") -> str:
    """Join list values into a readable bullet block."""
    lines: list[str] = []
    for value in values:
        if isinstance(value, dict):
            lines.append(bullet + json.dumps(value, ensure_ascii=False))
        elif value is not None and str(value).strip():
            lines.append(bullet + str(value).strip())
    return "\n".join(lines)


def normalize_language(language: str | None) -> str:
    """Normalize language codes to ISO-ish lowercase."""
    if not language:
        return "fr"
    language = language.strip().lower()
    mapping = {"french": "fr", "français": "fr", "english": "en", "arabe": "ar", "arabic": "ar"}
    return mapping.get(language, language[:2] if len(language) > 2 else language)


def build_canonical_text(record: dict[str, Any]) -> str:
    """
    Build a single searchable text blob from a structured KB record.

    Designed for embedding: title + narrative + structured facets.
    """
    parts: list[str] = []

    title = record.get("title") or record.get("question") or record.get("agency_name")
    if title:
        parts.append(str(title).strip())

    for key in ("content", "description", "answer"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())

    facet_map = {
        "needs": "Besoins",
        "recommended_services": "Services recommandés",
        "possible_products": "Produits possibles",
        "features": "Fonctionnalités",
        "workflow": "Workflow",
        "eligibility": "Éligibilité",
        "required_documents": "Documents requis",
        "simulation_parameters": "Paramètres de simulation",
        "recommendations": "Recommandations",
        "services_available": "Services disponibles",
        "channels": "Canaux",
        "possible_questions": "Questions possibles",
        "possible_customer_questions": "Questions clients possibles",
    }
    for key, label in facet_map.items():
        value = record.get(key)
        if isinstance(value, list) and value:
            parts.append(f"{label}:\n{flatten_list(value)}")

    # Agency / contact structured fields
    for key, label in (
        ("agency_name", "Agence"),
        ("city", "Ville"),
        ("address", "Adresse"),
        ("phone", "Téléphone"),
        ("opening_hours", "Horaires"),
        ("email", "Email"),
        ("credit_type", "Type de crédit"),
        ("segment_code", "Segment"),
    ):
        value = record.get(key)
        if value:
            parts.append(f"{label}: {value}")

    text = "\n\n".join(parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized document ready for chunking / indexing."""
    language = normalize_language(record.get("language"))
    category = record.get("category") or "general"
    document_type = record.get("document_type") or category
    source = record.get("source") or "amen_bank_knowledge_base"
    doc_id = record.get("id") or "unknown"

    canonical_text = build_canonical_text(record)
    tags = record.get("tags") if isinstance(record.get("tags"), list) else []

    return {
        "id": doc_id,
        "title": record.get("title") or record.get("question") or record.get("agency_name") or doc_id,
        "text": canonical_text,
        "category": category,
        "subcategory": record.get("subcategory") or record.get("segment_code") or record.get("credit_type"),
        "language": language,
        "source": source,
        "document_type": document_type,
        "tags": tags,
        "metadata": {
            "source": source,
            "category": category,
            "language": language,
            "document_type": document_type,
            "document_id": doc_id,
            "title": record.get("title") or record.get("question") or record.get("agency_name"),
            "tags": tags,
        },
    }
