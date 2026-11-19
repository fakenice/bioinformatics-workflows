[中文](README_zh.md)

# FlowSeq — Interactive Bioinformatics Pipeline Navigator

**A knowledge-constrained AI Skill for standardized, traceable and reproducible bioinformatics workflow generation.**

---

## Architecture

```
┌──────────┐
│   User   │
└────┬─────┘
     │  Natural language query
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Skill (SKILL.md)                                            │
│                                                              │
│  Step 1: Understand query → omics type + study design        │
│                                                              │
│     ┌─ Covered in quick reference table? ─┐                  │
│     │ YES                    │ NO         │                  │
│     ▼                        ▼            │                  │
│  Step 2a                    Step 2b       │                  │
│  Preset search queries      Generic search (3 rounds)        │
│  (per-category keywords)    Round 1: find authoritative src  │
│  web_search("GATK...")      Round 2: drill into best source  │
│  web_search("nf-core...")   Round 3: supplement QC metrics   │
│     │                        │                               │
│     └────────┬───────────────┘                               │
│              ▼                                               │
│  Step 3: Extract structured info                             │
│  (steps, tool versions, QC thresholds, references)           │
│              │                                               │
│              ▼                                               │
│  Step 4: Output → Markdown table | FlowSeq JSON              │
│              │                                               │
│              ▼                                               │
│  Step 5: Knowledge accumulation (feedback loop)              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  Write back to:                                      │     │
│  │  • SKILL.md quick reference table  (Step 2b → 2a)   │     │
│  │  • references/study_designs.md    (detailed pipeline)│     │
│  │  • references/sharp_edges.md      (new pitfalls)     │     │
│  │  • src/data/pipelines/{slug}.json (FlowSeq source)   │     │
│  └──────────────┬──────────────────────────────────────┘     │
└─────────────────┼────────────────────────────────────────────┘
                  │  Grounded context (references/*.md + 14 pipeline JSONs)
                  ▼
┌──────────────────────────────────────┐
│  Knowledge Constraints               │
│  study_designs  — decision matrix    │
│  patterns       — reusable code      │
│  sharp_edges    — known pitfalls     │
│  validations    — QC rules           │
│  + Semantic Search (79-chunk bge-zh) │
└────┬─────────────────────────────────┘
     │  Constrained context window
     ▼
┌──────────┐
│   LLM    │  Grounded generation — no hallucinated tools or parameters
└────┬─────┘
     │
     ▼
┌─────────────────────────┐
│  Standardized Pipeline  │  Structured Markdown + FlowSeq JSON
│  + Nextflow .nf export  │  + Tool versions, QC thresholds, DOIs
└─────────────────────────┘
```

**Key insight**: The Skill does not let the LLM freely improvise. Every pipeline step, tool version, QC threshold, and reference must trace back to the knowledge base. When a query hits an uncovered domain, the generic search path (Step 2b) not only answers the user but also feeds back into the quick reference table (Step 5), progressively shrinking uncovered territory over time.

---

## What This Is

A **bioinformatics workflow intelligence Skill repository** that guides AI coding assistants through standardized NGS analysis. It works as a constraint layer between the user and the LLM: the Skill intercepts the query, selects the right pipeline, injects domain knowledge (patterns, traps, validations), and the LLM generates grounded, citable output.

This repository also hosts **FlowSeq** — an interactive pipeline browser + Skill documentation frontend, deployed at:

