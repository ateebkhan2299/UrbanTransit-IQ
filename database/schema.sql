-- Database Design (Raw SQL mirror for Project Report)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    action VARCHAR NOT NULL,
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE model_registry (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR NOT NULL,
    pipeline VARCHAR NOT NULL,
    version INTEGER NOT NULL,
    trained_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metrics JSON,
    file_path VARCHAR NOT NULL
);

CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    route_id VARCHAR NOT NULL,
    action TEXT NOT NULL,
    reason JSON NOT NULL,
    priority VARCHAR NOT NULL,
    generated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR DEFAULT 'open'
);

CREATE TABLE saved_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR NOT NULL,
    generated_by INTEGER NOT NULL REFERENCES users(id),
    format VARCHAR NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR NOT NULL
);
