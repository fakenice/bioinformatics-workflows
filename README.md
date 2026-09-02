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

6 deterministic metrics for automated Skill output evaluation, zero API calls, one command. Evaluated with **qwen3:14b** (local Ollama, `think=False`, `temperature=0.3`) on 20 test cases (14 pipelines + 6 cross-cutting/edge cases), with an ablation comparison of **Prompt + Skill** (SKILL.md as system prompt) vs **Prompt Only** (neutral system prompt) on the no-internet baseline — isolating the pure textual contribution of SKILL.md, so the difference between the two groups comes solely from the Skill instructions (cleaner controlled comparison).

**Ablation results** (Prompt + Skill vs Prompt Only, no-internet baseline):

| Metric | + Skill | Prompt Only | Δ |
|--------|---------|-------------|---|
| Pipeline Selection Accuracy | 90.0% | 85.0% | +5.0% |
| Knowledge Grounding Rate | 96.8% | 94.0% | +2.9% |
| Parameter Correctness | 100% | 100% | 0 |
| Reference Coverage | 89.5% | 68.4% | +21.1% |
| Schema Validity | 100% | 100% | 0 |
| **Overall (5 metrics)** | **95.3%** | **89.5%** | **+5.8%** |
| Workflow Completeness | 75.6% | 72.0% | +3.7% |

```bash
cd python/evaluation
python runner.py                     # 5-metric evaluation on results/outputs.json
python runner.py results/outputs_qwen3_14b.json -o results/report_qwen3_14b_baseline.json
python runner.py results/outputs_qwen3_14b_noskill.json -o results/report_qwen3_14b_noskill.json
```

Workflow Completeness (6th metric) is evaluated separately via `metrics/workflow_completeness.py` — 18 pipeline cases × standard step coverage (82 standard steps in total).

Implementation: `python/evaluation/` — 20 test cases × 6 deterministic metrics, no external API, no manual annotation.

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

## License

MIT
