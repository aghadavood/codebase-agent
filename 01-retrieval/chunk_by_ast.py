import ast


def chunk_by_ast(text: str) -> list[str]:
    lines = text.splitlines()
    tree = ast.parse(text)
    chunks = []
    covered = set()              # the bag of line numbers inside some function

    # --- Pass one: functions (you already wrote this) ---
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            chunk_lines = lines[node.lineno - 1 : node.end_lineno]
            chunks.append("\n".join(chunk_lines))
            # NEW: mark every line this function covers
            covered.update(range(node.lineno, node.end_lineno + 1))   # ← study this

    # --- Pass two: collect the leftover tissue ---
    run = []
    for n in range(1, len(lines) + 1):
        if n not in covered:
            run.append(lines[n - 1])
        else:
            if run and any(line.strip() for line in run):
                chunks.append("\n".join(run))
            run = []
    if run and any(line.strip() for line in run):
        chunks.append("\n".join(run))

    return chunks


if __name__ == "__main__":
    with open("../00-foundations/ask_the_repo.py", "r", encoding="utf-8") as f:
        text = f.read()
    chunks = chunk_by_ast(text)
    print(f"Got {len(chunks)} chunks")
    for i, c in enumerate(chunks):
        print(f"----- chunk {i} -----")
        print(c)
