"""
Amen Bank Knowledge Base — Chunking Module

Token-aware recursive chunking with overlap for RAG embedding pipelines.

Default strategy:
  - chunk_size: 500 tokens
  - overlap: 100 tokens
"""

from __future__ import annotations

import re
from typing import Any


DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 100


def approximate_token_count(text: str) -> int:
    """
    Approximate token count without requiring a proprietary tokenizer.

    Uses whitespace word pieces with a mild subword factor suitable for
    French/English banking text (~1.3 tokens per whitespace word).
    """
    words = re.findall(r"\S+", text)
    if not words:
        return 0
    return max(1, int(len(words) * 1.3))


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences while keeping punctuation."""
    parts = re.split(r"(?<=[\.\!\?\n])\s+", text.strip())
    return [p.strip() for p in parts if p and p.strip()]


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:
    """
    Chunk text to approximately `chunk_size` tokens with `overlap` tokens.

    Prefer sentence boundaries; fall back to word windows for long sentences.
    """
    if not text or not text.strip():
        return []
    if approximate_token_count(text) <= chunk_size:
        return [text.strip()]

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    sentences = split_into_sentences(text)
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    def flush() -> None:
        nonlocal current, current_tokens
        if current:
            chunks.append(" ".join(current).strip())
            # Build overlap window from the end of the flushed chunk.
            overlap_words: list[str] = []
            token_budget = 0
            for sentence in reversed(current):
                words = re.findall(r"\S+", sentence)
                approx = max(1, int(len(words) * 1.3))
                if token_budget + approx > overlap and overlap_words:
                    break
                overlap_words.insert(0, sentence)
                token_budget += approx
            current = overlap_words
            current_tokens = approximate_token_count(" ".join(current)) if current else 0

    for sentence in sentences:
        sent_tokens = approximate_token_count(sentence)
        if sent_tokens > chunk_size:
            # Hard-split oversized sentence by words.
            words = re.findall(r"\S+", sentence)
            step_words = max(1, int(chunk_size / 1.3))
            overlap_words = max(1, int(overlap / 1.3))
            start = 0
            while start < len(words):
                window = words[start : start + step_words]
                chunks.append(" ".join(window))
                if start + step_words >= len(words):
                    break
                start += max(1, step_words - overlap_words)
            current = []
            current_tokens = 0
            continue

        if current_tokens + sent_tokens > chunk_size and current:
            flush()
        current.append(sentence)
        current_tokens += sent_tokens

    if current:
        chunks.append(" ".join(current).strip())

    # Drop tiny trailing fragments that are pure overlap duplicates.
    deduped: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        key = re.sub(r"\s+", " ", chunk.lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        if approximate_token_count(chunk) >= 20 or not deduped:
            deduped.append(chunk)
    return deduped


def chunk_document(
    document: dict[str, Any],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[dict[str, Any]]:
    """Create RAG chunks with required metadata for a normalized document."""
    text = document.get("text") or ""
    pieces = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    base_meta = dict(document.get("metadata") or {})
    base_meta.update(
        {
            "source": document.get("source"),
            "category": document.get("category"),
            "language": document.get("language"),
            "document_type": document.get("document_type"),
            "document_id": document.get("id"),
            "title": document.get("title"),
        }
    )

    chunks: list[dict[str, Any]] = []
    total = len(pieces)
    for index, piece in enumerate(pieces):
        chunk_id = f"{document.get('id', 'doc')}_chunk_{index:03d}"
        chunks.append(
            {
                "id": chunk_id,
                "text": piece,
                "token_count": approximate_token_count(piece),
                "chunk_index": index,
                "chunk_total": total,
                "metadata": {
                    **base_meta,
                    "chunk_id": chunk_id,
                    "chunk_index": index,
                    "chunk_total": total,
                    "chunk_size_target": chunk_size,
                    "chunk_overlap_target": overlap,
                },
            }
        )
    return chunks
