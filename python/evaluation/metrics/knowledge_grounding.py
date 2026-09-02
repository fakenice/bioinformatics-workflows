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
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
SKILL_ROOT = Path(__file__).resolve().parent.parent.parent.parent

PIPELINES_DIR = SKILL_ROOT / "src" / "data" / "pipelines"
REFERENCES_DIR = SKILL_ROOT / "references"
SKILL_MD = SKILL_ROOT / "SKILL.md"

# 权威来源域白名单：公认的文献/工具/文档来源域。
# URL 判定时，host 命中 KB 域名或本白名单即视为 grounded（引用真实权威来源不算幻觉）。
# 注意：host 比较前会去掉 "www." 前缀。
AUTHORITY_HOSTS = {
    "nature.com", "ncbi.nlm.nih.gov", "nextflow.io", "readthedocs.io",
    "qiime2.org", "10xgenomics.com", "arb-silva.de", "docker.com",
    "mrcieu.ac.uk", "saige.org", "popgen.dk", "bowtie2.github.io",
    "humann.readthedocs.io", "kraken2.readthedocs.io", "nf-core.org",
    "mrcieub.github.io", "wwwprsice.org", "mr-tool.org", "mrbase.org",
    "mrpresso.org", "support.10xgenomics.com",
}


def _host_of(url: str) -> str:
    """提取 URL 的 host（小写）"""
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _norm_host(host: str) -> str:
    """去掉 www. 前缀，便于域名级比较"""
    return host[4:] if host.startswith("www.") else host

# 从知识库预提取的已知实体（懒加载）
_KB_TOOLS: set[str] | None = None
_KB_DOIS: set[str] | None = None
_KB_URLS: set[str] | None = None
_KB_HOSTS: set[str] | None = None


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

    return tools, dois, urls


def _get_kb():
    global _KB_TOOLS, _KB_DOIS, _KB_URLS
    if _KB_TOOLS is None:
        _KB_TOOLS, _KB_DOIS, _KB_URLS = _build_kb()
    return _KB_TOOLS, _KB_DOIS, _KB_URLS


def _get_kb_hosts() -> set[str]:
    """KB 中所有 URL 的 host 集合（规范化：小写、去 www.），用于域名级匹配"""
    global _KB_HOSTS
    if _KB_HOSTS is None:
        _, _, kb_urls = _get_kb()
        hosts: set[str] = set()
        for u in kb_urls:
            try:
                hosts.add(_norm_host(urlparse(u).netloc))
            except Exception:
                pass
        _KB_HOSTS = hosts
    return _KB_HOSTS


def _url_grounded(u: str, kb_urls: set[str], extra_urls: set[str] | None = None) -> bool:
    """URL 是否 grounded：精确匹配 KB URL / 检索来源白名单，或 host 在 KB 域名 / 权威来源域中"""
    if u in kb_urls:
        return True
    if extra_urls and u in extra_urls:
        return True
    try:
        h = _norm_host(urlparse(u).netloc)
    except Exception:
        return False
    return h in _get_kb_hosts() or h in AUTHORITY_HOSTS


_KB_CORPUS: str | None = None


def _get_corpus() -> str:
    """KB 全文语料（小写），用于工具名 grounded 判定（覆盖 name/docker 之外的 description/notes/references 字段）"""
    global _KB_CORPUS
    if _KB_CORPUS is None:
        parts: list[str] = []
        if PIPELINES_DIR.exists():
            for f in PIPELINES_DIR.rglob("*.json"):
                if f.name in ("index.ts", "versions.json"):
                    continue
                try:
                    parts.append(f.read_text(encoding="utf-8"))
                except (UnicodeDecodeError, OSError):
                    pass
        if REFERENCES_DIR.exists():
            for f in REFERENCES_DIR.rglob("*.md"):
                parts.append(f.read_text(encoding="utf-8", errors="ignore"))
        if SKILL_MD.exists():
            parts.append(SKILL_MD.read_text(encoding="utf-8", errors="ignore"))
        _KB_CORPUS = " ".join(parts).lower()
    return _KB_CORPUS


