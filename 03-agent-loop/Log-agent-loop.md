## note for feuture layer 3 agents here is the definition of work flow and agent and the different between them

workflow, what i have done until now. rerank_pipeline is a workflow. hybrid search runs, then the reranker runs, then you take top-3. Always those steps. Always that order. i decided the order when i wrote the code. The steps never change no matter what question comes in. 
A recipe. The chef (i) wrote the recipe; the kitchen just executes it.

agent, what im building now. The steps are not written in advance. The model looks at the situation and decides what to do next, does it, looks again, decides again — and it decides when to stop. i didn't write the sequence; the model makes it up as it goes. i gave it tools and a goal, not a recipe. 
A chef i hired, not a recipe i wrote.

one-line difference : in a workflow I decide the steps in advance; in an agent the model decides the steps as it goes.

why resend history every turn: the model has no memory between calls. Each turn I must resend the WHOLE story — the question, the model's own tool calls, AND their results — or it reasons from a gap and hallucinates (silent wrong answer, no crash — same trap as Layer 1's index alignment).
