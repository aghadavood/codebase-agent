# codebase-agent

Building a codebase agent from scratch, one step at a time — and documenting
**every failure** along the way. Point it at a code project; by the end it can
answer questions about the code and act on it.

This is **one project in one repo**. Each numbered folder is a *step* that builds
on the one before it. I'm learning in public: build it → watch it break →
figure out why → fix it → write down the lesson. The failures are the point.

## The steps

Each folder below is one stage of the same evolving project . They go in order; each reuses what the last one built.

| Folder | What this step adds | source
|--------|---------------------|
| `00-foundations` | naive version: stuff a whole project into one prompt (breaks on real repos) | --
| `01-retrieval` | retrieve only the relevant chunks instead of everything (RAG) | https://weaviate.io/blog/introduction-to-rag
| `02-workflows` | fixed multi-step pipelines (chaining, routing, evaluate-and-improve) | 
| `03-agent-loop` | let the model decide which tools to call, in a loop | 
| `04-tools-aci` | make the tools reliable; add a tool that *acts* on the code |
| `05-mcp` | expose the tools over MCP so other apps (like Cursor) can use them | https://modelcontextprotocol.io/docs/getting-started/intro
| `06-memory` | give it memory that persists across sessions |
| `07-evals` | measure it — prove each step actually improved things |

_Currently done: `00-foundations`._

Each folder has its own `README` and a `LOG` with the failure story for that step.

## Why a codebase agent

Developer tooling is where applied-AI demand and depth both point. This project
exercises the three skills that get you hired or paid: retrieval on messy real
data (step 1), reliable tool design (steps 3–4), and evaluation (step 7).

## Running it

The model lives in one place — `shared/llm.py` — so the whole project uses the
same model and swapping it is a one-line change. It currently uses a free
NVIDIA NIM endpoint (OpenAI-compatible).

```bash
pip install openai
# free key from build.nvidia.com  (starts with nvapi-)
$env:NVIDIA_API_KEY="your-key-here"   # PowerShell

cd 00-foundations
python ask_the_repo.py C:\path\to\some\project "What does this do?"
```

## The full plan

The detailed step-by-step roadmap (what to build, what failure to expect, what
to read) lives in [`ROADMAP.md`](ROADMAP.md).

## Sources I'm learning from

- Anthropic, *Building Effective Agents* — https://www.anthropic.com/engineering/building-effective-agents
- Model Context Protocol — https://modelcontextprotocol.io/docs/getting-started/intro