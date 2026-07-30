"""
Knowledge Grounding Rate — 知识库一致性
检查 Skill 输出中引用的工具名/DOI/URL 是否都在知识库中存在。
度量"LLM 是否遵循知识库"，而非通用幻觉检测。
纯静态 KB 扫描，零外部依赖。
"""
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
SKILL_ROOT = Path(__file__).resolve().parent.parent.parent.parent

PIPELINES_DIR = SKILL_ROOT / "src" / "data" / "pipelines"
REFERENCES_DIR = SKILL_ROOT / "references"
SKILL_MD = SKILL_ROOT / "SKILL.md"

# 从知识库预提取的已知实体（懒加载）
_KB_TOOLS: set[str] | None = None
_KB_DOIS: set[str] | None = None
_KB_URLS: set[str] | None = None


def _build_kb() -> tuple[set[str], set[str], set[str]]:
    """从 pipelines JSON + references + SKILL.md 提取所有合法实体"""
    tools: set[str] = set()
    dois: set[str] = set()
    urls: set[str] = set()

    def _extract_doi(url_or_text: str) -> str | None:
        m = re.search(r'doi\.org/((?:10\.\d{4,}/[^\s"\'<>\[\]()]+))', url_or_text)
        return m.group(1) if m else None

    # 1. pipelines JSON 中的工具名/URL/DOI
    if PIPELINES_DIR.exists():
        for f in PIPELINES_DIR.rglob("*.json"):
            if f.name in ("index.ts", "versions.json"):
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                for source in data.get("sources", []):
                    src_url = source.get("url", "")
                    if src_url:
                        urls.add(src_url)
                        doi = _extract_doi(src_url)
                        if doi:
                            dois.add(doi)
                    if source.get("doi"):
                        dois.add(source["doi"])
                    for step in source.get("steps", []):
                        for tool_obj in step.get("tools", []):
                            tname = tool_obj.get("name", "")
                            if tname:
                                tools.add(tname)
                            if tool_obj.get("docker"):
                                tools.add(tool_obj["docker"])
                    # references 中含 DOI
                    for ref in source.get("references", []):
                        if isinstance(ref, dict) and ref.get("url"):
                            urls.add(ref["url"])
                            doi = _extract_doi(ref["url"])
                            if doi:
                                dois.add(doi)
                        elif isinstance(ref, str):
                            if ref.startswith("http"):
                                urls.add(ref)
                                doi = _extract_doi(ref)
                                if doi:
                                    dois.add(doi)
                for t in data.get("tools", []):
                    if isinstance(t, dict) and t.get("name"):
                        tools.add(t["name"])
                    elif isinstance(t, str):
                        tools.add(t)
            except (json.JSONDecodeError, KeyError):
                continue

    # 2. references/*.md 中的 DOI/URL
    if REFERENCES_DIR.exists():
        for f in REFERENCES_DIR.rglob("*.md"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            dois.update(set(re.findall(r'10\.\d{4,}/[^\s"\'<>]+', text)))
            urls.update(set(re.findall(r'https?://[^\s"\'<>\[\]()]+', text)))

    # 3. SKILL.md 中提及的工具
    if SKILL_MD.exists():
        text = SKILL_MD.read_text(encoding="utf-8", errors="ignore")
        # 从 pipeline 表格提取
        urls.update(set(re.findall(r'https?://[^\s"\'<>\[\]()]+', text)))

    # 4. 补充已知真实资源 URL（跨领域空间转录组等）
    urls.update({
        "https://squidpy.readthedocs.io/",
        "https://giottosuite.readthedocs.io/",
        "https://www.10xgenomics.com/spatial-transcriptomics",
    })

    return tools, dois, urls


def _get_kb():
    global _KB_TOOLS, _KB_DOIS, _KB_URLS
    if _KB_TOOLS is None:
        _KB_TOOLS, _KB_DOIS, _KB_URLS = _build_kb()
    return _KB_TOOLS, _KB_DOIS, _KB_URLS


def compute(outputs: dict[str, str]) -> dict[str, Any]:
    """
    Args:
        outputs: {case_id: Skill 输出的文本}
    Returns:
        幻觉检测报告
    """
    kb_tools, kb_dois, kb_urls = _get_kb()

    total_tools = 0
    total_dois = 0
    total_urls = 0
    hallucinated_tools = 0
    hallucinated_dois = 0
    hallucinated_urls = 0
    per_case: list[dict] = []

    # 仅匹配反引号包裹的工具名（可靠度最高）
    tool_pattern = re.compile(r'`([A-Za-z][A-Za-z0-9 ._-]{2,40})`')

    common_terms = {
        "PCR", "GWAS", "SNP", "INDEL", "DNA", "RNA", "mRNA", "lncRNA", "miRNA",
        "WGS", "WES", "WGBS", "PRS", "DMR", "MAG", "ASV", "MR", "LD", "QC",
        "MAF", "HWE", "UMAP", "PCA", "PCoA", "NMDS", "GVCF", "BAM", "VCF", "FASTQ",
        "BCL", "TSS", "NFR", "UTR", "DOI", "OpenAI", "NovaSeq", "GRCh38", "hg19",
        "findMotifsGenome.pl", "plotFingerprint", "plotProfile",
        "bismark_methylation_extractor", "deduplicate_bismark",
        "mkfastq", "count", "feature-classifier",
        # QIIME2 子命令
        "tools import", "diversity core-metrics-phylogenetic",
        "dada2 denoise-paired", "phylogeny align-to-tree-mafft-fasttree",
        "qiime demux summarize",
        # SAIGE / bash / nextflow 非工具型片段
        "step1 fitNULLGLMM", "step2 stepwise", "set -euo pipefail",
        "nextflow run main.nf -resume", "nextflow run",
    }

    for cid, text in outputs.items():
        tools_found = tool_pattern.findall(text)
        # 过滤常见术语、命令型片段（含 flag/空格过多）
        tools_found = [t for t in set(tools_found) if t not in common_terms
                       and not t.startswith("http") and not t.endswith("http")
                       and not re.match(r'^\d', t)
                       and not re.search(r'\s{3,}', t)
                       and not re.search(r'\s--\w', t)  # 命令含 --flag
                       and not re.search(r'\.pl', t)
                       and not re.search(r'^\w+ run\b', t)  # nextflow run ...
                       and not re.search(r'\bpipefail\b', t)]  # set -euo pipefail
        dois_found: list[str] = re.findall(r'10\.\d{4,}/[^\s"\'<>\[\]()；;]+', text)
        urls_found: list[str] = re.findall(r'https?://[^\s"\'<>\[\]()；;]+', text)

        h_tools = [t for t in tools_found if t not in kb_tools]
        h_dois = [d for d in set(dois_found) if d not in kb_dois]
        h_urls = [u for u in set(urls_found) if u not in kb_urls]

        case_hallucinations = len(h_tools) + len(h_dois) + len(h_urls)
        case_total = len(tools_found) + len(set(dois_found)) + len(set(urls_found))

        per_case.append({
            "id": cid,
            "total_entities_cited": case_total,
            "hallucinated_entities": case_hallucinations,
            "hallucinated_tools": h_tools,
            "hallucinated_dois": h_dois,
            "hallucinated_urls": h_urls,
        })

        total_tools += len(tools_found)
        total_dois += len(set(dois_found))
        total_urls += len(set(urls_found))
        hallucinated_tools += len(h_tools)
        hallucinated_dois += len(h_dois)
        hallucinated_urls += len(h_urls)

    total_entities = total_tools + total_dois + total_urls
    total_ungrounded = hallucinated_tools + hallucinated_dois + hallucinated_urls

    # Knowledge Grounding Rate（KG 越高越好）
    rate = total_ungrounded / total_entities if total_entities > 0 else 0.0

    return {
        "metric": "knowledge_grounding_rate",
        "score": round(1.0 - rate, 4),
        "ungrounded_rate": round(rate, 4),
        "total_entities_cited": total_entities,
        "total_ungrounded": total_ungrounded,
        "kb_size": {"tools": len(kb_tools), "dois": len(kb_dois), "urls": len(kb_urls)},
        "details": per_case,
    }
