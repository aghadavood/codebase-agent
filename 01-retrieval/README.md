# 01.07.2026 -01 — Retrieval (RAG)

Point the system at a code repo and ask a question about it. This layer finds the
few pieces of code that actually answer the question, and hands only those to the
model — instead of stuffing the whole repo into one prompt (that was Layer 0, and
it hit the token wall).

The pipeline, start to end:

**chunk → embed → store → search → rerank → answer**

---

## What each step does

**1. Chunk — cut the code into meaningful pieces (`chunk_by_ast.py`)**

You can't embed a whole file at once, so you split it. But *how* you split matters.
Cutting every 50 lines slices through the middle of functions — one chunk ends up
holding fragments of several unrelated things, and its meaning turns to mush.

The fix: split on the code's real structure, not on line count. Python parses code
into a syntax tree (AST) that knows where each function and class begins and ends.
So we walk that tree, take each function/class as its own clean chunk, and gather
the leftover lines (imports, constants, the `__main__` block) into their own chunks
so nothing is lost. One chunk = one complete idea.

**2. Embed — turn each chunk into numbers (`shared/embeddings.py`)**

An embedding model converts text into a vector — a list of numbers that captures
meaning. Two things that *mean* the same get similar numbers, even if they use
different words.

One rule that silently wrecks accuracy if you get it wrong: this model has two
modes. Use `passage` mode when embedding code chunks, and `query` mode when
embedding the user's question. Same model for both, different mode.

**3. Store — keep each chunk next to its vector**

Every chunk is stored paired with its vector. For learning, this is just a plain
Python list in memory — no external vector database yet. The cosine-similarity math
was written by hand first (four lines) to understand it, then swapped for FAISS and
confirmed to give identical results. Now FAISS isn't magic — it's a fast version of
math I already understand.

**4. Search — find the closest chunks by meaning**

Turn the question into a vector too, then measure which chunk vectors point in the
most similar direction (cosine similarity). Take the top few. This is *semantic*
search: it matches meaning, not exact words.

**5 & 6. Sharpen the search — hybrid + rerank (`hybrid.py`, `shared/rerank.py`)**

Semantic search alone is humble: the right answer often wins only barely, and it's
fuzzy on exact names (ask for `build_index` and it might hand back `build_store`).
Two additions fix this:

- **Hybrid search** runs semantic search *and* BM25 (a keyword scorer that catches
  exact names, rare words, and error strings — the stuff embeddings smear together).
  The two score lists are merged so a chunk that wins on *either* rises to the top.

- **Reranking** is the final judge. Semantic and BM25 score the query and chunk
  *separately*; a reranker (cross-encoder) reads them *together* in one pass, so it
  can tell that `build_index` **creates** the index while `search_index` only uses
  one — a distinction the separate scorers structurally can't see. It's slow, so it
  runs only on the top ~10 candidates from hybrid, then re-sorts to the top 3.

The pattern is **wide then narrow**: hybrid casts a wide net (recall), the reranker
picks the keepers (precision). Never trim before reranking — the reranker can only
re-order what it's handed.

**7. Answer**

The final chunks go to a small, fast chat model with one instruction: explain in
plain words using only this code, don't just repeat it back. The retrieved code is
the context the model reasons over. That's RAG.

---

## Models used

All via NVIDIA NIM, one API key, OpenAI-compatible.

| Job | Model | Why |
|-----|-------|-----|
| Embedding | `nvidia/nv-embedqa-e5-v5` | 1024-dim; needs `passage`/`query` mode |
| Rerank | `nv-rerank-qa-mistral-4b:1` | hosted cross-encoder, free, no GPU |
| Chat | `meta/llama-3.1-8b-instruct` | small + fast; summarizing is an easy job |

**Match the model size to the job.** An early version used a 122B model just to
write a short summary — it queued 200+ seconds on the free tier. The hard part
(finding the code) is already done by search; summarizing is easy, so a small model
does it in under a second. The big model is saved for later layers, where the model
has to make real decisions.

---

## The main lessons (full stories in `LOG.md`)

- **Line-count chunking breaks meaning.** Split on code structure (AST), not on a
  fixed number of lines.
- **Ranking is trustworthy, absolute scores are not.** Semantic scores cluster
  tightly (0.38 vs 0.34) — the right answer wins, but barely. That weak margin is
  what motivated hybrid and rerank.
- **Averaging two weak scorers is compromise, not arbitration.** It can land farther
  from the truth than either alone. Don't blend harder — add a better judge.
- **A model on the catalog page isn't always a callable API.** Check for an
  `invoke_url`, not just a model card. (404 = wrong/missing URL; 410 = permanently
  retired.)
- **Finding the right code isn't enough** — you have to tell the model what to do
  with it. One added instruction turned a copy-paste answer into a real explanation.

---

## Known gaps (future work)

Ranked by practical impact.

- **No persistence — re-embeds the whole repo on every run.** Storage is an
  in-memory Python list, so nothing is saved between runs and large repos pay the
  full embedding cost each time. *Fix: a local vector DB (Chroma) — embed once,
  save to disk, reuse.* Chroma is the planned fix; 
  deliberately deferred to keep Layer 2 on-roadmap and because Layer 3's access pattern should shape the storage design.
- **Python-only.** Chunking uses Python's AST, so other languages aren't parsed.
  A clean v1 boundary, not a bug. *Fix: add parsers for other languages (e.g.
  tree-sitter) using the same walk-the-tree approach.*
- **Nested functions can be duplicated across chunks.** A minor correctness edge
  case — adds a little retrieval noise, rarely changes the answer. Polish item.