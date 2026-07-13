"""
Amen Bank Knowledge Base — Document Cleaning Module

Removes HTML artifacts, navigation/footer noise, duplicated content,
and normalizes whitespace/encoding while preserving meaningful banking
service information. Never retains customer-specific demo data patterns.
"""

from __future__ import annotations

import hashlib
import html
import re
import unicodedata
from typing import Any

from bs4 import BeautifulSoup

# Patterns that may appear when scraping web pages — strip aggressively.
NAV_FOOTER_PATTERNS = [
    re.compile(r"(?i)accueil\s*\|\s*particuliers\s*\|\s*professionnels"),
    re.compile(r"(?i)mentions légales"),
    re.compile(r"(?i)politique de confidentialité"),
    re.compile(r"(?i)tous droits réservés"),
    re.compile(r"(?i)cookie(s)?\s*(policy|settings|consent)"),
    re.compile(r"(?i)menu\s*principal"),
    re.compile(r"(?i)skip to (main )?content"),
]

# Privacy: reject content that looks like customer/demo account data.
SENSITIVE_PATTERNS = [
    re.compile(r"\bTN\d{2}[A-Z0-9]{20,30}\b"),  # IBAN-like
    re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),  # card-like
    re.compile(r"(?i)\b(account|compte)\s*(number|n[o°]?)\s*[:\-]?\s*\d{6,}"),
    re.compile(r"(?i)\b(solde|balance)\s*[:\-]?\s*\d+([.,]\d{3})*\s*(tnd|dt|€|\$)?"),
    re.compile(r"(?i)\b(password|mot de passe|login)\s*[:\-]\s*\S+"),
]


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities using BeautifulSoup."""
    if not text:
        return ""
    if "<" in text and ">" in text:
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
    return html.unescape(text)


def normalize_encoding(text: str) -> str:
    """Normalize unicode to NFC and replace non-printable controls."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)
    return text


def normalize_spaces(text: str) -> str:
    """Collapse whitespace while preserving paragraph breaks lightly."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_navigation_and_footer(text: str) -> str:
    """Remove common scraped navigation/footer repetitions."""
    for pattern in NAV_FOOTER_PATTERNS:
        text = pattern.sub(" ", text)
    return text


def contains_sensitive_customer_data(text: str) -> bool:
    """Return True if text appears to contain customer/demo financial data."""
    return any(p.search(text) for p in SENSITIVE_PATTERNS)


def clean_text(text: str) -> str:
    """Full cleaning pipeline for a single text field."""
    text = strip_html(text)
    text = normalize_encoding(text)
    text = remove_navigation_and_footer(text)
    text = normalize_spaces(text)
    return text


def content_fingerprint(text: str) -> str:
    """Stable hash for near-exact deduplication."""
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _synthesize_primary_text(record: dict[str, Any]) -> str:
    """Build a primary narrative for records that use structured fields only."""
    for key in ("content", "description", "answer"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    # Agency / location records
    if record.get("agency_name") or record.get("category") == "agencies":
        parts = [
            record.get("agency_name"),
            record.get("city"),
            record.get("address"),
            record.get("phone"),
            record.get("opening_hours"),
        ]
        services = record.get("services_available")
        if isinstance(services, list) and services:
            parts.append("Services: " + ", ".join(str(s) for s in services if s))
        return clean_text(" | ".join(str(p) for p in parts if p))

    # FAQ-style fallback
    if record.get("question") and record.get("answer"):
        return clean_text(f"{record['question']} {record['answer']}")

    title = record.get("title")
    return clean_text(str(title)) if title else ""


def clean_document_record(record: dict[str, Any]) -> dict[str, Any] | None:
    """
    Clean a raw JSON document record.

    Returns None if the record is empty after cleaning or fails privacy checks.
    """
    cleaned = dict(record)
    text_fields = (
        "content",
        "description",
        "answer",
        "title",
        "question",
        "agency_name",
        "city",
        "address",
        "phone",
        "opening_hours",
        "email",
        "website",
        "banking_website",
        "risk_disclaimer",
    )

    for field in text_fields:
        if field in cleaned and isinstance(cleaned[field], str):
            cleaned[field] = clean_text(cleaned[field])

    # Clean list-of-strings fields commonly used in the KB.
    list_fields = (
        "needs",
        "recommended_services",
        "possible_products",
        "features",
        "workflow",
        "possible_questions",
        "possible_customer_questions",
        "eligibility",
        "required_documents",
        "simulation_parameters",
        "recommendations",
        "channels",
        "services_available",
        "tags",
        "emails",
    )
    for field in list_fields:
        if field in cleaned and isinstance(cleaned[field], list):
            cleaned[field] = [
                clean_text(item) if isinstance(item, str) else item
                for item in cleaned[field]
                if item is not None and (not isinstance(item, str) or clean_text(item))
            ]

    primary = _synthesize_primary_text(cleaned)
    if not primary or len(primary) < 20:
        return None
    if contains_sensitive_customer_data(primary):
        return None

    # Ensure downstream normalizers always find narrative text for agencies.
    if not cleaned.get("content") and cleaned.get("agency_name"):
        cleaned["content"] = primary

    cleaned["_fingerprint"] = content_fingerprint(primary)
    return cleaned

def deduplicate_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicated content based on fingerprint; keep first occurrence."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for record in records:
        fingerprint = record.get("_fingerprint")
        if not fingerprint:
            primary = record.get("content") or record.get("description") or record.get("answer") or ""
            fingerprint = content_fingerprint(str(primary))
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        unique.append(record)
    return unique
