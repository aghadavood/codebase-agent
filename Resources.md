Layer 0 — Foundations (done)

##Layer 1 — Retrieval (RAG)

Read the introduction-to-RAG piece first (the basic RAG concept — embeddings + vector DB + retrieval), then the Weaviate "What is Agentic RAG" page you sent. For Layer 1, only read the first third of the agentic-RAG page — the "Fundamentals" and "What is RAG" sections that explain a naive pipeline: a retrieval component (an embedding model and a vector database) plus a generative component (an LLM), where the query runs a similarity search to retrieve the most similar documents and give the LLM extra context. Skip the multi-agent and framework sections for now — those are Layer 3 material. Your goal for Layer 1: understand embeddings, chunking, and top-k retrieval. The page also flags the exact failure you'll hit: naive RAG is one-shot — context is retrieved once, with no reasoning or validation over its quality. PyPIPyPI
##Layer 2 — Workflows

Read Anthropic's "Building Effective Agents" (anthropic.com/engineering/building-effective-agents) — specifically the workflows section (prompt chaining, routing, parallelization, evaluator-optimizer) and the augmented-LLM building block. This is the core source. The resources.anthropic.com/building-effective-ai-agents link is the same material in a companion/cookbook format — use it for the reference code. Skip the agent section until Layer 3.
##Layer 3 — Agent loop

Same Anthropic doc, now the agents section (the LLM-using-tools-in-a-loop part). Then go back to the Weaviate page and read the parts you skipped — single-agent router, multi-agent, and especially the ReAct framework: ReAct = Reason + Act — the agent reasons about the next action, executes it (e.g. a tool), observes the feedback, and iterates until the task is done. That loop is what you're building in Layer 3. PyPI
##Layer 4 — Tools / ACI

Same Anthropic doc, Appendix 2 ("Prompt engineering your tools"). That's the whole reading — it's short and it's the highest-leverage content in the roadmap.
The LangGraph doc (docs.langchain.com/oss/python/langgraph) fits here too as optional reading — read it to understand what a framework gives you, but per Anthropic's own advice, build Layers 2–3 raw first. Treat LangGraph as "see how a framework expresses the loop you already built by hand," not as the foundation.
##Layer 5 — MCP

Read modelcontextprotocol.io/docs/getting-started/intro — the "getting started" and core-concepts (tools, resources, prompts) sections, plus the Python SDK quickstart. Skip the deep protocol/transport spec until something breaks.
##Layer 6 — Memory

Read letta.com docs — focus on the memory concepts (short-term vs long-term, what gets persisted). The Weaviate page frames the idea: AI agents use memory, both short-term and long-term, to plan, act, and adapt. Your Layer 6 job is deciding what's worth keeping vs re-retrieving. PyPI
##Layer 7 — Evals & observability

# Reading List — one source per layer

Read **per layer, not all at once.** The build-break-fix loop only works if the
reading lands *after* you've felt the problem. You're on Layer 1 — read only the
RAG material now; the rest is wasted until you get there.

---

## Layer 0 — Foundations  ✅ done
No reading needed. You already lived the lesson (the whole-repo prompt hit the
token wall). Move on.

---

## Layer 1 — Retrieval (RAG)
**Read:**
- Intro to RAG: https://weaviate.io/blog/introduction-to-rag
- Then the FIRST THIRD of: https://weaviate.io/blog/what-is-agentic-rag
  (the "Fundamentals" + "What is RAG" sections only)

**Focus on:** embeddings, chunking, vector database, top-k retrieval.
A naive pipeline = embedding model + vector DB + LLM; the query runs a
similarity search to fetch the most relevant chunks as extra context.

**Skip for now:** the multi-agent and framework sections (that's Layer 3).

**Practical companion (when you're writing the code):** Weaviate Quickstart
and their `recipes` GitHub (linked at the bottom of the agentic-RAG page).
Note: you can use a FREE local vector DB (Chroma) instead of Weaviate Cloud —
the page sells their product, but the concepts are general.

**The failure to expect:** naive RAG is one-shot — it retrieves once with no
validation. Answers go confidently wrong when chunking splits a function or the
answer spans files. Fixes: structure-aware chunking, hybrid search, reranking.
Measure recall@k before/after.

---

## Layer 2 — Workflows (NOT agents yet)
**Read:** https://www.anthropic.com/engineering/building-effective-agents
→ the **workflows** section + the "augmented LLM" building block.
Companion / reference code: https://resources.anthropic.com/building-effective-ai-agents

**Focus on:** prompt chaining, routing, parallelization, evaluator-optimizer.
Build these RAW (a few lines each), not with a framework.

**Skip for now:** the agents section (Layer 3).

---

## Layer 3 — Agent loop
**Read:**
- Same Anthropic doc → the **agents** section (LLM + tools in a loop).
- Then the parts of the Weaviate agentic-RAG page you skipped: single-agent
  router, multi-agent, and especially **ReAct** (Reason + Act: reason about the
  next action → execute a tool → observe feedback → iterate until done).

**Focus on:** the loop, stop conditions, when multi-agent is (rarely) worth it.

---

## Layer 4 — Tools / ACI
**Read:** Anthropic doc → **Appendix 2 ("Prompt engineering your tools")**.
Short, and the highest-leverage content in the whole roadmap.

**Optional:** https://docs.langchain.com/oss/python/langgraph/overview
Read it to see how a framework expresses the loop you already built by hand —
NOT as a foundation. Build raw first.

---

## Layer 5 — MCP
**Read:** https://modelcontextprotocol.io/docs/getting-started/intro
→ getting-started + core concepts (tools, resources, prompts) + Python SDK
quickstart.

**Skip for now:** the deep protocol/transport spec (read it only when something
breaks).

---

## Layer 6 — Memory
**Read:** https://www.letta.com/ docs → memory concepts (short-term vs
long-term, what gets persisted).

**Focus on:** the real question — what's worth PERSISTING vs RE-RETRIEVING each
time. Memory is a curation problem, not a storage problem.

---

## Layer 7 — Evals & observability
**Read:** https://docs.langchain.com/langsmith/observability
→ tracing + running evaluations against a test set.
Pair with: a current "Context Engineering Survey" on arXiv (search it; cite the
specific one you use).

**Focus on:** measure, then iterate. The concept matters more than the tool.
Run an eval against your Layer 1 vs later agent to show measurable improvement.

---

### Rule of thumb
- Concepts come from these sources.
- Practical "how do I write this in Python" comes from each tool's quickstart +
  example repos when you sit down to build.
- If a source is selling you a product, take the concept and use a free
  alternative (e.g. Chroma instead of Weaviate Cloud).
