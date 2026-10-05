# RAG Project Memory

This file is intended to be copied into a clean repository and used as the durable project memory for building a production-ready RAG system. The chat can coordinate the work, but this file and the repo should hold the long-term state.

## Working Principle

Use the conversation for decisions and iteration, but keep durable memory in the repository:

- Track decisions, assumptions, experiments, and next steps in markdown.
- Track evaluation data and results in files.
- Use commits or explicit checkpoints after meaningful improvements.
- Prefer measurable improvements over subjective prompt tweaking.
- Use notebooks for exploration and analysis, but move reusable pipeline logic into tested modules under `src/`.

## Collaboration Preference

The user is learning by implementing the code themselves. Explain the next practical step and provide notebook guidance when asked; do not implement code on their behalf unless explicitly requested. Keep the project focused on building a working RAG baseline before adding research-analysis workflows. The user does not need to read every paper or manually label every chunk. When the user implements a function, review it without rewriting it unless asked.

## Memory Files

Use `RAG_PROJECT_MEMORY.md` as the stable project guide. It should describe the overall approach, preferred ecosystem, build steps, evaluation philosophy, production-readiness themes, and how to resume the project later. Update it only when the project direction, principles, or structure changes.

Use `docs/rag-build-log.md` as the running project diary. It should capture what happened in each work session: current goal, changes made, decisions made and why, experiments run, eval summaries, problems found, open questions, and next concrete steps.

In short:

- `RAG_PROJECT_MEMORY.md` is the map and principles.
- `docs/rag-build-log.md` is the travel journal and latest state.

## Preferred Ecosystem

Use the LangChain, LangGraph, and LangSmith ecosystem as much as practical:

- Use LangChain for document loading, text splitting, embeddings, retrievers, model calls, structured output, and RAG chains where it fits.
- Use LangGraph when the RAG flow needs state, branching, retries, routing, human review, multi-step retrieval, or agentic behavior.
- Use LangSmith for tracing, datasets, evaluation runs, experiment comparison, feedback capture, and regression tracking.
- Prefer ecosystem-native patterns first, but allow other libraries when they clearly improve quality, cost, latency, or maintainability.

## Target Build Path

1. Build a minimal end-to-end RAG baseline from the existing processed chunk corpus: embeddings, a persistent local vector store, retrieval, grounded answer generation, and source/page citations.
2. Run the ten curated cross-paper gold questions against that baseline. Record retrieved sources and answers, then judge relevance, factual support, citation quality, and whether the four-paper corpus has enough evidence. Mark questions as answerable, partially answerable, or unsupported; corpus gaps are not automatically retrieval failures.
3. Improve one measured failure at a time (for example, retrieval depth, chunking, hybrid search, query rewriting, or answer instructions) and compare against the same questions.
4. Add synthetic passage-level evaluation examples only if they help diagnose retrieval behavior. They are optional support for the baseline, not a prerequisite for building it.
5. Consider LangGraph orchestration, reranking, and production hardening only when the baseline and evaluation show a concrete need.

### Later: improve retrieval
   - Chunk size and overlap experiments
   - Metadata filters
   - Hybrid search
   - Query rewriting
   - Multi-query retrieval
   - Parent-child document retrieval

### Later: add reranking
   - Cross-encoder reranker or LLM-based reranker
   - Tune candidate count before reranking
   - Tune final context count after reranking
   - Measure quality, latency, and cost tradeoffs

### Later: improve answer quality
   - Prompt hardening
   - Citation enforcement
   - Refusal behavior when evidence is weak
   - Structured output where useful
   - Tests for hallucination-prone cases

### Later: production hardening
   - Observability and tracing
   - Feedback capture
   - Caching
   - Async or scheduled ingestion
   - Versioned indexes
   - Access control
   - Cost monitoring
   - Latency monitoring
   - Deployment and rollback plan

### Later: continuous evaluation
   - Offline evals before deploy
   - Online feedback review
   - Canary or A/B testing
   - Drift checks as documents change
   - Periodic refresh of golden questions

## Step Questions

Use these questions at the start of each step. They are prompts for scoping, implementation, and evaluation. They do not need perfect answers before work starts.

### 1. Define The Use Case

- Who will use the system?
- What documents should it answer from?
- What should it be allowed to use besides the documents, if anything?
- What questions should it answer well?
- What questions should it refuse or handle cautiously?
- What makes an answer useful for this user?
- What mistakes would be unacceptable?

### 2. Build The Baseline RAG

- What is the simplest useful ingestion pipeline?
- What document formats need to be supported first?
- What chunking strategy is good enough for the first version?
- Which embedding model and vector store will be used?
- What metadata should be stored with each chunk?
- How many chunks should be retrieved for the baseline?
- How will answers show citations?

### 3. Evaluate The Baseline

