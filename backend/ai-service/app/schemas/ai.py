from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: str = Field(default="fr", pattern="^(fr|ar|en)$")
    conversation_id: str | None = None


class SourceReference(BaseModel):
    id: str
    title: str = ""
    source: str = ""
    category: str = ""
    score: float = 0.0


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    conversation_id: str
    language: str


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    language: str | None = None


class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str


class RecommendRequest(BaseModel):
    segment: str = Field(min_length=2)
    needs: list[str] = Field(default_factory=list)
    language: str = Field(default="fr", pattern="^(fr|ar|en)$")


class Recommendation(BaseModel):
    product: str
    description: str
    reason: str


class RecommendResponse(BaseModel):
    segment: str
    recommendations: list[Recommendation]


class DocumentQuestionRequest(BaseModel):
    document_id: str
    question: str = Field(min_length=1, max_length=500)
    language: str = Field(default="fr", pattern="^(fr|ar|en)$")


class DocumentQuestionResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    sources: list[SourceReference]
