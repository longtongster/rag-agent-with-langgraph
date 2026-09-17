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

The user leads this learning project. Discuss next steps and tradeoffs before generating code or changing files, and wait for their go-ahead. When the user implements a function, review it without rewriting it unless asked. Keep explanations concise. Do not require reading whole papers or manually scanning the corpus to create evaluation evidence.

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

1. Define the use case
   - Target users
   - Document sources
   - Answer style
   - Latency and cost constraints
   - Security, privacy, and access-control needs
   - Important failure modes

2. Build a baseline RAG system
   - Document loading
   - Cleaning and normalization
   - Chunking
   - Embeddings
   - Vector store
   - Retriever
   - Answer generation
   - Source citations

3. Add evaluation early
   - Golden question set
   - Synthetic questions generated from known source chunks
   - Expected supporting documents or passages
   - Retrieval metrics: recall@k, precision@k, MRR
   - Answer metrics: groundedness, faithfulness, completeness, citation quality
   - Regression tests for future changes

4. Improve retrieval
   - Chunk size and overlap experiments
   - Metadata filters
   - Hybrid search
   - Query rewriting
   - Multi-query retrieval
   - Parent-child document retrieval

5. Add reranking
   - Cross-encoder reranker or LLM-based reranker
   - Tune candidate count before reranking
   - Tune final context count after reranking
   - Measure quality, latency, and cost tradeoffs

6. Improve answer quality
   - Prompt hardening
   - Citation enforcement
   - Refusal behavior when evidence is weak
   - Structured output where useful
   - Tests for hallucination-prone cases

7. Production hardening
   - Observability and tracing
   - Feedback capture
   - Caching
   - Async or scheduled ingestion
   - Versioned indexes
   - Access control
   - Cost monitoring
   - Latency monitoring
   - Deployment and rollback plan

8. Continuous evaluation
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

### 3. Add Evaluation Early

- What are 10-20 realistic user questions?
- Which questions should be curated, generated synthetically from sampled passages, or later collected from real usage?
- For each question, which source document or passage should be found?
- Which questions should produce a refusal or uncertainty?
- How will generated questions retain provenance to their source document, page, section, and passage?
- How will document and passage hashes identify stale evaluation examples when sources change?
- What retrieval metrics matter first: recall@k, precision@k, MRR, or something else?
- What answer behaviors should be scored: groundedness, completeness, citation quality, tone?
- What score is good enough to move to the next iteration?
- How will eval results be saved and compared, preferably with LangSmith datasets and experiment runs?

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
Continue from RAG_PROJECT_MEMORY.md. Read the current build log and help me with the next step.
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
- Evaluation should be added before optimizing retrieval or prompts.
- The repository remains the durable memory rather than the chat history.

## Next Recommended Step

Start the next session by discussing automatic passage sampling and the candidate-question format, before writing code. Sample meaningful passages across the four papers, generate roughly 20–30 synthetic candidate questions in total with source provenance, and automatically filter duplicates and weak candidates. The user reviews only a small representative sample and important failures. Keep the ten broad curated questions; attach evidence later using retrieval-assisted review. See `docs/rag-build-log.md` for current results and implementation follow-ups.

## Established Use Case and Evaluation Plan

### Scope Questions

- What document collection should the system answer from?

The targeted knowledge base is a collection of articles that predict football outcomes based on features. It can contain good features but also the best performing models. When we talk about football it is the real football. Not American football. This will most likely be scientific articles. I expect this to be generally pdf files. 


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

### Synthetic Evaluation Questions

Synthetic questions can broaden coverage without requiring a human to read every document. Do not generate several questions for every small chunk: this is costly and tends to create repetitive, unnatural evaluation data.

Use this workflow:

- Start with a small set of realistic, generic questions representing actual research tasks.
- Sample meaningful passages or sections across documents, using stratified sampling when document types or topics differ.
- Generate a limited pool of candidate questions from those sampled passages. For the current four-paper collection, target roughly 20–30 candidates in total rather than questions for every chunk.
- Store the source document, page, section, and passage as expected evidence.
- Automatically reject malformed, trivial, duplicate, and near-duplicate questions.
- Keep questions that cover distinct topics, documents, difficulty levels, and answer behaviours.
- Manually inspect only a small representative sample and important failures.
- Ask the RAG system the generated question.
- Check whether retrieval finds the expected passage or another genuinely relevant source.
- Judge whether the answer is grounded in the retrieved evidence.
- Add real user questions and production failures to the dataset once they become available.

Store enough metadata to avoid repeating work:

- Document ID.
- Document version or document hash.
- Page, section, and passage or chunk ID.
- Passage or chunk text hash.
- Generated questions.
- Expected evidence.
- Generation timestamp.
- Origin (`curated`, `synthetic`, or `production`).
- Review status.

Use this rule for incremental updates:

- If the source passage is unchanged, keep its existing evaluation examples.
- If a sampled passage is new and improves coverage, generate candidate questions for it.
- If a source passage changes, regenerate its questions or mark the existing examples as stale.

Synthetic questions are useful for coverage, but they are not a replacement for a small curated set. The evaluation dataset should eventually combine curated questions, filtered synthetic questions, and representative questions or failures from real usage.

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
