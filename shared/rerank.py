"""
shared/rerank.py  —  one place that talks to the reranking model.

Every layer imports `rerank()` from here. The NVIDIA cross-encoder reads
(query, chunk) pairs together — unlike embeddings, which score query and
chunk separately. Hosted rerank lives on ai.api.nvidia.com (not integrate).
"""

import os

import requests

RERANK_MODEL = "nv-rerank-qa-mistral-4b:1"
RERANK_URL = "https://ai.api.nvidia.com/v1/retrieval/nvidia/reranking"


def rerank(query: str, chunks: list[str]) -> list[float]:
    """Score each (query, chunk) pair. Returns logits in input order — index i → score i."""
    if not chunks:
        return []

    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        raise RuntimeError(
            "Set NVIDIA_API_KEY first. Get a free key at https://developer.nvidia.com/nvidia-ai-studio\n"
            '  PowerShell:  $env:NVIDIA_API_KEY="your-key-here"'
        )

    resp = requests.post(
        RERANK_URL,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json={
            "model": RERANK_MODEL,
            "query": {"text": query},
            "passages": [{"text": text} for text in chunks],
            "truncate": "END",
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()

    scores = [0.0] * len(chunks)
    for item in data["rankings"]:
        scores[item["index"]] = float(item["logit"])
    return scores


if __name__ == "__main__":
    chunks = [
        "def search_index(query, index, store, k): ...",
        "def build_index(store):\n    arr = np.array(...)\n    faiss.normalize_L2(arr)\n    index = faiss.IndexFlatIP(1024)\n    index.add(arr)",
    ]
    query = "create the faiss search structure"
    for score, text in zip(rerank(query, chunks), chunks):
        print(f"{score:+.3f}  {text.splitlines()[0][:60]}")
