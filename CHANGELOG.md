# Changelog

All notable changes to this repository are documented here. Dates are git commit
dates (`git log` maps 1:1); small same-day commits (README tweaks, typo fixes) are
folded into one entry per phase.

## [Unreleased]

- Planned: expand the evaluation benchmark beyond 20 test cases and re-run the
  skill-vs-prompt ablation with per-metric uncertainty (McNemar/Wilson already
  reported for the pipeline-selection metric)
- Planned: thicken `references/qc_standards.md`, flagged as the main retrieval
  coverage gap in the evaluation report
- 2026-11-18 Added `docs/DECISIONS.md`: retrieval-threshold, scoring and
  evaluation-protocol decisions logged only where the repo carries written
  evidence (commit dates cited)

## [v1.0] - 2026-11-18

- `4b4f6f1` `CITATION.cff` + How-to-cite sections (EN/中文 README), `bibtex` entry

## 2026-11-03

- `282e5f3` evaluation fix: score only pipeline cases (cross-domain cases judged
  separately on refusal behaviour), report uncertainty instead of bare percentages

## 2026-10-13/14

- `7b3c747` commit the qwen3:14b ablation run files and a provenance table mapping
  every README number to a committed artifact
- `54925ed` render `v1.0.0_report.md` from committed results (no GPU, no network)

## 2026-09-02

- `4f65b88` true semantic search: `BAAI/bge-small-zh-v1.5` embeddings via fastembed
  (local ONNX), 79-chunk index
- `9bf63a8` wire semantic retrieval into `ResearchAgent` (keyword-first,
  semantic-fallback decision rule)
- `7739375` / `1ac29a6` SKILL.md Step 2b landed in code: `uncovered_domain` +
  executable 3-round `WebFallbackPlan`, with honest zero-result protection
- `21318c0` retrieval quality metrics in the README

## 2026-08-02/03

- `160bb8e` V1 frontend: pipeline management, category editing, auto-build API
- `bb1d1df` web-fetch fallback path
- `bbc0308` split bilingual README (EN / 中文) with language switch
- `b1a4534` category-filter and launcher fixes

## 2026-07-28..31

- `44bbb9f` initial commit: FlowSeq v1.0 — 10 pipelines with interactive flowcharts
- `351bde7` / `4f7689a` family-trio WGS, MR/PRS/rare-variant pipelines, enriched GWAS
- `fa28927` / `3800a7a` repo upgraded to a Skill repo: SKILL.md + FlowSeq unified,
  build-time pipeline JSON generation
- `a18fce6` full bilingual fields across pipeline JSONs
- `a043ace` evaluation framework added
- `59c5c30` Agent & RAG implementation (4-tool plan/act loop)
