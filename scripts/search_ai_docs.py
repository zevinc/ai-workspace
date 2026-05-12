import sys
import psycopg2
from openai import OpenAI

client = OpenAI()

query = " ".join(sys.argv[1:])

def embed(text):
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding

DB = psycopg2.connect(
    dbname="ai_knowledge",
    user="ai",
    password="ai123456",
    host="localhost",
    port=5432
)

qvec = embed(query)

with DB.cursor() as cur:
    cur.execute(
        """
        SELECT file_path, content, 1 - (embedding <=> %s::vector) AS score
        FROM ai_docs
        ORDER BY embedding <=> %s::vector
        LIMIT 5
        """,
        (qvec, qvec)
    )

    for row in cur.fetchall():
        print("\n---")
        print("file:", row[0])
        print("score:", row[2])
        print(row[1][:800])