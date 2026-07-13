import json
import uuid
from pathlib import Path

import structlog

from app.core.config import settings
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    DocumentQuestionRequest,
    DocumentQuestionResponse,
    RecommendRequest,
    RecommendResponse,
    Recommendation,
    SearchRequest,
    SearchResponse,
    SearchResult,
    SourceReference,
)
from app.services.llm_provider import get_llm_provider

logger = structlog.get_logger(__name__)

SEGMENT_RECOMMENDATIONS = {
    "particuliers": [
        ("Compte Courant", "Gestion quotidienne en TND", "Adapté aux besoins courants"),
        ("@mennet", "Banque digitale complète", "Services en ligne 24/7"),
        ("Carte Visa", "Paiements sécurisés", "Acceptée internationalement"),
    ],
    "jeunes": [
        ("Compte Jeune", "Compte adapté aux étudiants", "Frais réduits"),
        ("Amen Mobile", "Application mobile", "Paiements et virements mobiles"),
        ("Épargne Programmée", "Épargne automatique", "Construire un capital"),
    ],
    "entreprises": [
        ("@mennet Corporate", "Banque digitale entreprise", "Trade finance et cash management"),
        ("Crédit Professionnel", "Financement activité", "Investissement et trésorerie"),
        ("Carte Corporate", "Gestion dépenses pro", "Contrôle et reporting"),
    ],
    "professionnels": [
        ("Compte Professionnel", "Compte dédié TPE/PME", "Séparation pro/perso"),
        ("Crédit Investissement", "Financement équipement", "Développement activité"),
    ],
    "tre": [
        ("Compte TRE", "Compte résidents étrangers", "Gestion en devises"),
        ("Banque Internationale", "Transferts SWIFT", "Opérations transfrontalières"),
    ],
}


class RetrievalEngine:
    def __init__(self):
        self._chunks: list[dict] = []
        self._embedder = None
        self._collection = None
        self._load_chunks()

    def _load_chunks(self):
        chunks_path = Path(settings.chunks_path)
        if chunks_path.exists():
            self._chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
            logger.info("loaded_chunks", count=len(self._chunks))

    def _get_embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer(settings.embedding_model)
            except Exception as e:
                logger.warning("embedder_unavailable", error=str(e))
        return self._embedder

    def _get_collection(self):
        if self._collection is None:
            try:
                import chromadb
                client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
                self._collection = client.get_or_create_collection(settings.chroma_collection)
            except Exception as e:
                logger.warning("chromadb_unavailable", error=str(e))
        return self._collection

    def search(self, query: str, top_k: int = 5, language: str | None = None) -> list[dict]:
        collection = self._get_collection()
        if collection and collection.count() > 0:
            embedder = self._get_embedder()
            if embedder:
                query_embedding = embedder.encode(query).tolist()
                where = {"language": language} if language else None
                results = collection.query(
                    query_embeddings=[query_embedding], n_results=top_k, where=where,
                    include=["documents", "metadatas", "distances"],
                )
                hits = []
                for i in range(len(results["ids"][0])):
                    hits.append({
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "score": 1 - results["distances"][0][i],
                        "metadata": results["metadatas"][0][i],
                    })
                return hits

        return self._keyword_search(query, top_k, language)

    def _keyword_search(self, query: str, top_k: int, language: str | None) -> list[dict]:
        query_lower = query.lower()
        scored = []
        for chunk in self._chunks:
            if language and chunk.get("metadata", {}).get("language") != language:
                continue
            text = chunk.get("text", "").lower()
            words = query_lower.split()
            score = sum(1 for w in words if w in text) / max(len(words), 1)
            if score > 0:
                scored.append({"id": chunk["id"], "text": chunk["text"], "score": score,
                                 "metadata": chunk.get("metadata", {})})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


class AIService:
    def __init__(self):
        self.retrieval = RetrievalEngine()
        self.llm = get_llm_provider()
        self._conversations: dict[str, list[dict]] = {}

    async def chat(self, request: ChatRequest) -> ChatResponse:
        conv_id = request.conversation_id or str(uuid.uuid4())
        hits = self.retrieval.search(request.message, top_k=settings.top_k, language=request.language)
        context = "\n\n".join(f"[{h['id']}] {h['text']}" for h in hits)
        prompt = (
            f"Context:\n{context}\n\n"
            f"Question ({request.language}): {request.message}\n\n"
            f"Answer based only on the context above."
        )
        answer = await self.llm.generate(prompt, request.language)
        sources = [
            SourceReference(
                id=h["id"], title=h["metadata"].get("document_id", ""),
                source=h["metadata"].get("source", ""), category=h["metadata"].get("category", ""),
                score=h["score"],
            )
            for h in hits
        ]
        self._conversations.setdefault(conv_id, []).append(
            {"role": "user", "content": request.message}, {"role": "assistant", "content": answer}
        )
        return ChatResponse(answer=answer, sources=sources, conversation_id=conv_id, language=request.language)

    async def search(self, request: SearchRequest) -> SearchResponse:
        hits = self.retrieval.search(request.query, top_k=request.top_k, language=request.language)
        results = [SearchResult(id=h["id"], text=h["text"], score=h["score"], metadata=h["metadata"]) for h in hits]
        return SearchResponse(results=results, query=request.query)

    async def recommend(self, request: RecommendRequest) -> RecommendResponse:
        segment_key = request.segment.lower().strip()
        recs = SEGMENT_RECOMMENDATIONS.get(segment_key, SEGMENT_RECOMMENDATIONS["particuliers"])
        recommendations = [Recommendation(product=r[0], description=r[1], reason=r[2]) for r in recs]
        if request.needs:
            hits = self.retrieval.search(" ".join(request.needs), top_k=3, language=request.language)
            for h in hits:
                cat = h["metadata"].get("category", "")
                recommendations.append(
                    Recommendation(product=cat, description=h["text"][:200], reason="Correspond à vos besoins")
                )
        return RecommendResponse(segment=request.segment, recommendations=recommendations[:5])

    async def document_question(self, request: DocumentQuestionRequest) -> DocumentQuestionResponse:
        hits = self.retrieval.search(request.question, top_k=3)
        doc_hits = [h for h in hits if h["metadata"].get("document_id") == request.document_id]
        if not doc_hits:
            doc_hits = [h for h in self.retrieval._chunks if h.get("metadata", {}).get("document_id") == request.document_id][:3]
            doc_hits = [{"id": c["id"], "text": c["text"], "score": 1.0, "metadata": c.get("metadata", {})} for c in doc_hits]
        context = "\n".join(h["text"] for h in doc_hits)
        prompt = f"Document context:\n{context}\n\nQuestion: {request.question}\nAnswer:"
        answer = await self.llm.generate(prompt, request.language)
        sources = [SourceReference(id=h["id"], source=h["metadata"].get("source", ""),
                                   category=h["metadata"].get("category", "")) for h in doc_hits]
        return DocumentQuestionResponse(document_id=request.document_id, question=request.question,
                                        answer=answer, sources=sources)
