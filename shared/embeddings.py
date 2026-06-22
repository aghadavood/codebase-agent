"""
shared/embeddings.py  —  one place that talks to the embeddings model.

Every layer imports `embed()` from here. The Nvidia embeddings model through
NVIDIA's OpenAI-compatible endpoint, which means we use the standard
`openai` library and just point it at NVIDIA's URL.
"""

import os

from openai import OpenAI

EMBED_MODEL = "nvidia/nv-embedqa-e5-v5"

BASE_URL = "https://integrate.api.nvidia.com/v1"

def _client() -> OpenAI:
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        raise RuntimeError(
            "Set NVIDIA_API_KEY first. Get a free key at https://developer.nvidia.com/nvidia-ai-studio\n"
            '  PowerShell:  $env:NVIDIA_API_KEY="your-key-here"'
        )
    return OpenAI(api_key=key, base_url=BASE_URL)


def embed(text: str, mode: str) -> list[float]:
    """Embed one string. mode must be 'passage' (chunks) or 'query' (questions)."""
    if mode not in ("passage", "query"):
        raise ValueError('mode must be "passage" or "query"')

    resp = _client().embeddings.create(
        model=EMBED_MODEL,
        input=[text],
        extra_body={"input_type": mode},
    )
    return resp.data[0].embedding


if __name__ == "__main__":
    v = embed("def hello(): return 'hi'", "passage")
    print(len(v))
    print(v[:5])
