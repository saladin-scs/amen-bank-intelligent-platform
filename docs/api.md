# API Reference

Base URL: `http://localhost:8000` (via API Gateway)

## Authentication

### Register

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "+21612345678"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

Response:

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Refresh Token

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

### Current User

```http
GET /auth/me
Authorization: Bearer <access_token>
```

## Banking

All banking endpoints require `Authorization: Bearer <access_token>`.

### Accounts

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/banking/accounts` | List user accounts |
| GET | `/banking/accounts/{id}` | Account details |
| GET | `/banking/accounts/{id}/transactions` | Transaction history |

### Transfers

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/banking/transfers` | Create transfer |
| GET | `/banking/transfers` | Transfer history |
| GET | `/banking/beneficiaries` | List beneficiaries |
| POST | `/banking/beneficiaries` | Add beneficiary |

### Products

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/banking/products` | List products |
| GET | `/banking/products/{id}` | Product details |

### Agencies

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/banking/agencies` | List agencies |
| GET | `/banking/agencies/{id}` | Agency details |

### Messages

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/banking/messages` | Support messages |
| POST | `/banking/messages` | Send message |

## AI Service

### Chat (RAG Assistant)

```http
POST /ai/chat
Content-Type: application/json

{
  "message": "Comment ouvrir un compte @mennet ?",
  "language": "fr",
  "conversation_id": "optional-uuid"
}
```

Response:

```json
{
  "answer": "...",
  "sources": [{"id": "...", "title": "...", "source": "https://..."}],
  "conversation_id": "uuid",
  "language": "fr"
}
```

### Semantic Search

```http
POST /ai/search
Content-Type: application/json

{
  "query": "carte internationale",
  "top_k": 5,
  "language": "fr"
}
```

### Product Recommendation

```http
POST /ai/recommend
Content-Type: application/json

{
  "segment": "jeunes",
  "needs": ["épargne", "paiement mobile"],
  "language": "fr"
}
```

### Document Question

```http
POST /ai/document-question
Content-Type: application/json

{
  "document_id": "acc-001",
  "question": "Quels sont les frais ?",
  "language": "fr"
}
```

## Error Responses

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

| Code | Meaning |
| --- | --- |
| 400 | Validation error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
