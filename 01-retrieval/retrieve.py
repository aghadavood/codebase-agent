import sys
import time
from pathlib import Path
from chunk_by_ast import chunk_by_ast
import faiss
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.embeddings import embed, embed_batch  # noqa: E402
from shared.llm import chat  # noqa: E402

VECTOR_DIM = 1024


def build_store(chunks: list[str]) -> list[dict]:
    """Embed each chunk as passage and pair text with its vector."""
    vectors = embed_batch(chunks, "passage")
    return [{"text": text, "vector": vector} for text, vector in zip(chunks, vectors)]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    return dot / (norm_a * norm_b)


def semantic_score_all(query: str, store: list[dict]) -> list[float]:
    """Score every chunk by cosine similarity; return floats in store order."""
    qvec = embed(query, "query")
    return [cosine(qvec, item["vector"]) for item in store]


def search(query: str, store: list[dict], k: int) -> list[tuple[float, str]]:
    """Embed query as query, return top-k (score, text) pairs by cosine similarity."""
    qvec = embed(query, "query")
    scored = [(cosine(qvec, item["vector"]), item["text"]) for item in store]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:k]


def build_index(store: list[dict]) -> faiss.IndexFlatIP:
    arr = np.array([item["vector"] for item in store], dtype="float32")
    faiss.normalize_L2(arr)
    index = faiss.IndexFlatIP(VECTOR_DIM)
    index.add(arr)
    return index


def search_index(
    query: str, index: faiss.IndexFlatIP, store: list[dict], k: int
) -> list[tuple[float, str]]:
    q = np.array([embed(query, "query")], dtype="float32")
    faiss.normalize_L2(q)
    scores, idx = index.search(q, k)
    return [
        (float(score), store[i]["text"])
        for score, i in zip(scores[0], idx[0])
        if i >= 0
    ]


def answer(
    query: str, store: list[dict], index: faiss.IndexFlatIP, k: int = 5
) -> str:
    hits = search_index(query, index, store, k)
    code_block = "\n\n".join(
        f"--- chunk {i + 1} ---\n{text}" for i, (_, text) in enumerate(hits)
    )
    prompt = (
        "You are a code assistant. Using only the code in <context>, "
        "answer the question in plain prose. Do NOT reproduce the code; "
        "explain what it does.\n\n"
        f"<context>\n{code_block}\n</context>\n\n"
        f"Question: {query}"
    )
    text, _usage = chat(prompt)
    return text


if __name__ == "__main__":

    # 1. read a real file and chunk it
    target = "../00-foundations/ask_the_repo.py"
    with open(target, encoding="utf-8") as f:
        chunks = chunk_by_ast(f.read())
    print(f"{len(chunks)} chunks\n")

    # 2. build store + index (one batched embed call)
    t = time.time()
    store = build_store(chunks)
    print(f"embed: {time.time() - t:.1f}s")

    t = time.time()
    index = build_index(store)
    print(f"index: {time.time() - t:.1f}s")

    # 3. ask
    question = "What does the entry point do?"
    print(f"\nQ: {question}\n")
    t = time.time()
    out = answer(question, store, index, k=3)
    print(f"answer: {time.time() - t:.1f}s")
    print("\nA:", out)