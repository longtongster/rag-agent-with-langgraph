# RAG Build Log

## Current Goal

Agree on automatic passage sampling and the synthetic candidate-question format before implementation. Use the verified four-paper corpus and keep manual review small.

### Paper-Search Prompt

The following prompt was used to ask ChatGPT to find the papers:

> Find five high-quality research papers on predicting professional men’s association-football match outcomes.
>
> **Requirements:**
>
> 1. Focus on match outcome prediction (home win/draw/away win, score, or goal difference).
> 2. Study predictive features and/or models such as XGBoost, random forests, neural networks, or deep learning.
> 3. Use matches from the Premier League, La Liga, and/or Bundesliga.
> 4. Use features reproducible from publicly available historical data.
> 5. Features must have been available before kickoff; exclude studies relying on future information or data leakage.
> 6. The complete paper must be legally and freely downloadable.
> 7. Prefer peer-reviewed, methodologically sound, and reproducible studies.
>
> **For each paper, provide:**
>
> - Full citation, publication year, and direct open-access link.
> - League(s), seasons, dataset, and prediction target.
> - Features used and their public data sources.
> - Models evaluated, validation method, metrics, and best result.
> - Why the paper was selected.
> - Reproducibility limitations.
>
> Verify that every link works and that each paper genuinely meets the requirements. Present the papers in a comparison table and rank them by relevance and methodological quality—not citation count alone.

**Possible future refinement:** Specify a publication period, such as 2018–2026, when focusing on modern modelling approaches.

### Best Predicting Features

| #  | Feature                    | Why it matters                                                        | How to calculate                                |
| -- | -------------------------- | --------------------------------------------------------------------- | ----------------------------------------------- |
| 1  | Elo / team strength rating | Strong measure of overall team quality                                | Update rating after every previous match        |
| 2  | Recent goal difference     | Captures recent attacking and defensive strength                      | Rolling average over last 5–10 matches          |
| 3  | Home/away goal difference  | Teams often perform differently home vs. away                         | Separate home and away performance              |
| 4  | Recent xG difference       | Better measure of underlying performance than goals                   | Rolling xG for − xG against                     |
| 5  | Recent xG for / against    | Separates attacking and defensive quality                             | Rolling average over last 5–10 matches          |
| 6  | Shots / shots on target    | Measures attacking dominance                                          | Rolling average/difference over recent matches  |
| 7  | Recent form                | Captures short-term changes in team strength                          | Points or W/D/L over last 5 matches             |
| 8  | Home advantage             | Home teams have a persistent advantage                                | Home-team indicator / historical home advantage |
| 9  | Opponent-adjusted form     | Beating a strong opponent is more informative than beating a weak one | Weight results by opponent strength             |
| 10 | Rest days                  | More/less recovery time can affect performance                        | Days since previous match                       |
| 11 | League position / points   | Simple proxy for current team quality                                 | Current league table before the match           |

### Initial Evaluation Questions

These generic questions will test retrieval and synthesis across the initial paper collection:

> 1. What are the best pre-match features for predicting football match outcomes?
> 2. Which machine-learning models perform best for football match outcome prediction?
> 3. Which features can be calculated using only historical data available before kickoff?
> 4. Which features appear consistently useful across the studies?
> 5. What are the main risks of data leakage in football match prediction?
> 6. Which evaluation metrics are most appropriate for home/draw/away prediction?
> 7. How important is recent form compared with longer-term team strength?
> 8. Which publicly available data sources can be used to construct these features?
> 9. Which features are most suitable for an XGBoost football match prediction model?
> 10. What are the main limitations of current football match prediction approaches?

Expected evidence will be attached after PDF extraction. Synthetic evaluation will sample meaningful passages across the collection and generate roughly 20–30 candidates in total—not several questions for every chunk. Candidates will be deduplicated and filtered, with only a small representative sample and important failures reviewed manually.

## Current Status

- The initial use case has been scoped in `RAG_PROJECT_MEMORY.md`.
- Four distinct PDF papers remain in `data/raw/`; the post-match-focused Frontiers paper and the duplicate manuscript have been removed.
- An initial set of ten cross-document evaluation questions has been drafted.
- The evaluation approach has been set: combine generic curated questions with filtered synthetic questions from sampled passages, then add real usage cases later.
- Local vector indexes will be persisted under `data/vectorstore/`. Their generated contents are ignored by Git and can be rebuilt from `data/processed/`.
- Notebooks will be used for iterative exploration and analysis. Reusable implementation code will remain in `src/` and be imported into notebooks.
- The project uses a conventional installable package under `src/rag_agent/`.
- The ingestion pipeline loads PDFs, performs conservative text cleaning, creates token-based chunks, adds document and chunk provenance metadata, validates the combined corpus, and writes deterministic JSONL.
- Pipeline progress uses module-level logging. A `__main__` argparse entry point and optional report saving have been added; CLI argument wiring and logging configuration need follow-up.
- The last test run reported 33 passing tests covering PDF loading, cleaning, chunking, chunk metadata, validation, JSONL serialization, and ingestion orchestration.
- The latest ingestion run produced 162 JSONL chunks across four source documents, with valid/saved true and no reported validation errors or failed files.
- Direct chunking and orchestration tests now pass, including invalid settings, deterministic output, provenance, overlap, empty input, and extraction failures that preserve an existing corpus.
- The corpus exists at `data/processed/chunks.jsonl`: four documents and 162 chunks using 512-token chunks and 50-token overlap. Sampled text is usable with extraction caveats recorded below.
- Embedding, vector indexing, retrieval, and answer generation have not started.

