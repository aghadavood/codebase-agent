def chunk_by_lines(text: str, chunk_size: int = 50) -> list[str]:
    """Chunk the repo in constant size"""
    chunks = []
    
    lines = text.splitlines()
    for i in range(0, len(lines), chunk_size):
        chunks.append("\n".join(lines[i: i + chunk_size]))
    return chunks

if __name__ == "__main__":

    with open("../00-foundations/ask_the_repo.py", "r", encoding="utf-8") as f:
        text = f.read()
    chunks = chunk_by_lines(text, 50)
    print(f"Got {len(chunks)} chunks")
    print("----- one chunk -----")
    print(chunks[1])   # look at the second chunk
    print("----- last chunk -----")
    print(chunks[-1])   # look at the last chunk