CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS ai_docs (
                                       id BIGSERIAL PRIMARY KEY,
                                       file_path TEXT NOT NULL,
                                       title TEXT,
                                       tags TEXT[],
                                       summary TEXT,
                                       chunk_index INT NOT NULL,
                                       content TEXT NOT NULL,
                                       embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
    );

CREATE INDEX IF NOT EXISTS ai_docs_embedding_idx
    ON ai_docs USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);