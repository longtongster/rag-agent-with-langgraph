# RAG Build Log

## Current Goal

Build the minimal PDF extraction and chunking pipeline for the five selected papers.

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
- Five initial PDF papers have been added to `data/raw/`.
- An initial set of ten cross-document evaluation questions has been drafted.
- The evaluation approach has been set: combine generic curated questions with filtered synthetic questions from sampled passages, then add real usage cases later.
- Local vector indexes will be persisted under `data/vectorstore/`. Their generated contents are ignored by Git and can be rebuilt from `data/processed/`.
- Notebooks will be used for iterative exploration and analysis. Reusable implementation code will remain in `src/` and be imported into notebooks.
- No baseline RAG implementation has been started.

## Next Steps

1. Build the minimal PDF extraction and chunking pipeline with document, page, section, and passage metadata.
2. Sample meaningful passages across the five papers.
3. Generate roughly 20–30 synthetic candidate questions in total.
4. Deduplicate and filter the candidates, then inspect a small representative sample.
5. Store each retained question with its expected evidence and provenance.
6. Build and evaluate the minimal baseline retriever and answer-generation pipeline.
