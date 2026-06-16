r"""
ask-the-repo  —  Layer 0 (Foundations)

The deliberately dumb version: read every source file in a repo, stuff it ALL
into a single prompt, and ask Gemma a question about it.

No retrieval. No chunking. No cleverness. The whole point is to make the
context-window failure VISIBLE so you feel why Layer 1 (retrieval) exists.

Setup:
    pip install openai
    # free key from https://aistudio.google.com
    $env:GEMINI_API_KEY="your-key-here"      # PowerShell

Usage:
    python ask_the_repo.py C:\path\to\some\repo "What does the entry point do?"

Try it twice:
    1) A TINY repo (a few files). It works.
    2) A REAL repo. Watch the token count climb; on a big one the call slows,
       gets expensive, or fails. That failure is the lesson — write it in README.
"""

import sys
from pathlib import Path

# Import the shared model client (one folder up, in shared/).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from llm import chat, MODEL  # noqa: E402

# --- config -----------------------------------------------------------------

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist",
             "build", ".next", ".idea", ".vscode", "target"}
SOURCE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
               ".rb", ".c", ".h", ".cpp", ".cs", ".md", ".txt", ".json",
               ".toml", ".yaml", ".yml"}


# --- the dumb core ----------------------------------------------------------

def collect_repo_text(repo_path: Path) -> str:
    """Walk the repo and concatenate every source file into one big string.

    The naive thing: zero attempt to select what's relevant.
    """
    chunks = []
    for path in sorted(repo_path.rglob("*")):
        if path.is_dir():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in SOURCE_EXTS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = path.relative_to(repo_path)
        chunks.append(f"\n\n===== FILE: {rel} =====\n{text}")
    return "".join(chunks)


def rough_token_estimate(text: str) -> int:
    """Crude heuristic: ~4 characters per token. Enough to SEE trouble coming.

    The real count comes back from the API in `usage`, which we also print.
    """
    return len(text) // 4


# --- entry point ------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print('Usage: python ask_the_repo.py C:\\path\\to\\repo "your question"')
        sys.exit(1)

    repo_path = Path(sys.argv[1]).expanduser().resolve()
    question = sys.argv[2]

    if not repo_path.is_dir():
        print(f"Not a directory: {repo_path}")
        sys.exit(1)

    print(f"Reading repo: {repo_path}")
    repo_text = collect_repo_text(repo_path)

    est = rough_token_estimate(repo_text)
    print(f"Collected {len(repo_text):,} characters  (~{est:,} tokens, rough estimate)")
    print(f"Model: {MODEL}")
    print("-" * 60)

    prompt = (
        "You are given the full source of a code repository below.\n"
        "Answer the question using only what you can see.\n\n"
        f"{repo_text}\n\n"
        f"QUESTION: {question}\n"
    )

    # This is where it breaks on a big repo. We catch the error on purpose so
    # the failure is legible — the failure IS the point of Layer 0.
    try:
        answer, usage = chat(prompt, max_tokens=1024)
    except Exception as e:
        print("CALL FAILED. This is the Layer 0 lesson, not a bug to hide.")
        print(f"Error: {type(e).__name__}: {e}")
        print()
        print("Likely causes when this happens on a real repo:")
        print("  - the prompt exceeded the model's context window, OR")
        print("  - you hit the free-tier rate limit (too many tokens too fast).")
        print()
        print("Either way the lesson holds: stuffing the ENTIRE repo into one")
        print("call does not scale. That's exactly why Layer 1 (retrieval) exists")
        print("— fetch only the chunks relevant to the question.")
        sys.exit(2)

    print("ANSWER:\n")
    print(answer)
    print()
    print("-" * 60)
    print(f"Real token usage  ->  input: {usage.prompt_tokens:,}   "
          f"output: {usage.completion_tokens:,}")
    print("Note how big the input is. Now point this at a bigger repo and watch it grow.")


if __name__ == "__main__":
    main()