- Do the ten curated cross-paper questions retrieve relevant evidence from the current four-paper corpus?
- Which retrieved papers/pages support each answer, and which questions have insufficient corpus evidence?
- Are answers grounded, appropriately qualified, and cited to the right pages?
- Can answerability be recorded as answerable, partially answerable, or unsupported?
- Which failed cases are retrieval failures, generation failures, or simply corpus coverage gaps?
- What small change can be tested against the same questions?

### 4. Improve Retrieval

- Which eval questions fail because the right context is not retrieved?
- Are failures caused by chunking, embeddings, metadata, query wording, or missing documents?
- Would metadata filtering help?
- Would hybrid search help?
- Would query rewriting or multi-query retrieval help?
- Should parent-child retrieval be used to recover larger context?
- Did the retrieval change improve metrics without adding too much latency or cost?

### 5. Add Reranking

- Is the retriever finding the right answer somewhere in the candidate set?
- How many candidates should be retrieved before reranking?
- How many chunks should remain after reranking?
- Should the reranker be a cross-encoder, hosted API, or LLM-based judge?
- Which eval cases improve after reranking?
- Which cases get worse?
- Is the quality gain worth the added latency and cost?

### 6. Improve Answer Quality

- Are bad answers caused by missing context or poor generation?
- Does the prompt force the model to stay grounded in retrieved evidence?
- Does the model cite the specific sources it used?
- Does it refuse when the evidence is weak?
- Does it preserve important qualifiers, dates, versions, and conditions?
- Should answers be structured, such as JSON, bullet points, or a fixed template?
- Which hallucination-prone cases need regression tests?

### 7. Production Hardening

- What needs to be logged for debugging and observability?
- How will LangSmith traces connect user questions, retrieved chunks, prompts, model calls, and answers?
- How will user feedback be captured?
- What data should be cached?
- How will document ingestion run: manual, scheduled, or event-driven?
- How will indexes be versioned and rolled back?
- How will permissions and access control be enforced?
- What are the acceptable cost and latency limits?

### 8. Continuous Evaluation

- Which evals must pass before deployment?
- How often should the golden question set be refreshed?
- How will new user failures become new test cases?
- How will document drift be detected?
- Should changes be canaried or A/B tested?
- What metrics should be monitored in production?
- Who reviews low-confidence answers, bad feedback, or failed evals?

## Suggested Repo Structure

```text
.
├── docs/
│   ├── rag-build-log.md
│   ├── decisions.md
│   └── production-readiness.md
├── evals/
│   ├── golden_questions.jsonl
│   ├── expected_sources.jsonl
│   ├── runs/
│   └── reports/
├── data/
│   ├── raw/
│   ├── processed/
│   └── vectorstore/       # Generated local vector index; not committed
├── notebooks/             # Exploration and analysis; imports reusable code from src/
├── src/
│   └── rag_agent/
│       ├── ingest/
│       ├── retrieval/
│       ├── generation/
│       └── evaluation/
└── tests/
```

During local development, store the persistent vector database under `data/vectorstore/`. Treat it as a generated, rebuildable index and exclude its contents from Git. Keep extracted chunks and metadata in `data/processed/` as the inspectable source used to rebuild that index. If the project later uses a hosted vector database, only its configuration belongs in the repository.

Use `notebooks/` for iterative investigation, visual inspection, and experiments. Keep production and reusable code in `src/`, import that code into notebooks, and cover it with tests so results do not depend on hidden notebook state.

## Token-Cost Discipline

To keep future conversations efficient:

- Ask the assistant to read only the relevant files first.
- Keep this file and `docs/rag-build-log.md` updated.
- Store eval outputs in files instead of pasting large results into chat.
- Prefer small iterations with clear before/after metrics.
- Summarize major decisions in the repo after each session.
- Avoid asking the assistant to reload the whole codebase unless necessary.

Keep this file structured and skimmable. It is fine for it to grow while the project is still forming, but do not paste large logs, traces, generated datasets, or full eval outputs into it.

If this file becomes too long, split it into smaller topic files:

- `RAG_PROJECT_MEMORY.md` for the short overview and current direction.
- `docs/rag-build-log.md` for running session notes and next steps.
- `docs/evaluation-plan.md` for eval strategy, metrics, datasets, and review workflows.
- `docs/decisions.md` for architecture decisions and tradeoffs.
- `docs/production-readiness.md` for deployment, monitoring, access control, and operational checks.

Future conversations can then focus on one topic file at a time, which keeps context and token cost lower.

## How To Resume Later

In a future session, say:

```text
Continue from RAG_PROJECT_MEMORY.md. Read the current build log and help me implement the next RAG-baseline step in the notebook.
```

If this file has been copied into a new repository, start by creating:

