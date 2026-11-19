# Changelog

All notable changes to this repository are documented here. Dates are git commit
dates (`git log` maps 1:1); small same-day commits (README tweaks, typo fixes) are
folded into one entry per phase.

## [Unreleased]

- 2026-11-18 Added `docs/external_baselines.md`: published skill/knowledge-injection
  gains re-checked against sources (Moll 2026 +4.3 pt, Yan 2026 +0.43, Phuong 2026
  +6.28 pt mostly non-significant, SWE-bench oracle 1.96→4.8 %), registry
  reproducibility baselines (Grayson ACM REP'23 51 %/88 % crash-free), nf-core
  citation corrected to Langer 2025 / Ewels 2020, and three unverifiable leads
  logged as do-not-cite; README gained an External-baselines section
- 2026-11-19/20 Benchmark extended from 20 to 30 cases (TC-021…TC-030: RNA-seq
  batch effect, tumour-only somatic WGS without a matched normal, low-biomass 16S
  with a contaminated extraction blank, hg19 BAMs joint-genotyped with hg38
  samples, single-sample `-ERC GVCF`, cross-ancestry PRS from European summary
  statistics, single-replicate ChIP-seq and IDR, 10x Multiome and PacBio HiFi SV
  as uncovered questions, 3,000/30,000 case-control GWAS) and the skill-vs-prompt
  ablation re-run on both arms with local `qwen3:14b` — answers generated
  2026-11-19 by `python/evaluation/generate_outputs.py` (now committed; it writes
  a per-arm meta file with the system-prompt sha256), scored 2026-11-20. Added
  `python/evaluation/analyze_ext30.py` (paired statistics, reuses
  `runner._to_predictions` and the metric modules instead of re-scoring),
  `evaluation/metrics/render_ext30_report.py` →
  `evaluation/results/ext30_report.md` (renders the 30-case report from the
  committed JSONs only, MISSING line instead of an invented value,
  byte-reproducible; `test_ext30_stats.py` locks its numbers to the stats
  artifact), `tests/test_ext30_stats.py` (14 tests, 28 in the evaluation suite),
  and `results/report_ext30_stats.json`; `.gitignore` now carries `!` exceptions
  for every ext30 artifact the README quotes. **The outcome is negative in both
  directions**: the runner's 73.08% vs 80.77% is an extractor asymmetry (19/22 vs
  19/22 on the 22 cases both arms resolve), no pipeline-selection difference is
  resolvable at this size (2/4/3 discordant cases → a unanimous split still gives
  p = 0.5/0.125/0.25), neither arm abstains on the 4
  uncovered cases (0/4 credit in both), and `must_flag_traps` /
  `must_apply_validations` are declared on all 30 cases but scored by no metric.
  Fixed on the way: the first resolution helper passed the smaller discordant
  count as the binomial total, which returned p = 0.0 and invented "minimum
  detectable splits" — it now delegates to `statistics.mcnemar_exact`. README and
  README_zh gained the "Extended 30-case run / 30 例扩展运行" section; the
  `evaluation/benchmarks/test_cases.json` mirror was regenerated from the scored
  file and its hardcoded `generated` stamp corrected (2026-11-02 → 2026-11-19,
  with a comment to bump it when the case set changes). `OPTIMIZATION.md` known-issues
  table gained rows 15–17 for the defects this run exposed (unscored declared case
  fields, runner percentages computed on arm-specific denominators, dead
  `PIPELINES_DIR`) and row 10 is marked partially resolved
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
