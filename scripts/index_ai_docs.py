import os
import glob
import psycopg2
from openai import OpenAI

client = OpenAI()

DB = psycopg2.connect(
    dbname="ai_knowledge",
    user="ai_knowledge",
    password="ai_knowledge",
    host="localhost",
    port=5432
)

def chunk_text(text, size=1200, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def embed(text):
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding

def main():
    files = glob.glob("docs/ai/**/*.md", recursive=True)

    with DB.cursor() as cur:
        for path in files:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            cur.execute("DELETE FROM ai_docs WHERE file_path = %s", (path,))

            chunks = chunk_text(text)

            for i, chunk in enumerate(chunks):
                vector = embed(chunk)
                cur.execute(
                    """
                    INSERT INTO ai_docs
                    (file_path, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (path, i, chunk, vector)
                )

        DB.commit()

if __name__ == "__main__":
    main()