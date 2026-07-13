# Database Schema

## PostgreSQL Schemas

Two bounded contexts share one PostgreSQL instance with separate schemas.

## Auth Schema (`auth`)

### users

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK, default gen_random_uuid() |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | NOT NULL |
| phone | VARCHAR(20) | |
| role | VARCHAR(50) | DEFAULT 'customer' |
| is_active | BOOLEAN | DEFAULT true |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | |

### refresh_tokens

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| token_hash | VARCHAR(255) | NOT NULL |
| expires_at | TIMESTAMPTZ | NOT NULL |
| revoked | BOOLEAN | DEFAULT false |
| created_at | TIMESTAMPTZ | DEFAULT now() |

## Banking Schema (`banking`)

### accounts

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| user_id | UUID | NOT NULL (from auth) |
| account_number | VARCHAR(20) | UNIQUE |
| account_type | VARCHAR(50) | checking, savings |
| currency | VARCHAR(3) | DEFAULT 'TND' |
| balance | DECIMAL(15,3) | DEFAULT 0 |
| status | VARCHAR(20) | active, frozen |
| created_at | TIMESTAMPTZ | |

### transactions

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| account_id | UUID | FK → accounts.id |
| type | VARCHAR(20) | credit, debit |
| amount | DECIMAL(15,3) | NOT NULL |
| description | TEXT | |
| reference | VARCHAR(50) | |
| created_at | TIMESTAMPTZ | |

### beneficiaries

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| user_id | UUID | NOT NULL |
| name | VARCHAR(255) | |
| account_number | VARCHAR(20) | |
| bank_name | VARCHAR(255) | |
| created_at | TIMESTAMPTZ | |

### transfers

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| user_id | UUID | NOT NULL |
| from_account_id | UUID | FK |
| to_account_number | VARCHAR(20) | |
| beneficiary_id | UUID | FK, nullable |
| amount | DECIMAL(15,3) | |
| status | VARCHAR(20) | pending, completed, failed |
| description | TEXT | |
| created_at | TIMESTAMPTZ | |

### products

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| name | VARCHAR(255) | |
| category | VARCHAR(50) | account, card, loan |
| description | TEXT | |
| features | JSONB | |
| is_active | BOOLEAN | DEFAULT true |

### agencies

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| name | VARCHAR(255) | |
| address | TEXT | |
| city | VARCHAR(100) | |
| phone | VARCHAR(20) | |
| latitude | DECIMAL(10,7) | |
| longitude | DECIMAL(10,7) | |

### messages

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| user_id | UUID | NOT NULL |
| subject | VARCHAR(255) | |
| body | TEXT | |
| status | VARCHAR(20) | open, closed |
| created_at | TIMESTAMPTZ | |

## ER Diagram

```mermaid
erDiagram
    users ||--o{ refresh_tokens : has
    users ||--o{ accounts : owns
    accounts ||--o{ transactions : has
    users ||--o{ beneficiaries : manages
    users ||--o{ transfers : initiates
    users ||--o{ messages : sends
    accounts ||--o{ transfers : from
    beneficiaries ||--o{ transfers : to
```

## ChromaDB Collection

Collection: `amen_bank_kb`

| Field | Type | Description |
| --- | --- | --- |
| id | string | chunk ID |
| embedding | float[] | 768-dim vector |
| document | string | chunk text |
| metadata | object | category, language, source, document_id |

## Redis Keys

| Key Pattern | Purpose | TTL |
| --- | --- | --- |
| `rate_limit:{ip}` | Request counter | 60s |
| `session:{user_id}` | Cached user profile | 300s |
