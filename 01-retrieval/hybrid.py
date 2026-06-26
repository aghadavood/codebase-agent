import math
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from retrieve import semantic_score_all  # noqa: E402

K1 = 1.5
B = 0.75


def tokenize(text: str) -> list[str]:
    """Split code into lowercase word-tokens for keyword matching.

    Underscores and punctuation act as splitters, so `build_index(store)`
    becomes ['build', 'index', 'store'] — the words BM25 will count.
    """
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25Index:
    """Keyword index — scores chunks by how often query words appear in them."""

    def __init__(self, chunks: list[str]):
        self.chunks = chunks
        self.tokenized = [tokenize(text) for text in chunks]
        self.doc_lens = [len(tokens) for tokens in self.tokenized]
        self.n_docs = len(chunks)
        self.avgdl = sum(self.doc_lens) / self.n_docs if self.n_docs else 0.0

        self.df: dict[str, int] = {}
        for tokens in self.tokenized:
            for term in set(tokens):
                self.df[term] = self.df.get(term, 0) + 1

    def _idf(self, term: str) -> float:
        df = self.df.get(term, 0)
        return math.log((self.n_docs - df + 0.5) / (df + 0.5) + 1)

    def score(self, query: str) -> list[tuple[float, str]]:
        query_terms = set(tokenize(query))
        scored: list[tuple[float, str]] = []

        for i, tokens in enumerate(self.tokenized):
            term_counts = Counter(tokens)
            doc_len = self.doc_lens[i]
            total = 0.0

            for term in query_terms:
                freq = term_counts.get(term, 0)
                if freq == 0:
                    continue
                idf = self._idf(term)
                denom = freq + K1 * (1 - B + B * doc_len / self.avgdl)
                total += idf * (freq * (K1 + 1)) / denom

            scored.append((total, self.chunks[i]))

        return scored


def build_bm25(chunks: list[str]) -> BM25Index:
    return BM25Index(chunks)


def bm25_search(query: str, index: BM25Index, k: int) -> list[tuple[float, str]]:
    """Top-k, sorted (score, text) — standalone."""
    scored = list(zip(bm25_score_all(query, index), index.chunks))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:k]


def bm25_score_all(query: str, index: BM25Index) -> list[float]:
    """All chunks, store order — merge ingredient."""
    return [score for score, _ in index.score(query)]


def min_max(scores: list[float]) -> list[float]:
    """Scale a list of scores into the 0–1 range so two scorers compare fairly.

    If every score is identical (max == min), there's no spread to scale,
    so return all zeros instead of dividing by zero.
    """
    lo = min(scores)
    hi = max(scores)
    if hi == lo:
        return [0.0] * len(scores)
    return [(s - lo) / (hi - lo) for s in scores]


def hybrid_search(
    query: str,
    store: list[dict],
    bm25_index: BM25Index,
    k: int,
    alpha: float = 0.5,
) -> list[tuple[float, str]]:
    """Combine semantic + BM25 into one ranking.

    1. score ALL chunks on both searchers (store order)
    2. min-max each to 0–1 so they compare fairly
    3. blend per chunk: alpha * semantic + (1 - alpha) * bm25
    4. pair with text, sort, return top-k
    """
    semantic = min_max(semantic_score_all(query, store))
    bm25 = min_max(bm25_score_all(query, bm25_index))
    blended = [
        alpha * s + (1 - alpha) * b for s, b in zip(semantic, bm25)
    ]
    scored = list(zip(blended, (item["text"] for item in store)))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from chunk_by_ast import chunk_by_ast
    from retrieve import build_store

    target = Path(__file__).resolve().parent / "retrieve.py"
    with open(target, encoding="utf-8") as f:
        chunks = chunk_by_ast(f.read())

    store = build_store(chunks)
    bm25_index = build_bm25([item["text"] for item in store])

    queries = (
        "build_index",
        "create the faiss search structure",
    )
    for query in queries:
        print(f"\n=== query: {query!r} ===")
        for alpha in (1.0, 0.0, 0.5):
            print(f"\n--- alpha={alpha} ---")
            for score, text in hybrid_search(query, store, bm25_index, k=3, alpha=alpha):
                print(f"{score:.3f}  {text.strip().splitlines()[0][:60]}")