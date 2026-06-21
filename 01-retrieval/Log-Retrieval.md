##19.6.2026 Constant chuncking chunk_by_lines.py

### after the dumb work in foundation which just retrieve the whole conetnt of repository we got in to next step Retrieval.
Retrieval needs chuncking and embedding. 

### first step chuncking. but how  should chunck the code ?constant chuncking not works, thats very obvious.

one chuncking gets one vector and one meaning. so the chuncking strategy is a foundation to to embedding step. consider that with chunking size 50 for a code. which include functions imports and ... some functions have just 3 line of codes some 400 hundreds of code. 
line-counting cuts through structural boundaries — it starts a chunk in the middle of a function (that dangling if with no def above it) and ends mid-statement (the half-built prompt = (). The chunk ends up holding pieces of multiple unrelated things, so its single vector becomes a smudge that's sharp about nothing. "Broke the meaning" is the conclusion; "cut through function boundaries so one chunk holds fragments of several things" is the reason.
Constatnt chuncking broke the meaning of the vector which is the base for embedding models.
so Navie chuncking doesnt work.
### a better chunk should respect the natural boundaries of the code — one whole function or one whole class per chunk, so each chunk is one complete idea, while also splitting the giant functions and not drowning in tiny ones.

## 20.6.2026 Structure-aware chunking chunk_by_ast.py
The fix is to stop treating code as text and start treating it as code.  

There is a point ,python internally has to understand the code to run that . how ? it builds atree.
The ast module helps Python applications to process trees of the Python abstract syntax grammar.
AST-by-functions-only silently drops the connective tissue of the file
So the solution: You give it your source code as text, and it gives you back the structured tree.
That's the whole idea. Three things to lock in :
1.	ast parses source text into a tree that mirrors the code's real structure.
2.	In that tree, each function is a FunctionDef node that knows its start and end line.
3.	So: walk the tree → find the FunctionDefs → slice the file by their line numbers, not by 50. Structure-aware, not count-aware.

Now this problem: it give s just the functions , what about imports section, if __name__ == “__main__” ….?

### Solution :splitting on structure first, then falling back to fixed-size for the gaps.

Structure-aware chunking = two passes.

1. Pass one: walk the AST, pull out each FunctionDef (and ClassDef) as its own chunk — start line to end line. These are your clean, meaningful chunks.
2. Pass two: whatever lines are left over (imports, constants, the __main__ block) — the stuff between and outside functions — gather those so they're not lost. (Exactly how to gather them is a design choice we'll make when we hit it.)

## 21.6.2026

my  code drops pure-blank chunks but keeps comment-only ones.

Assuming the output is clean now and chuncking is done. 

untill now i have done :

1. The final chunking design — functions via AST + tissue via run/flush + drop-empty guard. One or two sentences. First, use Python’s syntax tree to pull out each function as its own chunk and mark which line numbers belong to functions. Then walk the file line by line: any lines not inside a function get collected into short “runs” of leftover code (imports, constants, comments, if __name__), and each run becomes a chunk when you hit a function or the end of the file — but skip runs that are only blank lines.

2. The decision you made: keep comment-only chunks, why ? Section comments are small but useful — they label parts of the file and can match retrieval queries like “entry point” or “config.” Blank lines carry no meaning. Dropping comment-only runs would mean parsing what counts as a comment vs. code in strings, which adds complexity without much gain at this stage.

3. One limitation still lurking ( nested-function duplication, and this is Python-only because ast only parses Python).  as "known gap, future work."