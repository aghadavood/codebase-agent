# Building a Codebase Agent — Layer-by-Layer Learning Journey

> One repo. One evolving system. Each layer is a weekend project that **builds on the last one's output**.
> The whole point: build it, watch it fail, document *why*, then fix it. The failures are the portfolio.

**Stack:** Python core, TypeScript only for any UI.
**Through-line:** A "codebase agent" — point it at a Git repo, it answers questions about the code, then learns to *act* on it (fix issues, open PRs). By the end you've built a tiny open version of what Cursor does.

**Why this domain:** developer tooling is the hottest paid niche in applied AI, you already have intuition for it, and "I built a mini coding agent and documented every failure" is a strong repo headline. The three skills employers actually pay for — retrieval on messy real data, reliable tool/ACI design, and evals/observability — all get exercised here.

---

## Repo structure

```
codebase-agent/
├── README.md            ← the journey: one section per layer, with the "it broke because…" story
├── 00-foundations/
├── 01-retrieval/
├── 02-workflows/
├── 03-agent-loop/
├── 04-tools-aci/
├── 05-mcp/
├── 06-memory/
├── 07-evals/
└── shared/              ← reused across layers (LLM client, repo loader, config)
```

Each layer folder gets its own `README.md` with: what you built, the failure you hit, the fix, and what you'd do differently. **That per-layer failure write-up is the most valuable thing in the repo** — almost nobody documents it.

---

## Layer 0 — Foundations
**Project: `ask-the-repo` (the dumbest possible version)**

Build a script that stuffs an entire small repo's source into one LLM prompt and answers a question about it. No retrieval, no chunking — just `read all files → one big prompt → answer`.

- **Build:** CLI that takes a repo path + a question, concatenates files, calls the model, prints the answer.
- **Watch it fail:** it works on a 5-file repo and then blows past the context window on anything real. Log the token count each run so the failure is *visible*.
- **Figure out why:** the context window is a scarce budget. This failure is the entire motivation for Layer 1. Write that down in the layer README.
- **Skills demonstrated:** tokenization, context-window economics, raw API calls, structured tool-use basics.

---

## Layer 1 — Retrieval (RAG)
**Project: `repo-qa` — chat with the codebase**

Replace "stuff everything" with "retrieve only the relevant chunks." This is the single most in-demand applied-AI skill, so spend real time here.

- **Build:** chunk the repo (by function/class, not blind 500-char splits), embed chunks, store in a vector DB (Chroma or Qdrant locally), retrieve top-k for a query, answer from those.
- **Watch it fail:** ask something where the answer spans files, or where naive chunking split a function in half. Recall drops; the answer is confidently wrong.
- **Figure out why → the fixes that matter:**
  - smarter chunking (respect code structure)
  - **hybrid search** (dense embeddings + BM25 keyword)
  - **reranking** the retrieved set before it hits the prompt
  - measure **recall@k** before and after each fix — put the numbers in the README
- **Reuse:** this retriever becomes a *tool* the agent calls in Layer 3.
- **Skills demonstrated:** embeddings, chunking strategy, hybrid search, reranking, retrieval evaluation. This is the "I can make RAG work on messy real data" proof.
- **Orientation reading:** the Weaviate RAG / agentic-RAG blog intros (fine for framing; the depth above is what separates you from beginners).

---

## Layer 2 — The augmented LLM & workflows (NOT agents yet)
**Project: `repo-pipeline` — a fixed multi-step workflow**

Before any autonomy, build a *predefined code path*. Anthropic's core lesson: the most successful implementations use simple composable patterns, not frameworks; start with LLM APIs directly and only add complexity when it demonstrably helps.

- **Build** one concrete workflow using these patterns in order of complexity:
  - **Prompt chaining:** summarize a file → extract its public API → generate docstrings.
  - **Routing:** classify an incoming question (architecture? bug? usage?) and send each type to a specialized prompt.
  - **Parallelization (sectioning):** review a file for bugs, style, and security in three parallel calls, aggregate.
  - **Evaluator-optimizer:** generate a docstring, have a second call critique it, loop until it passes.
