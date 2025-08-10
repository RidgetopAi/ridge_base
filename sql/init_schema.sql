-- sql/init_schema.sql
-- Ridge Base CLI Database Schema

CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    command TEXT NOT NULL,
    context_snapshot TEXT, --JSON blob of content
    response TEXT
);

CREATE TABLE IF NOT EXISTS decisions (
    id SERIAL PRIMARY KEY, 
    project_id INTEGER REFERENCES projects(project_id),
    category VARCHAR(100),  --tech_choice, design_decision, etc.
    decisions TEXT NOT NULL,
    reasoning TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS files_tracked (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id),
    path TEXT NOT NULL,
    hash VARCHAR(32),  -- MD5 hash for change detection
    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    insights TEXT  -- JSON blob of analysis results
);

CREATE TABLE IF NOT EXISTS checkpoints (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id),
    message_id INTEGER,  -- Reference to conversation
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_conversations_project_time ON conversations(project_id, timestamp);
CREATE INDEX idx_files_project_path ON files_tracked(project_id, path);
CREATE INDEX idx_decisions_project_category ON decisions(project_id, category);