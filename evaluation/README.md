# FlowSeq Evaluation Framework

## Why Evaluation Matters

A Skill is not a demo. It is a **claim**.

The claim is: "FlowSeq produces better bioinformatics workflow recommendations than a bare LLM."

This framework proves that claim with **quantitative evidence**, not anecdotes. It follows the evaluation philosophy of academic benchmarking: define metrics, establish baselines, measure improvement, and enable reproducible comparison.

## Architecture

```
evaluation/
├── README.md                    # This file
├── benchmarks/
│   └── test_cases.json          # 20 standardized test scenarios
├── metrics/
│   ├── workflow_accuracy.py     # Pipeline selection correctness
│   ├── hallucination.py         # Fabrication detection
│   ├── parameter_correctness.py # Tool parameter accuracy
│   ├── reference_coverage.py    # Citation density
│   ├── expert_evaluation.py     # Blind expert review protocol
│   └── report.py                # Aggregated report generator
└── results/
    └── v1.0.0_report.md         # Evaluation report
```

## Five Metrics

### 1. Workflow Selection Accuracy (★★★★★)
**Question**: Does the system pick the right pipeline for the right scenario?

Given 20 real-world bioinformatics scenarios (covering all 14 pipelines plus cross-domain edge cases), measure the exact-match rate between recommended pipeline ID and ground truth.

**Expected improvement**: ≥30% over bare LLM (LLMs routinely mismatch WES vs WGS or recommend non-existent pipelines).

### 2. Hallucination Reduction (★★★★★)
**Question**: Does the system fabricate tool versions, Docker images, or parameter names?

Bare LLMs frequently hallucinate versions like `GATK 5.0`, Docker tags like `biocontainers/gatk:latest`, or tools that don't exist. FlowSeq constrains output to a verified knowledge base of 14 pipeline JSON files + 2,500 lines of references.

**Measured across**: tools, versions, Docker images, parameters, QC thresholds.

**Expected improvement**: ≥50% reduction in hallucination rate.

### 3. Parameter Correctness (★★★★☆)
**Question**: Do the recommended parameters match official documentation?

Parameters like `--twopassMode Basic` for STAR, `resolution=0.5` for Seurat, or `--mind 0.03` for PLINK are verified against source documentation embedded in the pipeline definitions.

**Expected improvement**: ≥30% over bare LLM.

### 4. Reference Coverage (★★★★☆)
**Question**: Are outputs traceable to verifiable sources?

Bare LLMs rarely cite sources. FlowSeq embeds references (official docs, peer-reviewed papers, community pipelines) in every pipeline definition.

**Expected improvement**: ∞ (bare LLM → 0 refs; FlowSeq → 2–4 refs/case).

### 5. Expert Evaluation (★★★★★)
**Question**: Would a domain expert trust these recommendations?

Blind review protocol: 2–3 bioinformatics practitioners receive anonymized output pairs (System A / System B), rate them across 5 dimensions on a 1–5 scale. The evaluator does not know which is FlowSeq and which is bare LLM.

**Rubric dimensions**: Pipeline Suitability (30%), Tool Version Accuracy (20%), Parameter Appropriateness (20%), QC Thresholds (15%), Explainability (15%).

## Test Case Design

20 test cases covering:

| Category | Cases | Pipelines Covered |
|----------|-------|-------------------|
| DNA (germline/somatic/GWAS/MR/PRS/rare) | 9 | 8 |
| RNA (bulk + single-cell) | 3 | 2 |
| Epigenetic (ChIP-seq + WGBS) | 3 | 2 |
| Microbiome (metagenomics + 16S) | 2 | 2 |
| Cross-domain / edge cases | 3 | — |

Each test case includes:
- Realistic scenario description (as a user would phrase it)
- Expected pipeline ID (ground truth)
- Expected tools, versions, Docker images, QC thresholds

## Usage

```bash
# Run individual metric evaluators
python evaluation/metrics/workflow_accuracy.py
python evaluation/metrics/hallucination.py
python evaluation/metrics/parameter_correctness.py
python evaluation/metrics/reference_coverage.py

# Generate aggregate report
python evaluation/metrics/report.py
```

## Design Principles

1. **Real data only**: All test cases map to actual pipeline JSONs. No synthetic scenarios.
2. **Blind comparison**: Expert evaluation is double-blind. System A/B labels are randomized per evaluator.
3. **Reproducible**: Every metric is a deterministic Python script, not a prompt-based judgment.
4. **Minimal but sufficient**: 20 cases is enough for statistical significance, small enough for expert review.

## Roadmap

- [ ] v1.0: Framework + test cases + all 5 metric scripts
- [ ] v1.1: First evaluation run with actual LLM comparison data
- [ ] v1.2: Expert evaluation with 2–3 domain practitioners
- [ ] v2.0: Automated CI integration — run metrics on every pipeline update