def compute(outputs: dict[str, str], extra_urls: set[str] | None = None,
            extra_dois: set[str] | None = None) -> dict[str, Any]:
    """
    Args:
        outputs: {case_id: Skill 输出的文本}
        extra_urls: 额外 grounded URL 白名单（如联网检索注入的真实来源）
        extra_dois: 额外 grounded DOI 白名单（如联网检索注入的真实来源）
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

    # 工具名提取改为 KB 词典词边界匹配（替代反引号正则，反引号会漏掉无反引号工具名）
    def _norm(t: str) -> str:
        t = t.strip()
        t = re.sub(r'\s*\((R|R/Bioconductor|R包|bigsnpr|v[\d.]+)[^)]*\)', '', t)
        return t.strip()

    def _split(t: str) -> list[str]:
        return [p.strip() for p in re.split(r'\s*/\s*|\s*\+\s*', t) if p.strip()]

    # KB 规范化工具词典（小写）
    kb_tools_norm: set[str] = set()
    for _t in kb_tools:
        for _p in _split(_norm(_t)):
            _p = _p.lower()
            if _p and ':' not in _p and len(_p) >= 3:
                kb_tools_norm.add(_p)
                if _p.startswith('gatk '):
                    kb_tools_norm.add(_p[5:].strip())
                if _p.startswith('ensembl '):
                    kb_tools_norm.add(_p[8:].strip())

    # 额外检测词典：KB 外但输出中可能出现的工具名（用于提取以便统计未接地）
    extra_tools = {
        "apeglm", "ashr", "ihw", "tmm", "squidpy", "giotto", "spaceranger",
        "spatialde", "visium", "tn5", "merfish", "slide-seq", "stereo-seq",
        "slingshot", "nichenet", "pyscenic", "mr-base", "bwa-meth", "bs-seeker2",
        "bolt-lmm", "gsea", "qqman", "checkm", "snakemake", "conda-lock",
        "bigwig", "cadd", "loftee", "revel", "acat", "kegg", "reactome",
        "mafft", "fasttree", "silva", "trimmomatic", "collecthsmetrics",
        "dss", "methylkit", "annotatr", "gviz", "edger", "desnq2", "diffbind",
        "chipseeker", "homer", "meme-chip", "deeptools", "macs2", "macs3",
        "fastp", "picard", "bigsnpr", "qctool", "prsice-2", "prs-cs",
        "ldpred2", "ldsc", "gcta", "regenie", "saige", "skat", "skat-o",
        "dragmap", "multiqc", "fastqc", "bowtie2", "samtools",
    }

    detect_list = sorted(kb_tools_norm | extra_tools, key=len, reverse=True)

    def _match(text: str) -> list[str]:
        tl = text.lower()
        found: list[tuple[str, int, int]] = []
        for tok in detect_list:
            if ' ' in tok:
                pat = (r'(?<![a-z0-9])'
                       + r'\s+'.join(re.escape(w) for w in tok.split())
                       + r'(?![a-z0-9])')
            else:
                pat = r'(?<![a-z0-9._-])' + re.escape(tok) + r'(?![a-z0-9._-])'
            for m in re.finditer(pat, tl):
                if any(not (m.end() <= s or m.start() >= e) for (_, s, e) in found):
                    continue
                found.append((tok, m.start(), m.end()))
        found.sort(key=lambda x: x[1])
        return [t for t, _, _ in found]

    kb_corpus = _get_corpus()

    def _in_corpus(tok: str) -> bool:
        if ' ' in tok:
            pat = (r'(?<![a-z0-9])' + r'\s+'.join(re.escape(w) for w in tok.split())
                   + r'(?![a-z0-9])')
        else:
            pat = r'(?<![a-z0-9._-])' + re.escape(tok) + r'(?![a-z0-9._-])'
        return re.search(pat, kb_corpus) is not None

    for cid, text in outputs.items():
        tools_found = _match(text)
        dois_found: list[str] = re.findall(r'10\.\d{4,}/[^\s"\'<>\[\]()；;]+', text)
        urls_found: list[str] = re.findall(r'https?://[^\s"\'<>\[\]()；;]+', text)

        h_tools = [t for t in tools_found if not _in_corpus(t)]
        h_dois = [d for d in set(dois_found) if d not in kb_dois and not (extra_dois and d in extra_dois)]
        h_urls = [u for u in set(urls_found) if not _url_grounded(u, kb_urls, extra_urls)]

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