## Next Steps

1. Discuss automatic passage sampling and the candidate-question schema with the user before generating code. Do not ask the user to read four articles or scan 162 chunks.
2. Automatically sample meaningful methods, features, validation, and results passages across all four papers; exclude cover sheets and references. Preserve pre-match/post-match qualifiers and avoid evidence requiring visual interpretation.
3. Generate roughly 20–30 synthetic candidate questions in total from sampled passages. Retain source document/page/chunk identifiers, document/text hashes, generation timestamp, origin, and review status, together with expected evidence.
4. Automatically reject malformed, weak, duplicate, and near-duplicate candidates. The user reviews a small representative sample and important failures.
5. Keep the ten broad curated research questions. Attach evidence later with retrieval-assisted review; do not make manual labeling of all ten a prerequisite for synthetic generation.
6. Build and evaluate the minimal embedding and retrieval baseline.

## Session Wrap-up — 2026-09-17

### Final corpus

- The user replaced `fspor-07-1713852.pdf` with `s10994-018-5704-6.pdf`. Inspection showed the replacement is the published version of the study already present as `z1_MLJ.pdf`.
- With user authorization, removed `z1_MLJ.pdf`, retained the published version, and regenerated chunks and the report using the ingestion function with 512-token chunks and 50-token overlap.
- Final counts: `2024156785.pdf` 26; `a263-Article Text-847-2-10-20231219.pdf` 22; `s10994-018-5704-6.pdf` 32; `s10994-024-06625-9.pdf` 82. **Total: 162 chunks, four distinct papers.**
- `data/processed/ingestion-report.json` records `valid: true`, `saved: true`, four documents, and no errors or failed files. Raw PDFs and generated artifacts remain ignored by Git.
- Before duplicate removal, revalidated the corpus and checked that stored document hashes matched all current PDF files. Replacement-paper samples had readable prose and preserved provenance, with some heading/equation formatting artifacts.

### Extraction inspection and future multimodal support

- Isolated the old manuscript's XObject warning to PDF page 17. Visually compared the rendered page against extracted text; paragraphs, headings, caption, and chart labels were present. A second extractor produced identical text apart from whitespace. No baseline extraction fix was needed. This manuscript is now removed as a duplicate.
- This targeted check does not establish full visual extraction fidelity for the whole corpus. Parser warnings are not captured by the structural validation report.
- Keep the text baseline first. Consider structured table extraction, then figure/image retrieval and vision-based interpretation if evaluation failures justify them. Record questions requiring visual evidence; do not treat chart dots or flattened equations as reliably extracted evidence.

### User implementation and review

- The user implemented `save_ingestion_report()` with readable, sorted JSON and explicit UTF-8 output. `ingest_documents()` accepts optional `report_path`, saves after either validation outcome, and still returns the report. Unhandled exceptions can still prevent report saving.
- The assistant reviewed the implementation and added the requested helper docstring. The last existing-suite run reported **33 passed**; dedicated tests for report persistence and CLI behavior have not been added.
- Review follow-ups: prevent the report path from overwriting the chunks path; check report persistence for successful and failed validation.
- At wrap-up, the saved CLI defines positional arguments named `input-dir` and `output-path` but accesses `args.input_dir` and `args.output_path`. These names need alignment before the next CLI run (underscore positional names, or named `--input-dir` / `--output-path` options). The latest successful corpus regeneration called the Python function directly. No code was changed during this documentation wrap-up.

### Agreed working approach for tomorrow

- The user remains in the lead: discuss design first, then implement only when authorized. Keep reviews and explanations concise.
- Do not manually walk through the full corpus to label evidence. Follow the existing sampled synthetic-evaluation approach, with automated filtering and limited human review.
- Tomorrow starts with **passage-sampling strategy and candidate-question format**, not code generation. No synthetic questions, embeddings, vector index, or retrieval pipeline were created today.
- The user will make the commit after this documentation wrap-up.

## Session: Ingestion Verification — 2026-09-17

- Added 12 test cases for chunking and ingestion orchestration; `.venv/bin/python -m pytest -q` reports **33 passed**. The dependency emitted a deprecation warning for `langchain-community`; no dependency changes were made.
- Ran `ingest_documents(Path("data/raw"), Path("data/processed/chunks.jsonl"), chunk_size=512, chunk_overlap=50)` successfully. Saved the returned structural validation report at `data/processed/ingestion-report.json`.
- Confirmed chunk counts: `2024156785.pdf` 26; `a263-Article Text-847-2-10-20231219.pdf` 22; `fspor-07-1713852.pdf` 43; `s10994-024-06625-9.pdf` 82; `z1_MLJ.pdf` 35. Total: **208 chunks, five documents**.
- Inspected excerpts (up to 1,600 characters) from the first, middle, and last chunk of each paper. Prose is generally readable. Caveats include garbled MENDEL headers, accented-name artifacts, flattened equations/tables, and publisher cover material. This was a text spot check, not full visual verification against the PDFs.
- A follow-up extraction isolated the warning to `z1_MLJ.pdf`. The parser emitted `Exceeded 5000 form XObject invocations while extracting text; further form content is skipped.` Structural validation still passes: its empty `warnings` list does **not** mean extraction was complete, because parser warnings are not captured by that report.
- The Frontiers paper explicitly describes post-match prediction in chunk index 21, zero-based PDF page 7. Its evidence must retain that qualifier; the original paper-search requirements are not proof that every selected paper satisfies pre-kickoff availability.
- Generated corpus and report remain local, ignored artifacts under the existing Git rules. No embeddings or model calls were needed.
