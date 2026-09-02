"""
FlowSeq Agent Tools

Four tools that enable LLM agents to interact with the FlowSeq knowledge base.
Each tool has a clear schema, input/output contract, and boundary condition.
Designed for use in Planning → Tool Calling → Execution workflows.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────────────────────
# Data Models (Pydantic-style — minimal dependency footprint)
# ──────────────────────────────────────────────────────────────

@dataclass
class ToolInfo:
    name: str
    version: str
    params: str = ""
    docker: str = ""
    notes: str = ""


@dataclass
class PipelineStep:
    id: str
    name: str
    description: str
    tools: list[ToolInfo] = field(default_factory=list)
    notes: str = ""


@dataclass
class PipelineReference:
    title: str
    url: str
    ref_type: str  # "official" | "paper" | "community"
    doi: str = ""


@dataclass
class PipelineSource:
    id: str
    name: str
    source_type: str  # "official" | "community" | "paper"
    url: str
    steps: list[PipelineStep] = field(default_factory=list)
    references: list[PipelineReference] = field(default_factory=list)


@dataclass
class PipelineDefinition:
    id: str
    name: str
    name_zh: str
    category: str  # "dna" | "rna" | "epigenetic" | "microbiome"
    tags: list[str] = field(default_factory=list)
    overview: str = ""
    overview_en: str = ""
    icon: str = ""
    version: str = "1.0.0"
    sources: list[PipelineSource] = field(default_factory=list)


@dataclass
class SharpEdge:
    edge_id: str
    severity: str  # "critical" | "high" | "medium" | "low"
    summary: str
    symptoms: list[str] = field(default_factory=list)
    solution: str = ""
    pipeline_ids: list[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    rule_id: str
    passed: bool
    message: str
    line: int = -1
    severity: str = "warning"


# ──────────────────────────────────────────────────────────────
# Tool Definitions
# ──────────────────────────────────────────────────────────────

# Mapping from scenario keywords to pipeline IDs
# Based on 14 real pipelines in src/data/pipelines/
SCENARIO_KEYWORD_MAP: dict[str, list[str]] = {
    "family-trio-wgs": ["trio", "家系", "de novo", "denovo", "先证者", "父母", "遗传病", "pedigree", "mendelian"],
    "gwas": ["gwas", "病例对照", "case-control", "关联分析", "association", "全基因组关联", "case control"],
    "mendelian-randomization": ["孟德尔随机化", "mendelian randomization", "mr", "两样本", "two-sample", "因果", "causal", "ivw", "mr-egger"],
    "prs": ["prs", "多基因风险", "polygenic risk", "polygenic score", "风险预测", "risk prediction", "ldpred", "prsice"],
    "rare-variant": ["罕见变异", "rare variant", "skat", "burden", "聚合", "aggregation", "gene-based"],
    "wgs-germline": ["wgs", "全基因组", "whole genome", "germline", "种系", "germline variant", "gatk haplotypecaller"],
    "wgs-somatic": ["somatic", "体细胞", "tumor", "肿瘤", "mutect", "配对", "tumor-normal", "cancer"],
    "wes": ["wes", "外显子", "exome", "捕获", "capture", "acmg", "致病性分级"],
    "rna-seq": ["rna-seq", "转录组", "transcriptome", "差异表达", "differential expression", "deseq2", "edger", "go", "kegg"],
    "scrna-seq": ["单细胞转录组", "单细胞测序", "单细胞分析", "单细胞", "single cell", "single-cell", "scRNA", "scrna-seq", "seurat", "cell ranger", "聚类", "umap", "细胞注释", "cell type"],
    "chip-seq": ["chip-seq", "chip", "转录因子", "tf", "histone", "组蛋白", "macs2", "motif", "homer", "peak"],
    "wgbs": ["wgbs", "甲基化", "methylation", "bismark", "bisulfite", "亚硫酸盐", "dna methylation", "dss", "methylkit"],
    "metagenomics": ["宏基因组", "metagenomic", "肠道菌群", "gut microbiome", "metaphlan", "humann", "kneaddata"],
    "16s": ["16s", "16s rrna", "扩增子", "amplicon", "qiime2", "dada2", "silva", "alpha多样性", "ancom-bc"],
}

# Pipeline-to-traps mapping (pipeline_id → sharp edge IDs from sharp_edges.md)
# Only reference edge IDs that actually exist in references/sharp_edges.md.
# Universal traps (non-resumable-pipeline, unstable-sort-order) are appended
# automatically by check_traps() and need not be listed here.
PIPELINE_TRAP_MAP: dict[str, list[str]] = {
    "family-trio-wgs": ["symlink-container-failure", "vqsr-chain-vs-parallel", "gatk-bqsr-wrong-sites", "gatk-gvcf-mode-misuse", "bqsr-incomplete-known-sites", "reference-genome-mismatch"],
    "gwas": ["reference-genome-mismatch", "sample-contamination"],
    "wgs-germline": ["symlink-container-failure", "vqsr-chain-vs-parallel", "gatk-bqsr-wrong-sites", "gatk-gvcf-mode-misuse", "bqsr-incomplete-known-sites", "reference-genome-mismatch", "gcnv-inconsistent-counts", "gcnv-scaffold-contamination"],
    "wgs-somatic": ["reference-genome-mismatch", "sample-contamination", "manta-missing-pass-filter"],
    "wes": ["symlink-container-failure", "gatk-bqsr-wrong-sites", "reference-genome-mismatch"],
    "rna-seq": [],
    "scrna-seq": [],
    "chip-seq": ["symlink-container-failure"],
    "wgbs": ["reference-genome-mismatch"],
    "metagenomics": [],
    "16s": [],
    "mendelian-randomization": [],
    "prs": ["reference-genome-mismatch"],
    "rare-variant": [],
}

# Traps that apply to every pipeline (edge IDs present in sharp_edges.md)
UNIVERSAL_EDGE_IDS = ["non-resumable-pipeline", "unstable-sort-order"]

# Validation rules (from validations.md)
VALIDATION_RULES: list[dict] = [
    {"id": "val-001", "pattern": r"biocontainers/|nfcore/", "message": "Container image must use biocontainers or nfcore namespace", "severity": "critical"},
    {"id": "val-002", "pattern": r"set -euo pipefail", "message": "Shell scripts must include 'set -euo pipefail'", "severity": "critical"},
    {"id": "val-003", "pattern": r"cpus?\s*[\d]+|cpu\s*\d+", "message": "Each process must declare CPU limit", "severity": "high"},
    {"id": "val-004", "pattern": r"memory\s*['\"][\d.]+[GM]B", "message": "Each process must declare memory limit", "severity": "high"},
    {"id": "val-005", "pattern": r"time\s*['\"][\dhms]+", "message": "Each process must declare time limit", "severity": "medium"},
    {"id": "val-006", "pattern": r"container\s*['\"]", "message": "Each process must declare a container image", "severity": "high"},
    {"id": "val-007", "pattern": r"publishDir", "message": "Output must use publishDir for persistence", "severity": "medium"},
    {"id": "val-008", "pattern": r"GRCh38|hg38|GRCh37|hg19", "message": "Reference genome version must be explicitly declared", "severity": "critical"},
    {"id": "val-009", "pattern": r"(/home/|/Users/|C:\\)", "message": "Hard-coded paths detected — use parameterized paths", "severity": "critical"},
    {"id": "val-010", "pattern": r"dbsnp|gnomAD|1000g|1000genomes", "message": "Known resource files must be declared as input channels", "severity": "high"},
]

# ──────────────────────────────────────────────────────────────
# Tool 1: search_pipeline
# ──────────────────────────────────────────────────────────────


def search_pipeline(scenario: str, knowledge_base_dir: Optional[str] = None) -> Optional[PipelineDefinition]:
    """
    Match a user scenario to the best pipeline in the knowledge base.

    Args:
        scenario: Natural language description of the analysis need.
        knowledge_base_dir: Path to src/data/pipelines/ (auto-detected if None).

    Returns:
        Matching PipelineDefinition or None if no match found.
    """
    scenario_lower = scenario.lower()

    # Score each pipeline by keyword matches, weighted by keyword length so
    # specific terms ("single cell", "单细胞") outweigh generic ones
    # ("转录组", "rna-seq"). Ties are broken by specificity instead of
    # dict insertion order.
    scores: dict[str, float] = {}
    for pipeline_id, keywords in SCENARIO_KEYWORD_MAP.items():
        score = sum(len(kw) for kw in keywords if kw.lower() in scenario_lower)
        if score > 0:
            scores[pipeline_id] = score

    if not scores:
        return None

    # Return the highest-scoring pipeline
    best_id = max(scores, key=scores.get)  # type: ignore[arg-type]

    # Load pipeline JSON for full definition
    if knowledge_base_dir is None:
        knowledge_base_dir = str(
            Path(__file__).parent.parent.parent / "src" / "data" / "pipelines"
        )

    import json
    pipeline_path = Path(knowledge_base_dir) / f"{best_id}.json"
    if not pipeline_path.exists():
        return None

    with open(pipeline_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert JSON to PipelineDefinition
    sources = []
    for src_data in data.get("sources", []):
        steps = []
        for step_data in src_data.get("steps", []):
            tools = [
                ToolInfo(
                    name=tool.get("name", ""),
                    version=tool.get("version", ""),
                    params=tool.get("params", ""),
                    docker=tool.get("docker", ""),
                    notes=tool.get("notes", ""),
                )
                for tool in step_data.get("tools", [])
            ]
            steps.append(PipelineStep(
                id=step_data.get("id", ""),
                name=step_data.get("name", ""),
                description=step_data.get("description", ""),
                tools=tools,
                notes=step_data.get("notes", ""),
            ))
        refs = [
            PipelineReference(
                title=ref.get("title", ""),
                url=ref.get("url", ""),
                ref_type=ref.get("type", "official"),
                doi=ref.get("doi", ""),
            )
            for ref in src_data.get("references", [])
        ]
        sources.append(PipelineSource(
            id=src_data.get("id", ""),
            name=src_data.get("name", ""),
            source_type=src_data.get("type", "official"),
            url=src_data.get("url", ""),
            steps=steps,
            references=refs,
        ))

    return PipelineDefinition(
        id=data.get("id", best_id),
        name=data.get("name", ""),
        name_zh=data.get("nameZH", ""),
        category=data.get("category", ""),
        tags=data.get("tags", []),
        overview=data.get("overview", ""),
        overview_en=data.get("overviewEn", ""),
        icon=data.get("icon", ""),
        version=data.get("version", "1.0.0"),
        sources=sources,
    )


# ──────────────────────────────────────────────────────────────
# Tool 2: check_traps
# ──────────────────────────────────────────────────────────────


# Cache for parsed sharp edges: edge_id → SharpEdge
_SHARP_EDGE_CACHE: Optional[dict[str, "SharpEdge"]] = None


def _sharp_edges_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "references" / "sharp_edges.md"


def _load_sharp_edges() -> dict[str, "SharpEdge"]:
    """Parse references/sharp_edges.md into SharpEdge objects.

    Expected markdown format per entry:
        ## <Title>
        ### **Id**
        <edge-id>
        ### **Severity**
        <critical|high|medium|low>
        ### **Summary**
        <one line>
        ### **Symptoms**
        - bullet list
        ... (Why / Gotcha sections ignored)
        ### **Solution**
        <text>
    """
    global _SHARP_EDGE_CACHE
    if _SHARP_EDGE_CACHE is not None:
        return _SHARP_EDGE_CACHE

    edges: dict[str, "SharpEdge"] = {}
    md_path = _sharp_edges_path()
    if not md_path.exists():
        _SHARP_EDGE_CACHE = edges
        return edges

    import re
    text = md_path.read_text(encoding="utf-8")
    # Split into entry blocks at level-2 headings
    blocks = re.split(r"^## ", text, flags=re.MULTILINE)[1:]

    def _section(block: str, name: str) -> str:
        m = re.search(
            r"^### \*{0,2}" + re.escape(name) + r"\*{0,2}\s*\n(.*?)(?=^### |\Z)",
            block, flags=re.MULTILINE | re.DOTALL,
        )
        return m.group(1).strip() if m else ""

    for block in blocks:
        edge_id = _section(block, "Id")
        if not edge_id:
            continue
        edge_id = edge_id.splitlines()[0].strip()
        severity = _section(block, "Severity").splitlines()[0].strip().lower() if _section(block, "Severity") else "medium"
        summary = _section(block, "Summary").splitlines()[0].strip()
        symptoms = [
            line.lstrip("- ").strip()
            for line in _section(block, "Symptoms").splitlines()
            if line.strip().startswith("-")
        ]
        solution = _section(block, "Solution")
        edges[edge_id] = SharpEdge(
            edge_id=edge_id,
            severity=severity,
            summary=summary,
            symptoms=symptoms,
            solution=solution,
            pipeline_ids=["all"],
        )

    _SHARP_EDGE_CACHE = edges
    return edges


def check_traps(pipeline_id: str) -> list[SharpEdge]:
    """
    Retrieve known pitfalls for a given pipeline.

    Args:
        pipeline_id: Pipeline identifier (e.g., "rna-seq", "gwas").

    Returns:
        Universal traps plus the pipeline-specific SharpEdges defined in
        references/sharp_edges.md.
    """
    edges = _load_sharp_edges()
    edge_ids = list(UNIVERSAL_EDGE_IDS)
    for eid in PIPELINE_TRAP_MAP.get(pipeline_id, []):
        if eid not in edge_ids:
            edge_ids.append(eid)

    return [edges[eid] for eid in edge_ids if eid in edges]


# ──────────────────────────────────────────────────────────────
# Tool 3: validate_script
# ──────────────────────────────────────────────────────────────


def validate_script(script: str, pipeline_id: str = "") -> list[ValidationResult]:
    """
    Validate a Nextflow/Snakemake script against 10 known rules.

    Args:
        script: The script content as a string.
        pipeline_id: Optional pipeline ID for context-specific rules.

    Returns:
        List of ValidationResult objects.
    """
    import re

    results: list[ValidationResult] = []

    for rule in VALIDATION_RULES:
        match = re.search(rule["pattern"], script, re.IGNORECASE)
        line_num = -1
        if match:
            # Find which line the match is on
            line_num = script[:match.start()].count("\n") + 1
        results.append(ValidationResult(
            rule_id=rule["id"],
            passed=match is not None,
            message=rule["message"],
            line=line_num,
            severity=rule.get("severity", "warning"),
        ))

    return results


# ──────────────────────────────────────────────────────────────
# Tool 4: export_workflow
# ──────────────────────────────────────────────────────────────


def export_workflow(
    pipeline_id: str,
    params: Optional[dict] = None,
    knowledge_base_dir: Optional[str] = None,
) -> str:
    """
    Generate a Nextflow DSL2 script from a pipeline definition.

    Args:
        pipeline_id: Pipeline identifier.
        params: Optional parameter overrides.
        knowledge_base_dir: Path to pipeline JSONs.

    Returns:
        Nextflow DSL2 script as a string.
    """
    if params is None:
        params = {}

    pipeline = search_pipeline(pipeline_id, knowledge_base_dir) if not pipeline_id.startswith("manual:") else None
    if pipeline is None:
        return f"// Error: pipeline '{pipeline_id}' not found in knowledge base."

    lines = ["#!/usr/bin/env nextflow", 'nextflow.enable.dsl = 2', ""]
    lines.append(f"// Generated by FlowSeq Agent")
    lines.append(f"// Pipeline: {pipeline.name} ({pipeline.id})")
    lines.append(f"// Category: {pipeline.category}")
    lines.append("")

    # Default params
    lines.append("params {")
    lines.append(f"    reads = '{params.get('reads', '\"data/*_{1,2}.fastq.gz\"')}'")
    lines.append(f"    outdir = '{params.get('outdir', '\"results\"')}'")
    lines.append(f"    genome = '{params.get('genome', '\"GRCh38\"')}'")
    lines.append("}")
    lines.append("")

    # Generate processes from pipeline steps
    for source in pipeline.sources:
        for step in source.steps:
            process_name = step.id.replace("-", "_")
            container = ""
            for tool in step.tools:
                if tool.docker:
                    container = tool.docker
                    break

            lines.append(f"process {process_name.upper()} {{")
            if container:
                lines.append(f"    container '{container}'")
            lines.append(f"    cpus 4")
            lines.append(f"    memory '16 GB'")
            lines.append(f"    time '8h'")
            lines.append("")
            lines.append(f"    input:")
            lines.append(f"        path reads")
            lines.append("")
            lines.append(f"    output:")
            lines.append(f"        path '*', emit: results")
            lines.append(f"        path '*.log', emit: logs")
            lines.append("")
            lines.append(f"    script:")
            lines.append(f"    \"\"\"")
            lines.append(f"    set -euo pipefail")
            lines.append(f"    # {step.name}: {step.description}")
            for tool in step.tools:
                lines.append(f"    # Tool: {tool.name} {tool.version}")
                if tool.params:
                    lines.append(f"    # Params: {tool.params}")
            lines.append(f"    \"\"\"")
            lines.append("}")
            lines.append("")

    # Workflow section
    lines.append("workflow {")
    process_names = []
    for source in pipeline.sources:
        for step in source.steps:
            pname = step.id.replace("-", "_").upper()
            process_names.append(pname)

    if process_names:
        lines.append(f"    {process_names[0]}(params.reads)")
        for i in range(1, len(process_names)):
            lines.append(f"    {process_names[i]}({process_names[i-1]}.out.results)")
    lines.append("}")
    lines.append("")

    return "\n".join(lines)
