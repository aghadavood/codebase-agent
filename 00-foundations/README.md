# Layer 0 — Foundations: `ask-the-repo`

The deliberately dumb version of a codebase agent. It reads **every** source
file in a repo, stuffs it **all** into one prompt, and asks Gemma a question.

No retrieval. No chunking. That's intentional — this layer exists to make the
context-window wall something you *feel*, not just read about.

## Run it

```bash
pip install openai
# free key from https://aistudio.google.com  ("Get API key")
# PowerShell:
$env:GEMINI_API_KEY="your-key-here"

# 1) A tiny repo — this works:
python ask_the_repo.py C:\path\to\tiny\repo "What does the entry point do?"

# 2) A real repo — watch this strain or break:
python ask_the_repo.py C:\path\to\real\project "Where is auth handled?"
```

Uses **Gemma 4** (`gemma-4-31b-it`) through Google AI Studio's free,
OpenAI-compatible API. The model is set in `shared/llm.py` — change one line
there to swap it for any other model later.

## What you should observe

- On a small repo it answers fine and prints the real input token count.
- On a real repo the input balloons. Depending on size you'll see one of:
  the answer gets slow, the free-tier **rate limit** trips, or the prompt
  exceeds the **context window** and the call fails. The script catches errors
  on purpose and explains them, because the failure is the whole point.

## The failure write-up (fill this in after you run it — this is the valuable part)

> **What I expected:** _______
>
> **What actually happened:** the input hit ~______ tokens on `<repo>` and the
> call failed / got truncated / got slow + expensive.
>
> **Why:** the context window is a fixed, scarce budget. "Put everything in the
> prompt" does not scale — cost and latency rise with every token, and past a
> limit the call just fails. You cannot fit a real codebase in one prompt.
>
> **What this motivates:** Layer 1 — retrieval. Instead of sending everything,
> fetch only the chunks relevant to the question. That's RAG, and the rest of
> this repo is built on it.

## What this layer taught me

- [ ] How tool/text gets tokenized (~4 chars/token rule of thumb)
- [ ] The context window as a budget, not free space
- [ ] How to make a raw Claude API call and read `usage`
- [ ] Why "stuff it all in the prompt" is a dead end at real scale

## Commit message suggestion

```
Layer 0: naive whole-repo-in-one-prompt agent (works small, breaks real)
```

##change the model, Gemma was too little so i changed to 

MODEL = "qwen/qwen3.5-122b-a10b" from nvidia.

now it works very better.