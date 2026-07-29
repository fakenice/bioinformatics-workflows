"""
Semantic chunker for bioinformatics reference documents.

Splits markdown documents into meaningful chunks based on section boundaries,
not fixed token length. Each chunk carries metadata for precise source tracing.

Design: Each chunk = one semantic unit (a section, a sharp edge, a pattern,
a validation rule, or a pipeline step block). This enables "精准溯源" —
retrieval results can point to the exact source file and line range.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Chunk:
    """A single document chunk with full traceability metadata."""
    chunk_id: str
    content: str
    source_file: str          # e.g., "references/study_designs.md"
    section_title: str         # e.g., "## 家系/Trio 分析"
    line_start: int
    line_end: int
    pipeline_ids: list[str] = field(default_factory=list)  # Related pipelines
    tags: list[str] = field(default_factory=list)          # Keywords for filtering
    chunk_type: str = "paragraph"  # paragraph / code / table / list


@dataclass
class ChunkResult:
    """Result of chunking one document."""
    source_file: str
    total_chunks: int
    chunks: list[Chunk]


# ──────────────────────────────────────────────────────────────
# Pipeline-to-keywords mapping (for auto-tagging chunks)
# ──────────────────────────────────────────────────────────────

PIPELINE_KEYWORD_MAP: dict[str, list[str]] = {
    "family-trio-wgs": ["trio", "家系", "de novo", "denovo", "先证者", "遗传病", "pedigree", "mendelian", "slivar", "acmg", "hpo"],
    "gwas": ["gwas", "病例对照", "case-control", "关联", "association", "plink", "saige", "regenie", "pca", "ldsc"],
    "mendelian-randomization": ["孟德尔随机化", "mr", "ivw", "mr-egger", "two-sample", "工具变量", "多效性"],
    "prs": ["多基因风险", "prs", "polygenic", "ldpred2", "prsice", "c+t", "risk score"],
    "rare-variant": ["罕见变异", "rare variant", "skat", "burden", "聚合", "skat-o", "acat"],
    "wgs-germline": ["wgs", "全基因组", "germline", "种系", "gatk", "haplotypecaller", "bwa", "vqsr", "bqsr"],
    "wgs-somatic": ["somatic", "体细胞", "tumor", "肿瘤", "mutect2", "配对", "cancer", "strelka2", "maftools"],
    "wes": ["wes", "外显子", "exome", "捕获", "capture", "interval", "acmg"],
    "rna-seq": ["rna-seq", "转录组", "differential expression", "deseq2", "edger", "star", "salmon", "go", "kegg", "clusterprofiler"],
    "scrna-seq": ["单细胞", "single cell", "scRNA", "seurat", "cell ranger", "umap", "细胞注释", "monocle", "cellchat"],
    "chip-seq": ["chip-seq", "chip", "转录因子", "tf", "histone", "组蛋白", "macs2", "motif", "peak", "idr", "frip"],
    "wgbs": ["wgbs", "甲基化", "methylation", "bismark", "bisulfite", "dss", "dmp", "dmr", "亚硫酸盐"],
    "metagenomics": ["宏基因组", "metagenomic", "肠道", "gut", "metaphlan", "humann", "kneaddata", "宿主", "host"],
    "16s": ["16s", "16s rrna", "扩增子", "amplicon", "qiime2", "dada2", "silva", "alpha", "beta多样性", "ancom-bc", "lefse"],
}

# Generic keywords that apply across pipelines
CROSS_CUTTING_KEYWORDS = [
    "nextflow", "snakemake", "wdl", "docker", "container", "hpc", "slurm",
    "资源限制", "并行", "qc", "质量控制", "reproducible", "可复现",
    "set -euo pipefail", "biocontainers", "nf-core",
]


def _detect_pipeline_ids(text: str) -> list[str]:
    """Detect which pipelines a chunk is related to by keyword matching."""
    matched: list[str] = []
    text_lower = text.lower()
    for pipeline_id, keywords in PIPELINE_KEYWORD_MAP.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score >= 2:  # Require at least 2 keyword hits for a match
            matched.append(pipeline_id)
    return matched


def _detect_tags(text: str) -> list[str]:
    """Extract domain tags from chunk content."""
    tags: list[str] = []
    text_lower = text.lower()

    tag_rules = [
        ("qc", ["qc", "质量控制", "threshold", "阈值", "filter", "过滤"]),
        ("trap", ["trap", "陷阱", "pitfall", "gotcha", "error", "错误", "fail"]),
        ("code", ["nextflow", "snakemake", "wdl", "code", "template", "pattern"]),
        ("tool", ["gatk", "bwa", "star", "plink", "seurat", "macs2", "bismark", "qiime2"]),
        ("docker", ["docker", "container", "singularity", "biocontainers", "镜像"]),
        ("hpc", ["hpc", "slurm", "cluster", "grid", "batch", "云计算"]),
        ("reproducibility", ["reproducible", "可复现", "version", "版本"]),
    ]

    for tag, keywords in tag_rules:
        if any(kw in text_lower for kw in keywords):
            tags.append(tag)

    return tags


def chunk_markdown(file_path: str, content: str) -> ChunkResult:
    """
    Split a markdown document into semantic chunks at section boundaries.

    Splitting rules:
    - ## (level 2) headers always start a new chunk
    - ### (level 3) headers start a new chunk if previous chunk is large
    - Code blocks are kept intact (never split mid-block)
    - Tables are kept intact when possible
    """
    lines = content.split("\n")
    chunks: list[Chunk] = []
    chunk_index = 0
    current_start = 1
    current_lines: list[str] = []
    current_section = "Preamble"
    in_code_block = False

    for i, line in enumerate(lines, start=1):
        # Track code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block

        # Split at level-2 headers (never inside code blocks)
        if not in_code_block and line.startswith("## ") and current_lines:
            chunk_id = f"{Path(file_path).stem}_{chunk_index}"
            chunk_text = "\n".join(current_lines).strip()

            # Only create chunk if it has meaningful content
            if len(chunk_text) > 50:
                chunks.append(Chunk(
                    chunk_id=chunk_id,
                    content=chunk_text,
                    source_file=file_path,
                    section_title=current_section,
                    line_start=current_start,
                    line_end=i - 1,
                    pipeline_ids=_detect_pipeline_ids(chunk_text),
                    tags=_detect_tags(chunk_text),
                    chunk_type="code" if "```" in chunk_text else "paragraph",
                ))
                chunk_index += 1

            current_start = i
            current_lines = [line]
            current_section = line.strip("# ").strip()
        else:
            current_lines.append(line)

    # Don't forget the last chunk
    if current_lines:
        chunk_text = "\n".join(current_lines).strip()
        if len(chunk_text) > 50:
            chunks.append(Chunk(
                chunk_id=f"{Path(file_path).stem}_{chunk_index}",
                content=chunk_text,
                source_file=file_path,
                section_title=current_section,
                line_start=current_start,
                line_end=len(lines),
                pipeline_ids=_detect_pipeline_ids(chunk_text),
                tags=_detect_tags(chunk_text),
                chunk_type="code" if "```" in chunk_text else "paragraph",
            ))

    return ChunkResult(
        source_file=file_path,
        total_chunks=len(chunks),
        chunks=chunks,
    )


def chunk_all_references(references_dir: str) -> list[ChunkResult]:
    """
    Chunk all .md files in the references directory.

    Returns one ChunkResult per file.
    """
    results: list[ChunkResult] = []
    ref_path = Path(references_dir)

    if not ref_path.exists():
        print(f"Warning: references directory not found: {references_dir}")
        return results

    for md_file in sorted(ref_path.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        result = chunk_markdown(str(md_file), content)
        results.append(result)
        print(f"  {md_file.name}: {result.total_chunks} chunks")

    return results


def chunk_pipeline_json(pipelines_dir: str) -> list[Chunk]:
    """
    Chunk pipeline JSON files: each pipeline becomes one chunk with
    structured metadata (tools, versions, parameters).
    """
    import json

    chunks: list[Chunk] = []
    pipe_path = Path(pipelines_dir)

    if not pipe_path.exists():
        return chunks

    for json_file in sorted(pipe_path.glob("*.json")):
        if json_file.stem in ("versions", "index"):
            continue

        data = json.loads(json_file.read_text(encoding="utf-8"))
        pipeline_id = data.get("id", json_file.stem)

        # Build a structured text representation of the pipeline
        parts = [f"# Pipeline: {data.get('name', '')} ({data.get('nameZH', '')})"]
        parts.append(f"Category: {data.get('category', '')}")
        parts.append(f"Tags: {', '.join(data.get('tags', []))}")
        parts.append(f"Overview: {data.get('overview', '')}")
        parts.append("")

        for source in data.get("sources", []):
            parts.append(f"## Source: {source.get('name', '')} (type: {source.get('type', '')})")
            for step in source.get("steps", []):
                tools_str = ", ".join(
                    f"{t.get('name', '')} {t.get('version', '')}"
                    for t in step.get("tools", [])
                )
                params_str = "; ".join(
                    t.get("params", "")
                    for t in step.get("tools", [])
                    if t.get("params")
                )
                docker_str = "; ".join(
                    t.get("docker", "")
                    for t in step.get("tools", [])
                    if t.get("docker")
                )
                parts.append(f"Step: {step.get('name', '')}")
                parts.append(f"Tools: {tools_str}")
                if params_str:
                    parts.append(f"Params: {params_str}")
                if docker_str:
                    parts.append(f"Docker: {docker_str}")

        chunk_text = "\n".join(parts)

        chunks.append(Chunk(
            chunk_id=f"pipeline_{pipeline_id}",
            content=chunk_text,
            source_file=f"src/data/pipelines/{json_file.name}",
            section_title=data.get("name", pipeline_id),
            line_start=1,
            line_end=len(chunk_text.split("\n")),
            pipeline_ids=[pipeline_id],
            tags=[data.get("category", "")] + data.get("tags", []),
            chunk_type="pipeline",
        ))

    return chunks


# ──────────────────────────────────────────────────────────────
# Standalone test
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    workspace = Path(__file__).parent.parent.parent
    ref_dir = workspace / "references"

    if len(sys.argv) > 1:
        ref_dir = Path(sys.argv[1])

    print(f"Chunking references from: {ref_dir}")
    results = chunk_all_references(str(ref_dir))

    # Also chunk pipeline JSONs
    pipelines_dir = workspace / "src" / "data" / "pipelines"
    pipe_chunks = chunk_pipeline_json(str(pipelines_dir))
    print(f"\nPipeline chunks: {len(pipe_chunks)}")

    total = sum(r.total_chunks for r in results) + len(pipe_chunks)
    print(f"\nTotal chunks: {total}")

    # Show a sample
    if results:
        for r in results:
            if r.chunks:
                chunk = r.chunks[0]
                print(f"\n--- Sample from {r.source_file} ---")
                print(f"  ID: {chunk.chunk_id}")
                print(f"  Section: {chunk.section_title}")
                print(f"  Lines: {chunk.line_start}-{chunk.line_end}")
                print(f"  Pipelines: {chunk.pipeline_ids}")
                print(f"  Tags: {chunk.tags}")
                print(f"  Content preview: {chunk.content[:200]}...")
                break