- **Watch it fail:** routing misclassifies edge cases; the evaluator loops forever with no stop condition.
- **Figure out why:** workflows are predictable but rigid — they break on inputs you didn't foresee. That rigidity is the motivation for Layer 3's autonomy. Add stop conditions and gates.
- **Key principle to internalize:** do NOT reach for LangGraph yet. Implement these raw, in a few lines each. Pick up a framework later as convenience, not foundation — incorrect assumptions about a framework's internals are a common source of bugs.
- **Skills demonstrated:** the five canonical patterns, knowing workflow-vs-agent, restraint.
- **Source:** Anthropic, *Building Effective Agents* — `anthropic.com/engineering/building-effective-agents` (the screenshot's `/research/build…` link redirects here). Reference code: Anthropic cookbook, `patterns/agents`.

---

## Layer 3 — The agent loop
**Project: `repo-agent` — let it decide**

Now make it an agent: an LLM using tools in a loop based on environmental feedback. Give it the Layer 1 retriever and a file-reader as tools, and let *it* decide what to call.

- **Build:** a loop — model picks a tool → you execute it → feed the result back → repeat until done or a max-iteration cap. Tools: `search_code` (your retriever), `read_file`, `list_files`.
- **Watch it fail:** infinite loops, hallucinated tool arguments, the agent "answering" without actually calling a tool, runaway cost.
- **Figure out why:** autonomy trades latency/cost for flexibility and can compound errors. Add: max-iteration stops, input validation on tool args, logging of every step (transparency).
- **Decision to document:** when is multi-agent worth it? Mostly **not** — only the orchestrator-workers case (you can't predict the subtasks). Default to one agent with good tools. Write your reasoning in the README; this is exactly the question a strong interviewer asks.
- **Skills demonstrated:** the agent loop, stop conditions, error recovery, cost control.

---

## Layer 4 — Tools & the agent-computer interface (ACI)
**Project: `repo-agent-v2` — make the tools bulletproof**

The highest-leverage layer and the one most tutorials skip. Anthropic spent *more* time optimizing tools than prompts on SWE-bench. Treat tool design as seriously as UI design.

- **Build:** give the agent an *acting* tool — `apply_edit` or `run_tests` — and harden every tool's interface.
- **Watch it fail:** the classic — relative file paths break once the agent changes directory; ambiguous params get misused; the model can't tell two similar tools apart.
- **Figure out why → the fixes:**
  - require **absolute paths** (Anthropic's exact fix — the model then used it flawlessly)
  - write tool descriptions like docstrings for a junior dev: example usage, edge cases, clear boundaries
  - **poka-yoke** the args — design them so mistakes are *hard to make*
  - test many inputs, log the mistakes, iterate on the tool spec
- **Skills demonstrated:** ACI design, reliable tool-calling — a genuine differentiator, since most self-taught people never learn it.
- **Source:** *Building Effective Agents*, Appendix 2 ("Prompt engineering your tools").

---

## Layer 5 — MCP
**Project: `repo-mcp-server` — standardize the tools**

Wrap your tools in the Model Context Protocol so any MCP client (including Cursor itself) can use them. This is where your project becomes interoperable — and demoable.

- **Build:** an MCP server exposing `search_code`, `read_file`, `apply_edit` using the official **Python SDK** (`modelcontextprotocol/python-sdk`). Then connect it to a real client — **Cursor is itself an MCP client**, so you can literally plug your server into your own editor.
- **Watch it fail:** transport/schema mismatches, auth, the client not discovering your tools.
- **Figure out why:** MCP is JSON-RPC with a strict client-server contract (tools, resources, prompts). Read the spec for the message types.
- **Demo value:** "my custom code tools running inside Cursor" is a screenshot-worthy README moment.
- **Skills demonstrated:** MCP server authoring, interoperability, the client-server model.
- **Source:** `modelcontextprotocol.io/docs/getting-started/intro` (current spec: 2025-06-18). SDKs: `modelcontextprotocol/python-sdk`, `modelcontextprotocol/typescript-sdk`.

---

## Layer 6 — Memory
**Project: `repo-agent-memory` — make it remember**

Give the agent persistent memory across sessions so it recalls past questions, decisions, and the repo's quirks.

- **Build:** add a memory layer (try Letta, or roll a simple store first to understand the problem). Decide what's worth *persisting* vs. what should be *re-retrieved* each time.
- **Watch it fail:** memory bloat (everything saved, nothing useful), stale facts after the code changes, retrieval of irrelevant old context that poisons answers.
- **Figure out why:** memory is a curation problem, not a storage problem. Persist decisions and durable facts; re-retrieve volatile things (current file contents). Document your policy.
- **Skills demonstrated:** memory architecture, the persist-vs-retrieve tradeoff.
- **Source:** `letta.com`.

---

## Layer 7 — Evals & observability
**Project: `repo-agent-evals` — prove it works**

Woven through every layer in spirit, but now make it formal. Almost nobody self-taught has this, so it's your strongest hiring signal.

- **Build:** a test set of repo questions + expected outcomes; an eval harness scoring accuracy/recall; tracing on every agent run (LangSmith is one option — the *concept* matters more than the tool). Run the eval against your Layer 1 vs Layer 4 agent to show measurable improvement.
- **Watch it fail:** you discover a "fix" from an earlier layer actually made things worse on some inputs — which you only know *because* you now measure.
- **Figure out why:** this is the whole method — measure, iterate, add complexity only when it demonstrably improves outcomes. Put a before/after metrics table in the top-level README.
- **Skills demonstrated:** evals, tracing, production debugging, data-driven iteration.
- **Sources:** `docs.smith.langchain.com`; for context engineering, search arXiv for a current "Context Engineering" survey (several exist — cite the specific one you use).

---

## How to present the journey on GitHub

1. **Top-level README = the story arc.** Open with one GIF/screenshot of the final agent working in Cursor. Then a table: each layer, what it added, and the key failure→fix. End with the before/after eval metrics.
2. **Each layer folder tells its own failure story.** "It broke because X; here's the fix; here's the lesson." This is what makes the repo memorable.
3. **Commit history is part of the portfolio** — don't squash the journey into one commit. The messy middle is the proof you actually built it.
4. **Pin the repo, write a short post** walking through the three or four most instructive failures. That post is what gets shared.

## What makes this *marketable*
By the end you can credibly say, with code to back each one:
- "I built RAG that works on messy real codebases and measured recall improvements." (Layer 1)
- "I designed reliable agent tools / ACI and can explain why agents fail." (Layers 3–4)
- "I built MCP servers that run in real clients." (Layer 5)
- "I evaluate and trace agent systems in production terms." (Layer 7)

Those four sentences are the job description for applied-AI engineering roles right now.
