## 1.07.2026 Layer 2 — Workflows. Focus on: prompt chaining, routing, parallelization, evaluator-optimizer. Build these RAW (a few lines each), not with a framework. Skip the agents section.

learning to chain multiple model calls together into a fixed pipeline — because one single call to the model is often not enough to do a real job well.
### whats the story ?

In Layer 1 (retrieval), the whole system was basically: one call to the model. Retrieve chunks, stuff them in a prompt, ask the model once, get an answer. One shot. naive RAG is one-shot; it retrieves once with no validation, and answers go confidently wrong. One call, one chance, no do-over.


So the natural next question is: what if one call isn't enough? What if the job is too big for a single call to do well?

Think about a real task: "read this messy code file and give me clean documentation." If i ask the model to do that in one call, it has to — understand the code, and structure the docs, and write them, and check them — all at once. It does each of those a little worse because it's juggling. 

idea for future : Same way a person writing an essay in one pass, no outline, no editing, writes worse than someone who outlines, drafts, then edits.


That's what workflows are: breaking one big job into several small model calls, where you decide the order. Instead of "do everything at once," it's "first summarize → then outline → then write → then check." Each call does one easy thing well. You wire them together.

Why does this deserve its own folder / its own layer? Because it's a genuinely different skill from retrieval. Retrieval was about finding the right information. Workflows are about structuring the thinking — orchestrating several calls into a reliable pipeline. Different problem, different muscle.
And here's the deeper reason it sits right here, between retrieval and the agent loop. Look at the ladder in roadmap is climbing:

Layer 1: one model call. (simplest)
Layer 2 (here): several model calls, in an order you hardcode. ← the recipe
Layer 3: several model calls, in an order the model decides. ← the chef

Layer 2 is the middle rung.  stand on it to reach Layer 3. Because in Layer 2 i learn to connect multiple calls together — that's the mechanical skill — while you still control the order (safe, predictable, you can't get lost). 
Then in Layer 3, ill keep the "multiple connected calls" machinery but hand the ordering decision to the model. 

The four patterns in this folder are just four shapes of "multiple calls":

Chaining — calls in a line, each feeds the next. (assembly line)
Routing — first call picks which path, then you run that path. (a fork in the road)
Parallelization — several calls at the same time, combine results. (split the work)
Evaluator-optimizer — one call makes, another checks, repeat till good. (draft and edit)

All four share the same DNA: more than one call, and i decide how they connect. That's the whole folder.


The resource:   Anthropic's Building Effective Agents — the workflows section and the "augmented LLM" building block, and build them raw (a few lines each, no framework). That's the one source for this layer. 

by the end i'll have four small files — chaining.py, routing.py, parallel.py, evaluator.py — each a tiny working demo of one pattern, each proving i can wire multiple model calls into a pipeline i designed. That's the deliverable.








