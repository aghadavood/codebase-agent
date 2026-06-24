"""
shared/llm.py  —  one place that talks to the model.

Every layer imports `chat()` from here. The whole project uses Nvidia model through
NVIDIA's OpenAI-compatible endpoint, which means we use the standard
`openai` library and just point it at NVIDIA's URL. Swapping models later
(or providers) is a one-line change in this file — nothing else has to change.

Setup:
    pip install openai
    # PowerShell:
    $env:NVIDIA_API_KEY=""


"""

import os

from openai import OpenAI

# --- the one place to change models -----------------------------------------

#qwen3.5-122b-a10b — the top-left one.
#Why it's the right choice for your project:

#Its description literally says 122B MoE for coding, reasoning, multimodal chat, agent-ready — coding and agent-ready is exactly your use case.
#It has the "tool calling" tag. That matters a lot for the later layers (3–4) where your agent needs to call tools reliably. Picking a tool-calling model now means you won't have to switch again mid-project.
#The "10B active" part (MoE) means it's efficient — fast and cheap to run despite being large.

#MODEL = "qwen/qwen3.5-122b-a10b"
MODEL = "meta/llama-3.1-8b-instruct"
BASE_URL = "https://integrate.api.nvidia.com/v1"


def _client() -> OpenAI:
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        raise RuntimeError(
            "Set NVIDIA_API_KEY first. Get a free key at https://developer.nvidia.com/nvidia-ai-studio\n"
            '  PowerShell:  $env:NVIDIA_API_KEY="your-key-here"'
        )
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