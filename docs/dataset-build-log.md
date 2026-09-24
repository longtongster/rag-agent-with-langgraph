# Evaluation Dataset Build Log

This log tracks the creation of the synthetic evaluation dataset. It is a subproject of the broader RAG build and should be closed when the synthetic question set is finalized.

The ten curated research questions are deliberately separate. They are broad, mostly multi-document synthesis questions and will receive retrieval-assisted evidence later. They are not part of the passage-sampling workflow documented here.

## Current Goal

Randomly sample passages from the completed 152-chunk sampling pool, define the synthetic-question schema, and create roughly 20–30 filtered candidates while keeping manual review small and focused.

## Scope

The synthetic set should primarily test passage-based retrieval, source attribution, and grounded answering. It should cover meaningful evidence from all four papers without generating several repetitive questions for every chunk.

Important content categories include:

- predictive features;
- how features are constructed from historical data;
- whether feature construction is reproducible from public data;
- whether information was available before kickoff;
- models and model comparisons;
- validation and evaluation methods;
- reported results;
- limitations, leakage risks, and reproducibility constraints.

A feature-related passage is especially valuable when it explains how the feature can actually be calculated from historical, pre-match data. A general claim that a feature is useful is not enough if the study does not provide a reproducible construction method.

## Agreed Sampling Approach

Passage sampling happens before embeddings and before building the vector index. Screening reads the immutable ingestion output at `data/processed/chunks.jsonl`; sampling reads the derived `data/processed/screened_chunks.jsonl` and only considers records with `sampling_decision: include`.

The first pass should be transparent and reproducible:

1. Load the verified chunk corpus.
2. Preserve document, page, section, chunk, and text-hash provenance.
3. Exclude only clearly unusable material automatically.
4. Mark potentially useful but imperfect passages for review rather than discarding them prematurely.
5. Randomly sample from the remaining candidate pool using a recorded random seed.
6. Generate synthetic question candidates from the selected passages.

Embeddings are not needed to select the initial passages. They are introduced later when testing whether retrieval can find the expected passage for a generated question.

The practical screening workflow remains in `notebooks/synthetic-dataset-chunk-checks.ipynb`. This dataset-preparation logic can stay in the notebook for the current project; no source-code extraction is required unless it later becomes stable, reusable functionality and the user explicitly requests that change.

## Filtering Policy

The initial filtering pass is automated. It is not a request for the user to read all 162 chunks. The goal is only to remove material that is clearly unsuitable before random sampling; uncertain cases remain in the pool and can be reviewed later.

### Hard exclusions

- reference-list material;
- empty or almost-empty chunks;
- text made unusable by clear extraction failure.

### Mark, but do not automatically exclude

- short chunks;
- cover or introductory material;
- table or figure captions;
- passages with limited surrounding context;
- passages with formatting artifacts that may still preserve useful meaning.

Short passages may contain a useful conclusion, model comparison, or limitation. Human review should determine whether they are usable; a length heuristic alone should not remove them.

## Screening Record Schema

The original ingestion output remains unchanged. Each line in `data/processed/screened_chunks.jsonl` contains:

- `chunk`: the original chunk with `page_content` and provenance metadata;
- `screening`: all automatic and manual screening information.

The `screening` object contains:

- `status`: automatic `eligible`, `review`, or `exclude` result;
- `flags`: automatic reasons or warnings;
- `knowledge_base_decision`: final `include` or `exclude` decision for future indexing;
- `sampling_decision`: final `include` or `exclude` decision for synthetic-question sampling;
- `review_note`: concise reason for the final decision.

## Synthetic Candidate Schema

Each candidate should retain enough information to reproduce and audit the dataset:

- question;
- question type, initially `single_source` or `passage_grounded`;
- expected answer or answer points, where generated;
- expected evidence passage(s);
- document ID and document hash;
- PDF page and section when available;
- chunk ID and text hash;
- source content category;
- generation timestamp;
- origin: `synthetic`;
- filtering status and reason;
- review status and reviewer notes.

The expected evidence is the passage from which the question was generated. It is not a claim that the passage is the only text that could answer the question.

## Review Approach

Automatic filtering should remove malformed, trivial, duplicate, near-duplicate, and unsupported candidates. It should not pretend to establish perfect scientific ground truth.

The user should review only a small representative sample and important failures. Each review should show the question together with its selected passage and provenance; reviewing complete papers is not required.

Review should check:

- whether the question is answerable from the shown passage;
- whether the passage is meaningful and correctly attributed;
- whether pre-match/post-match status is preserved;
- whether a feature-construction claim is reproducible from historical data;
- whether the question is distinct and useful for retrieval evaluation.

## Status

**Chunk screening complete — random passage sampling is next.**

- Screened all 162 original chunks and wrote 162 valid JSONL records to `data/processed/screened_chunks.jsonl`.
- Automatic results: 151 `eligible`, 6 `exclude`, and 5 `review`.
- Final knowledge-base decisions: 155 `include`, 7 `exclude`.
- Final sampling decisions: 152 `include`, 10 `exclude`.
- All records contain the complete `screening` schema; no screening fields are missing.
- The original `data/processed/chunks.jsonl` was not modified.
- No synthetic questions, embeddings, vector index, or retrieval pipeline have been created yet.

### Screening Milestone — 2026-09-23

- Used conservative regex and text-quality heuristics to identify clear reference material and uncertain extraction.
- Manually reviewed five flagged chunks: publisher metadata, one substantive model-performance passage, one additional reference chunk, and two contextless table chunks.
- Kept metadata and table chunks available to the future knowledge base but excluded them from synthetic-question sampling; excluded confirmed reference material from both.
- Stored automatic signals and final decisions together under `screening`, while preserving each original chunk under `chunk`.

## Completion Criteria

Close this subproject when:

- the sampler and candidate schema are implemented and tested;
- roughly 20–30 candidates have been generated;
- malformed and duplicate candidates have been filtered;
- a representative sample and important failures have been reviewed;
- the final dataset and its provenance are saved;
- limitations and unresolved evidence issues are recorded here.

At closure, record the next phase as **Retrieval baseline and evaluation** in this log and summarize the transition in `docs/rag-build-log.md`.

## Next Steps

1. Use the recorded random seed `56` and sample approximately one in six of the 152 sampling-eligible chunks.
2. Inspect the resulting count and document distribution without manually scanning the full corpus.
3. Define and test the synthetic candidate schema.
4. Generate and filter roughly 20–30 candidate questions.
5. Perform the limited review and close this subproject.

## Planned Sampling Configuration

The sampling configuration is recorded before the sample is created so that the result can be reproduced:

- source: `data/processed/screened_chunks.jsonl`;
- eligible pool: 152 chunks with `sampling_decision: include`;
- sampling approach: random sample of approximately one in six;
- sample interval: `6`;
- random seed: `20260923`;
- planned output: `data/processed/sampled_chunks.jsonl`.

The seed and configuration are recorded here and in the notebook; they are not repeated inside every sampled chunk.
