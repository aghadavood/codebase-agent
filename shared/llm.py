"""
shared/llm.py  —  one place that talks to the model.

Every layer imports `chat()` from here. The whole project uses Gemma 4 through
Google AI Studio's OpenAI-compatible endpoint, which means we use the standard
`openai` library and just point it at Google's URL. Swapping models later
(or providers) is a one-line change in this file — nothing else has to change.

Setup:
    pip install openai
    # get a free key at https://aistudio.google.com  ("Get API key")
    # PowerShell:
    $env:GEMINI_API_KEY=""

Why Gemma 4: it's open, free on the AI Studio tier, and good enough for the
whole learning journey. Note the free tier has low rate limits — fine for a few
calls per session, but if you ever hit "rate limit" errors, either wait a bit
or switch MODEL below to a paid Gemini model (e.g. "gemini-3.5-flash").
"""

import os

from openai import OpenAI

# --- the one place to change models -----------------------------------------

# Gemma 4 options on the Gemini API:
#   "gemma-4-31b-it"      -> dense, highest quality (default)
#   "gemma-4-26b-a4b-it"  -> MoE, faster, slightly lower quality
# To upgrade to a paid Google model later, just change this string, e.g.
#   "gemini-3.5-flash"
MODEL = "gemma-4-31b-it"

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def _client() -> OpenAI:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "Set GEMINI_API_KEY first. Get a free key at https://aistudio.google.com\n"
            '  PowerShell:  $env:GEMINI_API_KEY="your-key-here"'
        )
    # The OpenAI library, pointed at Google's endpoint. That's the whole trick.
    return OpenAI(api_key=key, base_url=BASE_URL)


def chat(prompt: str, system: str | None = None, max_tokens: int = 1024):
    """Send one prompt, get the model's text back plus token usage.

    Returns a tuple: (text, usage) where usage has .prompt_tokens and
    .completion_tokens so layers can SEE how much context they're burning.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = _client().chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
    )
    text = resp.choices[0].message.content
    return text, resp.usage