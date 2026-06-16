# Layer 0 — Foundations LOG

## What I built
The dumbest possible codebase agent: read every file in a folder,
stuff it all into one prompt, send it to an AI, print the answer.

## What broke (the lesson)
- Pointed it at my .openclaw project → collected ~311,000 tokens.
- The model limit was way smaller → call rejected instantly.
- A small folder (~4,500 tokens) worked fine.

## What I learned
The context window and rate limits are a BUDGET, not free space.
You cannot stuff a whole codebase into one prompt — it doesn't scale.
That's the entire reason retrieval (RAG) exists, which is Layer 1.

## Stuff I learned the hard way (plumbing)
- Setting an API key in PowerShell ($env:...)
- Navigating folders + fixing imports when files move
- Git: init, remote, commit, push
- Always run a key-safety scan before pushing
- Read the REAL error line, not the script's guess
  (e.g. a "410 Gone" meant the model was retired, not a token limit)

## Model
Switched from Gemma to NVIDIA NIM (free) → qwen/qwen3.5-122b-a10b
(coding + tool-calling, free endpoint)

## Next
Layer 1 — retrieval. Send only the relevant chunks, not the whole folder.