- `docs/rag-build-log.md`
- `evals/golden_questions.jsonl`
- a minimal baseline RAG implementation
- a first retrieval evaluation script

## Current Status

- The use case is scoped around evidence-grounded research over scientific PDFs about professional men's association-football prediction.
- Four distinct papers are available in `data/raw/` after replacing a post-match-focused paper and removing a duplicate manuscript.
- A baseline ingestion pipeline now loads, conservatively cleans, token-chunks, annotates, validates, and saves the corpus as JSONL.
- The implementation uses an installable `src/rag_agent/` package, module-level logging, notebooks for exploration, and pytest for automated tests.
- The verified ingestion run produced `data/processed/chunks.jsonl` with 162 chunks across four documents. The last test run passed 33 tests; report persistence and the CLI still need dedicated checks. Extraction and source-scope caveats are recorded in the build log.
- Current v2 screening is complete: 162 records are saved in `data/processed/screened_chunks_v2_prompt.jsonl` and `data/processed/reviewed_screened_chunks_v2_prompt.jsonl`. The original `chunks.jsonl` remains unchanged. Each derived record contains the original chunk plus `content_type`, `categories`, `knowledge_base_recommendation`, `sampling_recommendation`, `evidence_quotes`, and `rationale` under `screening`.
- The current v2 recommendations include 142 chunks for the knowledge base and 138 for question sampling; 20 and 24 are respectively excluded. The automatic and reviewed v2 files are currently identical.
- The passage-question prompt and Pydantic response schema have been refined on individual examples. Their focus is candidate predictive-feature inventories, how features are constructed from data, reported evidence for predictive performance, and model comparisons. A feature being mentioned or used is not evidence that it is best; performance claims stay tied to the study’s task, dataset, and metric.
- An initial 25-passage sample and preliminary synthetic candidate batch are saved in `data/processed/synthetic_dataset.jsonl`. This optional passage-level evaluation work is parked while the RAG baseline is built; no embeddings, vector index, or retrieval evaluation have run yet.
- `notebooks/rag-baseline-build.ipynb` provides the current Markdown-only coding guide. The immediate next step is implementing the end-to-end baseline, then exercising it with the ten curated questions.
- The repository remains the durable memory rather than the chat history.

## Next Recommended Step

Implement the first end-to-end RAG baseline by following `notebooks/rag-baseline-build.ipynb`: load processed chunks with provenance, create embeddings and a persistent local index, retrieve passages, and generate cited answers. Then run the ten curated cross-paper questions and record answerability and failures. The four-paper collection is a prototype corpus and may not support every question.

## Established Use Case and Evaluation Plan

### Scope Questions

- What document collection should the system answer from?

The target collection is scientific research about real association-football match-outcome prediction. The RAG system should help researchers identify candidate and empirically strong predictive features, understand how to construct features from data (especially public data), and compare model families and reported performance. A model or feature that performs best in one study must remain tied to that study’s task, dataset, metric, and validation; do not present it as universally best.


- Who will ask questions?

The questions will be asked by researchers with a data science background. These people know about statistics and machine learning.  

- What should the system be allowed to use?

The system should answer only football-related questions supported by the indexed document collection. It must politely reject unrelated questions and state when the collection lacks sufficient evidence.

- What should the system not answer?

private data, legal advice, medical advice, questions outside the document set.

### First Evaluation Questions

Write 10-20 realistic user questions before optimizing the system. These are early test cases, not final exams.

For each question, capture:

- The user question.
- The document or section that probably contains the answer, if known.
- Whether the answer should be direct, cautious, or a refusal.
- Any metadata that matters, such as product version, date, department, region, or permission level.

The goal is to reveal what retrieval must find and what answer behavior is expected.

### Synthetic Evaluation Questions (Optional)

A preliminary 25-passage sample and candidate batch exist, but synthetic-question generation is parked while the baseline is built. The ten curated cross-paper questions are the initial eval set. Return to synthetic examples only if they help diagnose a measured passage-retrieval problem; they are not a gate for indexing, retrieval, or answer generation.

### Good Answer Behavior

At the start, "good answer" means how the system behaves, not that we already know the perfect content.

A good answer should:

- Answer the question directly when the documents support it.
- Use only the allowed sources.
- Cite the source documents or passages.
- Say that it does not know when the evidence is missing or weak.
- Avoid inventing details that are not in the retrieved context.
- Match the user's expected level of detail.
- Mention uncertainty or limits when the documents are ambiguous.

### Unacceptable Failure Modes

Define the failures that matter most for this use case:

- Hallucinating unsupported facts.
- Citing sources that do not support the answer.
- Answering from documents the user should not have access to.
- Giving confident answers when the evidence is weak.
- Missing critical qualifiers, dates, product versions, or policy conditions.
- Producing answers that are too vague to be useful.
