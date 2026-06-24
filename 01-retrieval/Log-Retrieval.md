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

### untill now i have done :

1. The final chunking design — functions via AST + tissue via run/flush + drop-empty guard. One or two sentences. First, use Python’s syntax tree to pull out each function as its own chunk and mark which line numbers belong to functions. Then walk the file line by line: any lines not inside a function get collected into short “runs” of leftover code (imports, constants, comments, if __name__), and each run becomes a chunk when you hit a function or the end of the file — but skip runs that are only blank lines.

2. The decision you made: keep comment-only chunks, why ? Section comments are small but useful — they label parts of the file and can match retrieval queries like “entry point” or “config.” Blank lines carry no meaning. Dropping comment-only runs would mean parsing what counts as a comment vs. code in strings, which adds complexity without much gain at this stage.

3. One limitation still lurking ( nested-function duplication, and this is Python-only because ast only parses Python).  as "known gap, future work."

### which embedding model?

some points, becasue im using nvidia playform there is just one api key for embedding ,model and generater. embedding model is seperated fro gernerater. one emeddnig model for  questions and chunkings.  nvidia get more option,  E5-family models have a passage/query mode and require an input_type parameter — passage when embedding documents during indexing, query when embedding the user's question. 

so i  have two rules to hold:

Same embedding model everywhere.
input_type="passage" for chunks, input_type="query" for the user's question.

my candidate : nvidia/nv-embedqa-e5-v5, it lives on a separate embeddings endpoint, and it needs passage/query mode.

## 22.06.2026

on Windows + Cursor, "it printed nothing" almost always means the file Python ran isn't the file you're looking at. Either unsaved buffer, or a terminal that's drifted. The fix-habit: after editing, Ctrl+S, then run, and if output is silent-with-no-error, suspect the save before you suspect the logic. You burned a few rounds on this — that's the tuition. It'll cost you minutes next time instead of a whole exchange.
Layer 1's embedding client is officially done. now storage.


## 24.06.2026
 all  the retrieval pipeline, start to end:

1. Embed every chunk as passage → list of vectors (you have the tool).
2. Store them, paired with the original chunk text. (we are here)
Embed the question as query → one vector.
3. Cosine-similarity the question vector against every chunk vector.
4. Take the top-k highest scores → those chunks are your answer.


"vector databases" (FAISS, Chroma, Pinecone). i dont use them now. because thats a learning im using the memory of python, a plain Python list in memory.

semantic retrieval works, but the raw similarity scores are weak and clustered — ranking is trustworthy, absolute scores are not, and tight margins are normal, especially on short/similar chunks. This motivates reranking later.

 embedding is now batched end-to-end. embed_batch → build_store → done.

 I stored each chunk paired with its numbers. To search, I turn the question into numbers too, then find which chunks sit closest in meaning-space. "Closest" is measured by cosine similarity — basically, do these two point in the same direction. I wrote that math by hand (four lines) so I'd understand it, then swapped in FAISS (a fast search library) and confirmed both gave identical results. Now I know exactly what FAISS does instead of treating it as magic.

The search finds the best chunks; then I hand those chunks to the chat model and ask it to answer using only that code. This is RAG — the retrieved code becomes the context the model reasons over.

Things that broke, and what they taught me:

Semantic search works but it's humble. The right answer ranked first, but barely — a math function scored almost as high as the auth function. The signal is real but weak. That's exactly why the next layer (sharper search) exists.

Perfect search, terrible answer. My first answer just copied the code back at me instead of explaining it. The search was fine — my instructions to the model were the problem. One added sentence ("explain in plain words, don't reproduce the code") fixed it. Lesson: finding the right code isn't enough; you have to tell the model what to do with it.

An hour lost to a non-bug. My code printed nothing and I assumed it was broken. The file just hadn't saved. On Windows, "no output, no error" usually means check the save first.

The big latency mystery (the important one). My answers were taking 2 to 12 MINUTES. I thought my code was broken. I tested it by isolating each part — and found that everything was instant except the final AI call. Even asking it to just say "hello" took 214 seconds. That proved the problem wasn't my code at all — the AI was stuck waiting in a free-tier queue. The cause: I was using a giant 122-billion-parameter model just to write a short summary. Total overkill. I swapped one line to use a small, fast model instead. It dropped from 214 seconds to 0.8 seconds. The lesson: match the model size to how hard the task is. Finding the code is the hard part; summarizing it is easy and doesn't need the giant model.

Where I landed: A complete, working pipeline I built and understand line by line — cut the code, turn it into numbers, store it, search by meaning, hand the best pieces to a fast model for a grounded answer.
Next: Make the search sharper — combine meaning-based search with exact keyword matching, then add a reranking step to push the best results to the top.