**[https://fakenice.github.io/bioinformatics-workflows](https://fakenice.github.io/bioinformatics-workflows)**

---

## Skill Capabilities

### Pipeline Knowledge Base

| Category | Pipeline | ID |
|----------|----------|----|
| DNA | WGS Germline Variant | `wgs-germline` |
| DNA | WGS Somatic Variant | `wgs-somatic` |
| DNA | Family Trio WGS | `family-trio-wgs` |
| DNA | WES Capture Sequencing | `wes` |
| DNA | GWAS Association Analysis | `gwas` |
| DNA | PRS Polygenic Risk Score | `prs` |
| DNA | Rare Variant Association | `rare-variant` |
| RNA | RNA-seq Differential Expression | `rna-seq` |
| RNA | Single-cell RNA-seq | `scrna-seq` |
| Epigenetics | ChIP-seq / CUT&RUN | `chip-seq` |
| Epigenetics | Whole-genome Bisulfite WGBS | `wgbs` |
| Microbiome | Metagenomics | `metagenomics` |
| Microbiome | 16S rRNA | `16s` |
| Genetic Epi | Mendelian Randomization | `mendelian-randomization` |

### Reference Knowledge

| File | Content |
|------|---------|
| `references/study_designs.md` | Decision matrix for 14 NGS experimental designs |
| `references/patterns.md` | Reusable Nextflow/Snakemake/WDL code patterns |
| `references/sharp_edges.md` | Known pitfalls, edge cases, and avoidance strategies |
| `references/validations.md` | Output quality validation rules and checklists |

### Semantic Search

A lightweight retrieval-augmented layer over the knowledge base. 79 document chunks (65 from references + 14 pipeline JSONs) are embedded and indexed, enabling natural-language queries like "how to handle batch effects" or "which pipelines need IDR" with sub-millisecond retrieval latency and full source traceability (`source_file:L123-L456`).

**True semantic vectors**: embeddings come from `BAAI/bge-small-zh-v1.5` (512-dim, Chinese-optimized) run locally via `fastembed` (ONNX, no GPU / no API key). The first run downloads the model through the HF mirror (`HF_ENDPOINT=https://hf-mirror.com` with `HF_HUB_DISABLE_XET=1`) into `python/.hf_cache`; afterwards it works offline. `SemanticSearcher` uses this embedder by default, falling back to a deterministic hash embedder (test-only) only when `fastembed` is not installed.

Implementation: `python/vector_store/` — `chunker.py` + `embedder.py` + `chroma_client.py` (NumPy + sklearn cosine) + `fastembed_provider.py`. Dependencies: `fastembed`, `numpy`, `scikit-learn`.

Rebuild the index: `python python/vector_store/build_semantic_index.py --build`.

**Retrieval quality** (evaluated with the bge-small-zh-v1.5 index): MR tool-variable multi-word query hits TOP1/TOP2 at 0.714/0.694; family trio *de novo* query correctly resolves to `wgs-germline/trio`; Mutect2 resolves to `wgs-somatic` (0.715). Residual misses are mostly knowledge-coverage gaps (e.g. thin `qc_standards.md`), not embedding issues.

**Wired into the agent (OPTIMIZATION #6)**: `ResearchAgent.plan()` now queries the semantic KB and records the top pipeline recommendation plus the top-3 hits; `run()` passes it into `search_pipeline()` via a new direct-ID load path (`_load_pipeline`), so retrieval genuinely drives the business call. Decision rule is keyword-authoritative with semantic fallback: a stable keyword hit wins (avoids `pipeline_ids` tag noise on shared chunks, e.g. rare-variant blocks tagged `family-trio-wgs`); the semantic recommendation only drives when keywords miss (novel wording / newly added pipelines), and any divergence is surfaced in `format_result()`. Python 3.11 compatibility: the f-string backslash expressions in `export_workflow` were replaced with pre-bound defaults (PEP 701 is 3.12+).

**Step 2b wired into the code**: the generic 3-round web search described in the workflow diagram is now implemented in the Python layer. When *both* the keyword match and the semantic recommendation miss (semantic top-aggregate score < `SEMANTIC_MIN_SCORE = 0.45`, calibrated on real queries: true hits ≥ 0.66, blind-spot fallbacks ≥ 0.536, off-topic ~0.40), `ResearchAgent.plan()` flags `uncovered_domain` and `run()` emits a `WebFallbackPlan` — a ready-to-use 3-round `web_search` plan (find authoritative source → drill into best source → supplement QC metrics), which the calling LLM agent executes per SKILL.md and feeds back into the KB (Step 5). The Python layer materializes the plan + grounded-context contract; it makes no network call itself.

### Evaluation

6 deterministic metrics for automated Skill output evaluation, zero API calls, one command. Evaluated with **qwen3:14b** (local Ollama, `think=False`, `temperature=0.3`) on 20 test cases (14 pipelines + 6 cross-cutting/edge cases; the case set now has 30 entries — the extended run is reported in its own section below), with an ablation comparison of **Prompt + Skill** (SKILL.md as system prompt) vs **Prompt Only** (neutral system prompt) on the no-internet baseline — isolating the pure textual contribution of SKILL.md, so the difference between the two groups comes solely from the Skill instructions (cleaner controlled comparison).

**Ablation results** (Prompt + Skill vs Prompt Only, no-internet baseline):

| Metric | + Skill | Prompt Only | Δ |
|--------|---------|-------------|---|
| Pipeline Selection Accuracy (18 pipeline cases) | 94.4% (17/18) | 88.9% (16/18) | +5.5 pt |
| Knowledge Grounding Rate | 96.8% | 94.0% | +2.9 pt |
| Parameter Correctness | 100% (15 params) | 100% (3 params) | 0 |
| Reference Coverage | 89.5% (17/19) | 68.4% (13/19) | +21.1 pt |
| Schema Validity | N/A (0/0) | N/A (0/0) | — |
| **Overall (4 valid metrics)** | **95.2%** | **87.8%** | **+7.4 pt** |
| Workflow Completeness | 75.6% | 72.0% | +3.7 pt |

The pipeline denominator is 18, not 20: TC-014 and TC-017 have no expected pipeline and are scored separately as out-of-scope abstention. Schema validity is 0/0 on this run and is excluded from the overall. The one-case pipeline difference is **not significant** (exact McNemar p = 1.0; Wilson 95% CI 74.2–99.0% vs 67.2–96.9%); see [`evaluation/results/v1.1.0_report.md`](evaluation/results/v1.1.0_report.md) for the corrected semantics and the MDE floor.

```bash
cd python/evaluation
python runner.py                     # 5-metric evaluation on results/outputs.json
python runner.py results/outputs_qwen3_14b.json -o results/report_qwen3_14b_baseline.json
python runner.py results/outputs_qwen3_14b_noskill.json -o results/report_qwen3_14b_noskill.json

# 30-case extended run (see the section below): regenerate answers, scores, stats, report
python generate_outputs.py --cases benchmarks/test_cases.json --out results/outputs_ext30_skill.json --arm skill
python generate_outputs.py --cases benchmarks/test_cases.json --out results/outputs_ext30_noskill.json --arm noskill
python runner.py results/outputs_ext30_skill.json -o results/report_ext30_skill.json
python runner.py results/outputs_ext30_noskill.json -o results/report_ext30_noskill.json
python analyze_ext30.py              # paired statistics -> results/report_ext30_stats.json
python ../../evaluation/metrics/render_ext30_report.py   # -> evaluation/results/ext30_report.md
```

Workflow Completeness (6th metric) is evaluated separately via `metrics/workflow_completeness.py` — 18 pipeline cases × standard step coverage (82 standard steps in total).

**Provenance of the table above** — every number traces to a committed file under `python/evaluation/results/`:

| Table column | Raw model outputs | Report file | Verified values |
|---|---|---|---|
| + Skill | `outputs_qwen3_14b.json` | `report_qwen3_14b_baseline.json` | 0.90 / 0.9684 / 1.0 / 0.8947 / 1.0 → overall **0.9526** |
| Prompt Only | `outputs_qwen3_14b_noskill.json` | `report_qwen3_14b_noskill.json` | 0.85 / 0.9395 / 1.0 / 0.6842 / 1.0 → overall **0.8947** |
| Workflow Completeness (+ Skill) | — | `workflow_completeness_qwen3_14b_fix4.json` | 62 / 82 standard steps = **0.7561** |
| Workflow Completeness (Prompt Only) | — | `workflow_completeness_qwen3_14b_noskill_fix4.json` | 59 / 82 = **0.7195** |

Metric order in each row: pipeline selection / knowledge grounding / parameter correctness / reference coverage / schema validity.

**Rendered report**: `evaluation/results/v1.0.0_report.md` is generated from those files by `python evaluation/metrics/render_report_from_results.py` (no GPU, no network). It records the numerator and denominator of every cell and flags the degenerate rows, which the table above can't show: **Schema Validity is 0/0 on this run** (stored as 100% because there was nothing to check), **Parameter Correctness rests on 15 vs 3 extractable parameters**, and **Pipeline Selection Accuracy differs by a single case out of 20** (both arms miss TC-009 and TC-017). The rows with comparable denominators — Reference Coverage 17/19 vs 13/19 and Knowledge Grounding 368/380 vs 326/347 — are the defensible ones. Quote the Overall number together with that caveat.

**Do not run `evaluation/metrics/report.py`**: it is a formatter whose `__main__` block still carries illustrative placeholder numbers (0.60 / 0.95 / …) that no run produced, and calling it overwrites `results/v1.0.0_report.md` with them. Use the renderer above.

Other files in `results/` are **different runs and should not be mixed with the table above**: `report.json` (overall 0.9823) and `comparison_report_final.json` are earlier comparisons whose input outputs are not recorded inside the report files themselves. The table quoted here is the citable one because it is the strictest controlled setting — same model, no-internet baseline, SKILL.md being the only difference.

Implementation: `python/evaluation/` — 30 test cases × 6 deterministic metrics, no external API, no manual annotation. The 20-case table above stays as the published v1.1.0 run; the 10 cases added on 2026-11-19 (TC-021…TC-030) are reported separately below, because they change the conclusion. They cover RNA-seq batch effect (TC-021), tumour-only somatic WGS without a matched normal (TC-022), low-biomass 16S with a contaminated extraction blank (TC-023), joint genotyping of hg19 BAMs with hg38 samples (TC-024), single-sample `-ERC GVCF` semantics (TC-025), cross-ancestry polygenic risk scores from European summary statistics (TC-026), ChIP-seq with one biological replicate and whether IDR still applies (TC-027), 10x Multiome and PacBio HiFi structural variants as uncovered questions (TC-028–TC-029), and a 3,000-case/30,000-control GWAS tested with PLINK's chi-square (TC-030).

#### Extended 30-case run (answers generated 2026-11-19, scored 2026-11-20): the skill effect is not measurable

Same model and settings as above (local Ollama `qwen3:14b`, `think=False`, `temperature=0.3`); the only difference is SKILL.md as the system prompt (7,475 characters, `system_prompt_sha256` 33d105c1…) versus a neutral one (158 characters, 3851f8ec…). Generation took 2,353.3 s (skill) and 2,208.8 s (prompt only). Provenance: `results/outputs_ext30_*_meta.json`; raw per-arm scores: `results/report_ext30_{skill,noskill}.json`; paired statistics: `results/report_ext30_stats.json`, regenerated by `python analyze_ext30.py`, which reuses `runner._to_predictions` and the metric modules instead of re-scoring anything. A rendered companion to this section is committed at [`evaluation/results/ext30_report.md`](evaluation/results/ext30_report.md) (`python evaluation/metrics/render_ext30_report.py`): it reads those four JSONs and the two meta files, prints every numerator and denominator, and writes a MISSING line instead of a value when an artifact is absent — it contains no hard-coded result number, and re-running it is byte-reproducible.

| Metric | + Skill | Prompt Only | What the paired test says |
|---|---|---|---|
| Pipeline Selection (runner, each arm's own denominator) | 73.08% (19/26) | 80.77% (21/26) | not a paired comparison — see below |
| Pipeline Selection on the 22 cases both arms resolved | 19/22 | 19/22 | McNemar b/c = 1/1, p = 1.0 |
| Pipeline Selection, all 26 in-scope (unresolved counts as wrong) | 19/26 | 21/26 | b/c = 1/3, p = 0.625 |
| Pipeline Selection, lenient (expected id present in the text) | 19/26 | 22/26 | b/c = 0/3, p = 0.25 |
| Reference Coverage, per-case any-source hit | 17/23 | 18/23 | b/c = 4/5, p = 1.0 |
| Knowledge Grounding (entity-level, not paired) | 637/658 = 96.81% | 721/772 = 93.39% | no per-case pairing defined |
| Parameter Correctness | 100% (12 checked) | 100% (17 checked) | cannot separate the arms |
| Schema Validity | 0/0, excluded | 0/0, excluded | the prompt never asks for JSON |
| Overall (4 valid metrics) | 83.55% | 83.72% | — |

Four findings, all of them negative:

1. **The apparent −9.5 pt skill deficit is an extractor artifact.** `runner.py --baseline` subtracts two percentages computed on *different* 26-case denominators: the keyword/regex extractor resolved 4 in-scope answers in the skill arm versus 2 in the prompt-only arm (`extractor_audit.unparsed_in_scope`). On the 22 cases both arms resolved, the arms are 19/22 vs 19/22. The same asymmetry, plus per-case pairing, does not reproduce the earlier +21.1 pt Reference Coverage gain: source-level coverage here is 18/28 vs 17/28, and the paired per-case comparison is 17/23 vs 18/23, p = 1.0.
2. **For pipeline selection this run cannot resolve a difference at all.** The discordant counts are 2, 4 and 3 across the three modes, so even a unanimous split gives p = 0.5, 0.125 and 0.25 respectively (`paired_resolution` in every row) — no outcome of this size reaches α = 0.05. Reference coverage pairs 9 discordant cases and could in principle resolve an 8:1 split (p = 0.039); the observed 4:5 gives p = 1.0. The unpaired sensitivity floor at n = 26 is a 38.9 pt gap, which is why the paired resolution and not that number is what any claim must be checked against. The honest statement is therefore "no measurable skill effect in either direction", not "the skill hurts".
3. **Neither arm abstains on out-of-scope questions.** On the 4 cases with no expected pipeline the skill arm answered 1 and left 3 unresolved, the prompt-only arm answered 3 and left 1 unresolved; abstention credit went to nobody (0/4 in both arms), so the `__uncovered__` path in `workflow_accuracy.py` is still untested against real model output.
4. **Several declared case fields are never scored, so their 100% means less than it looks.** `must_flag_traps` and `must_apply_validations` are present on all 30 cases and referenced by no metric module. `must_include_params` declares 37 parameter constraints, while the parameter metric only range-checks occurrences of its 13 hardcoded parameter names that happen to appear in the text (12 in the skill arm, 17 in the baseline arm), and its `PIPELINES_DIR` constant (`metrics/parameter_correctness.py:12`) points at a directory that does not exist and is never read. 100% reads as "nothing extractable was out of range", not "the declared parameters were used".

Quote the v1.1.0 table above for the published run and this section for anything on 30 cases. Neither is a demonstrated skill gain: on the 20-case run the single-case pipeline difference was already non-significant (p = 1.0), and on the 30-case run pairing removes the apparent effect in both directions.

### Agentic Workflow

The Skill exposes a **Planning → Tool Calling → Execution** loop through 4 tools:

| Tool | Function |
|------|----------|
| `search_pipeline` | Match the best pipeline from the knowledge base |
| `check_traps` | Retrieve known pitfalls for a given pipeline |
| `validate_script` | Run validation rules against generated scripts |
| `export_workflow` | Generate executable Nextflow DSL2 `.nf` scripts |

Implementation: `python/agent/`

### Self-Updating

The Skill automatically writes newly discovered pipeline information back into the repository (Step 5 in SKILL.md): new `references/` sections, new `src/data/pipelines/*.json` files, and index registration.

### Build System

`scripts/build-pipelines.ts` generates 5 study-design pipeline JSONs from structured templates on each build. 9 standard omics pipelines are hand-curated JSON. All 14 are unified into `index.ts` and `versions.json` for the FlowSeq frontend.

---

## FlowSeq — Pipeline Browser & Site

An interactive web frontend for browsing and validating all Skill content.

### Features

- **Category Navigation**: Supports four major domains — DNA Analysis, RNA Analysis, Epigenetics, Microbiome — each with fine-grained subcategories (e.g. DNA → Germline / Somatic / Association, Microbiome → Metagenomics / 16S Amplicon), filter pipelines by category
- **Smart Search**: `Ctrl+K` shortcut opens search overlay with fuzzy pipeline name matching
- **Pipeline Details**: Each pipeline displays standardized analysis step chains, recommended tools with versions, and authoritative references with clickable DOIs
- **i18n**: Toggle between English / Chinese via `EN` / `中` button in the top-right corner for instant UI language switching
- **Pipeline Compare**: Select multiple pipelines for side-by-side toolchain comparison
- **Local Launch**: Double-click `FlowSeq.lnk` for one-click startup — auto-installs dependencies and opens the browser
- **Export**: Export pipeline info as Markdown or JSON

### Tech Stack

| Layer | Choice |
|-------|--------|
| Framework | React 19 + TypeScript |
| Build | Vite |
| Markdown | react-markdown + remark-gfm |
| Styling | Tailwind CSS 4 |
| State | Zustand 5 |
| Routing | React Router 7 |
| i18n | Custom Context (lightweight) |
| Deployment | GitHub Pages + Actions |

### Local Usage

**Dev mode (recommended):**

```bash
npm run dev -- --host --open
```

Hot reload enabled. Double-click `FlowSeq.lnk` for one-click launch.

**Production build:**

```bash
npm install
npm run build
npm run preview
```

---

## Project Structure

```
├── SKILL.md                      # Skill instruction file
├── README.md                     # English documentation
├── README_zh.md                  # Chinese documentation
├── references/                   # Knowledge base documents
│   ├── study_designs.md
│   ├── patterns.md
│   ├── sharp_edges.md
│   ├── validations.md
│   ├── schema.md
│   ├── search_strategies.md
│   ├── qc_standards.md
│   ├── category_tree.md
│   └── architecture.md
├── python/                       # Python modules (RAG + Agent)
│   ├── vector_store/             # Semantic search (chunker + embedder + vector store)
│   ├── agent/                    # Agent workflow (tools + research agent)
│   └── evaluation/               # Evaluation framework (benchmarks + metrics)
├── scripts/
│   └── build-pipelines.ts        # Build-time pipeline JSON generation
├── src/                          # FlowSeq frontend
│   ├── i18n/                     # Internationalization (en / zh)
│   ├── components/               # PipelineMarkdown, SourceSwitcher, SearchOverlay, etc.
│   ├── pages/                    # HomePage, PipelinePage, DocsPage, ComparePage
│   ├── data/pipelines/           # 14 pipeline JSON + index.ts + versions.json
│   ├── store/                    # Zustand state management
│   └── types/                    # TypeScript type definitions
├── .github/workflows/
│   └── deploy.yml                # Auto deploy to GitHub Pages
├── public/
└── start_flowseq.bat             # One-click dev server launcher (Windows)
```

---

### Agent & RAG Integration

The current implementation exposes bioinformatics capabilities through a local Python tool registry, enabling agent-based workflow orchestration. Its modular architecture is transport-agnostic and can be seamlessly extended to MCP, REST APIs, or other agent protocols without modifying the underlying knowledge layer. Semantic retrieval (RAG) can be integrated as a retrieval backend while preserving the repository's knowledge-constrained workflow generation paradigm.

---

## External baselines

`docs/external_baselines.md` collects published numbers we can be compared
against, each re-checked against the source on 2026-11-18 with its citation and
table, plus an explicit list of what is *not* comparable (task domain, outcome
metric, denominator, significance correction). It also records two negative
results: there is no published quantitative skill-ablation baseline in
bioinformatics yet, and several citation leads we went in to verify
(an nf-core "mass deployment" paper, two named reproduction tools) turned out
to have no publication record at all, so they are listed as do-not-cite.

## How to cite

Machine-readable metadata lives in `CITATION.cff` at the repo root (GitHub renders it in the
sidebar). If you reuse the pipeline knowledge base, please also credit the upstream
pipelines it indexes.

```bibtex
@software{wu2026flowseq,
  author  = {Wu, Yiting},
  title   = {FlowSeq: A knowledge-constrained AI skill for standardized, traceable and reproducible bioinformatics workflow generation},
  url     = {https://github.com/fakenice/bioinformatics-workflows}
}
```

---

## License

MIT
