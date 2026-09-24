# Database Design

## Overview
The application database (relational) holds operational and metadata objects like Users, Audit Logs, and saved Recommendations.
**It does NOT hold the Big Data (trips, tickets) which remain in Parquet format.**

## ER Diagram
```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOG : generates
    USERS ||--o{ SAVED_REPORTS : creates
    USERS {
        int id PK
        string username
        string password_hash
        string role
        boolean is_active
    }
    AUDIT_LOG {
        int id PK
        int user_id FK
        string action
        json details
    }
    RECOMMENDATIONS {
        int id PK
        string route_id
        string action
        json reason
        string priority
        string status
    }
    MODEL_REGISTRY {
        int id PK
        string model_name
        string pipeline
        int version
        json metrics
    }
    SAVED_REPORTS {
        int id PK
        string report_type
        int generated_by FK
        string file_path
    }
```

## Security
- Passwords hashed with `bcrypt`.
- JWT Tokens signed with `HS256` secret logic.
- Audit table is append-only.

## Backup Approach (Production)
In a real deployment (e.g. Render/Railway), PostgreSQL automated daily backups should be enabled via `pg_dump`, retaining 7-14 days of snapshots.
