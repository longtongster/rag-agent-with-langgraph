# Evaluation Dataset Build Log

> **Parked for now (2026-10-02):** the immediate project goal is to build the RAG baseline and evaluate it with the ten curated cross-paper questions. Regenerating this synthetic passage-question set is optional and should resume only if it helps diagnose a measured retrieval problem. This log preserves the work and plan for that optional task; it is not the current project gate.

This log tracks the creation of the synthetic evaluation dataset. It is a subproject of the broader RAG build and should be closed when the synthetic question set is finalized.

The ten curated research questions are deliberately separate. They are broad, mostly multi-document synthesis questions and will receive retrieval-assisted evidence later. They are not part of the passage-sampling workflow documented here.

## Current Goal

Generate and review one grounded question candidate for each of the existing 25 sampled passages. The first candidate batch is preliminary: user review identified low-value items (including a routine train/test split question and overly detailed ANN mechanics). The prompt and Pydantic schema have now been tightened around the ten intended research questions; regenerate candidates for the same sample before accepting the dataset.

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

A concrete feature inventory is useful even when a passage does not establish predictive performance. Keep that distinct from evidence that a feature performed well in a particular study. Feature-construction details are especially valuable when they explain how to calculate a feature from identifiable historical data, ideally public and available before kickoff. Do not infer public availability, reproducibility, or predictive value when the paper does not establish it. Record model comparisons and the evaluation evidence behind a reported “best” model without treating one study’s result as universal.

## Agreed Sampling Approach

Passage sampling happens before embeddings and before building the vector index. The notebook reads the immutable ingestion output at `data/processed/chunks.jsonl`, screens its 162 chunks, and writes `data/processed/screened_chunks_v2_prompt.jsonl` plus `data/processed/reviewed_screened_chunks_v2_prompt.jsonl`. Chapter 2 selects records whose `screening.sampling_recommendation` is `include`. The two v2 files currently contain the same records and recommendations.

The first pass should be transparent and reproducible:

1. Load the verified chunk corpus.
2. Preserve document, page, section, chunk, and text-hash provenance.
3. Exclude only clearly unusable material automatically.
4. Keep a useful candidate-feature inventory even when predictive value or construction details are not reported; do not overstate what the paper proves.
5. Randomly sample 25 passages from the 138 currently eligible records using seed `56`.
6. Generate one passage-grounded question candidate per sampled passage and review each against its source.

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

## Current Screening Record Schema

The original ingestion output remains unchanged. Each line in the v2 screening files contains:

- `chunk`: the original chunk with `page_content` and provenance metadata;
- `screening`: all automatic and manual screening information.

The current `screening` object contains `content_type`, `categories`, `knowledge_base_recommendation`, `sampling_recommendation`, `evidence_quotes`, and `rationale`. The recommendations use `include`, `exclude`, or `review`. The current schema does not include the older `status`, `flags`, `knowledge_base_decision`, `sampling_decision`, or `review_note` fields.

The question-generation Pydantic response contains `suitable`, `categories`, `aligned_evaluation_questions` (one or more of `Q1`–`Q10` for suitable items), `primary_category`, `question`, `answer`, `evidence_quote`, and `rejection_reason`. A suitable item must align to at least one high-level evaluation question. The schema validates field shape and alignment IDs, while the prompt defines substantive alignment and excludes procedural trivia; semantic usefulness still requires review. This is the model response schema; a durable candidate record that also stores source provenance has not yet been created.

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

## Status — updated 2026-10-01

**Current v2 screening is complete; the initial 25-passage sample and question batch exist, but the batch is preliminary and must be regenerated under the revised prompt/schema.**

- The original corpus contains 162 chunks across four papers; `data/processed/chunks.jsonl` remains unchanged.
- `screened_chunks_v2_prompt.jsonl` and `reviewed_screened_chunks_v2_prompt.jsonl` each contain 162 records using the current schema.
- Current v2 knowledge-base recommendations: 142 `include`, 20 `exclude`.
- Current v2 sampling recommendations: 138 `include`, 24 `exclude`.
- The reviewed file is currently byte-identical to the automatic v2 file; the manually inspected contextless-table decision matches the v2 recommendation.
- The initial 25 passages were sampled from the 138 eligible records using seed `56` and saved with generated candidates in `data/processed/synthetic_dataset.jsonl`. The IDs and order match `random.sample` with that seed and the current eligible pool.
- User review flagged low-value candidates, including routine split-ratio trivia and excessive ANN training detail. The existing candidates were generated under the previous prompt/schema and are not accepted as the final set.
- The revised prompt directly anchors generation to the ten high-level research questions in `docs/rag-build-log.md`, distinguishes feature inventory/construction/performance claims, and rejects generic procedural trivia unless materially relevant. The Pydantic model now requires `aligned_evaluation_questions` IDs (`Q1`–`Q10`) for suitable items and none for unsuitable items.
- The existing 25-passage sample should be retained for a like-for-like regeneration and review. No embeddings, vector index, or retrieval evaluation have been run.

### Initial screening experiment — 2026-09-23 (superseded by current v2 screening)

- Used conservative regex and text-quality heuristics to identify clear reference material and uncertain extraction.
- Manually reviewed five flagged chunks: publisher metadata, one substantive model-performance passage, one additional reference chunk, and two contextless table chunks.
- Kept metadata and table chunks available to the future knowledge base but excluded them from synthetic-question sampling; excluded confirmed reference material from both.
- Stored automatic signals and final decisions together under `screening`, while preserving each original chunk under `chunk`.

## Completion Criteria

Close this subproject when:

- a 25-passage sample has been drawn and recorded;
- up to 25 question candidates have been generated from the sampled passages;
- candidates have been filtered and reviewed;
- malformed and duplicate candidates have been filtered;
- a representative sample and important failures have been reviewed;
- the final dataset and its provenance are saved;
- limitations and unresolved evidence issues are recorded here.

At closure, record the next phase as **Retrieval baseline and evaluation** in this log and summarize the transition in `docs/rag-build-log.md`.

## Next Steps

1. Regenerate question candidates for the same 25 sampled passages in `data/processed/synthetic_dataset.jsonl` using the revised prompt and Pydantic schema; retain the sample and its provenance.
2. Review whether each item materially supports its assigned high-level question, is useful, accurately grounded, and supported by an exact source quote. Keep study-specific performance claims tied to the reported task, data, and metric.
3. Filter duplicates and weak items, then save accepted candidates with source provenance.
4. Review the candidate set and update this log with actual counts and unresolved issues.

## Planned Sampling Configuration

The configured sampling parameters used for the existing draw are:

- source: the current v2 screening records in `data/processed/screened_chunks_v2_prompt.jsonl` (138 records have `sampling_recommendation: include`);
- sample size: `25`, without replacement;
- random seed: `56`.

The notebook does not write a separate `sampled_chunks.jsonl` file; the selected passages are retained within `data/processed/synthetic_dataset.jsonl`. Do not draw a new sample for the prompt-quality comparison unless the sampling plan is deliberately changed.
