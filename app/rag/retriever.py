import os
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

EMBED_MODEL = "models/embedding-001"

DATA_PATH = "data/rag_sources/delhi.txt"


def load_document():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text, chunk_size=500):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks


def embed_text(text):
    response = genai.embed_content(
        model=EMBED_MODEL,
        content=text
    )
    return np.array(response["embedding"])


def build_embeddings():

    text = load_document()
    chunks = chunk_text(text)

    embeddings = []
    for chunk in chunks:
        vector = embed_text(chunk)
        embeddings.append(vector)

    return chunks, embeddings


# Build once at startup
CHUNKS, EMBEDDINGS = build_embeddings()


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve(query, top_k=2):

    query_vector = embed_text(query)

    similarities = []
    for idx, emb in enumerate(EMBEDDINGS):
        score = cosine_similarity(query_vector, emb)
        similarities.append((score, idx))

    similarities.sort(reverse=True)

    top_chunks = [CHUNKS[idx] for (_, idx) in similarities[:top_k]]

    return top_chunks