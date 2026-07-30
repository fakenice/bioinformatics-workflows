"""
Workflow Completeness — 流程完整性
检查 Skill 输出的步骤序列是否覆盖该管线应有的标准步骤。
纯确定性指标，零外部依赖。
"""

import json
import os
import re

# ============================================================
# 各管线的标准步骤定义（按 pipeline_id 映射）
# ============================================================
PIPELINE_STANDARD_STEPS = {
    # WGS 家族
    "trio_wgs": [
        "Quality Control",
        "Read Alignment",
        "Variant Calling",
        "Variant Annotation",
        "Variant Filtering",
    ],
    "small_variant_wgs": [
        "Quality Control",
        "Read Alignment",
        "Variant Calling",
    ],
    "structural_variant_wgs": [
        "Quality Control",
        "Read Alignment",
        "SV Calling",
        "SV Annotation",
    ],
    "somatic_wgs": [
        "Quality Control",
        "Read Alignment",
        "Somatic Variant Calling",
        "Variant Annotation",
        "Variant Filtering",
    ],

    # WES
    "small_variant_wes": [
        "Quality Control",
        "Read Alignment",
        "Variant Calling",
        "Variant Annotation",
    ],

    # RNA-Seq
    "rna_seq": [
        "Quality Control",
        "Read Alignment",
        "Expression Quantification",
        "Differential Expression Analysis",
    ],
    "circrna_seq": [
        "Quality Control",
        "Read Trimming",
        "CircRNA Detection",
        "CircRNA Annotation",
        "Differential Analysis",
    ],

    # Methylation
    "wgb": [
        "Quality Control",
        "Read Alignment",
        "Methylation Calling",
        "Differential Methylation Analysis",
    ],
    "methylation_epic_array": [
        "Quality Control",
        "Normalization",
        "Probe Filtering",
        "Differential Methylation Analysis",
    ],

    # Single-cell
    "scrna_seq": [
        "Quality Control",
        "Normalization",
        "Dimensionality Reduction",
        "Clustering",
        "Differential Expression Analysis",
    ],
    "single_cell_atac": [
        "Quality Control",
        "Peak Calling",
        "Dimensionality Reduction",
        "Clustering",
        "Motif Enrichment Analysis",
    ],

    # Targeted / Panel
    "targeted_panel": [
        "Quality Control",
        "Read Alignment",
        "Variant Calling",
        "Variant Annotation",
    ],

    # Other
    "gwas": [
        "Quality Control",
        "Association Testing",
        "Visualization",
        "Annotation",
    ],
    "chip_seq": [
        "Quality Control",
        "Read Alignment",
        "Peak Calling",
        "Peak Annotation",
        "Motif Discovery",
    ],
}


# Pipeline ID aliases (normalized → standard key)
PIPELINE_ALIASES = {
    "family-trio-wgs": "trio_wgs",
    "trio-wgs-denovo": "trio_wgs",
    "wgs-germline": "small_variant_wgs",
    "wgs-somatic": "somatic_wgs",
    "scrna-seq": "scrna_seq",
    "single-cell-rna": "scrna_seq",
    "scatac-seq": "single_cell_atac",
    "sc-atac": "single_cell_atac",
    "circrna": "circrna_seq",
    "wgb": "wgb",
    "wgbs": "wgb",
    "epic-array": "methylation_epic_array",
    "mendelian-randomization": None,  # meta-analysis, no pipeline steps
    "rare-variant": None,
    "prs": None,
    "metagenomics": None,
    "16s": None,
}


def _normalize_pipeline_id(raw: str) -> str | None:
    """Normalize pipeline_id to standard key."""
    pid = raw.strip().lower().replace("_", "-")
    # Direct match first
    if pid in PIPELINE_STANDARD_STEPS:
        return pid
    # Replace - back to _ for lookup
    pid_u = pid.replace("-", "_")
    if pid_u in PIPELINE_STANDARD_STEPS:
        return pid_u
    # Check aliases
    if pid in PIPELINE_ALIASES:
        return PIPELINE_ALIASES[pid]
    if pid_u in PIPELINE_ALIASES:
        return PIPELINE_ALIASES[pid_u]
    return None


# ============================================================
# Chinese → English step name mapping
# ============================================================
CN_STEP_MAP = {
    "质量控制": "Quality Control",
    "质控": "Quality Control",
    "qc": "Quality Control",
    "比对": "Read Alignment",
    "序列比对": "Read Alignment",
    "read alignment": "Read Alignment",
    "标记重复": "Quality Control",
    "bqsr": "Quality Control",
    "碱基质量重校准": "Quality Control",
    "变异检测": "Variant Calling",
    "单样本 gvcf": "Variant Calling",
    "gvcf 整合": "Variant Calling",
    "gvcf": "Variant Calling",
    "variant calling": "Variant Calling",
    "变异注释": "Variant Annotation",
    "注释": "Variant Annotation",
    "annotation": "Variant Annotation",
    "变异过滤": "Variant Filtering",
    "过滤": "Variant Filtering",
    "filtering": "Variant Filtering",
    "表达定量": "Expression Quantification",
    "表达量化": "Expression Quantification",
    "expression quantification": "Expression Quantification",
    "差异表达分析": "Differential Expression Analysis",
    "差异分析": "Differential Expression Analysis",
    "differential expression": "Differential Expression Analysis",
    "降维": "Dimensionality Reduction",
    "pca": "Dimensionality Reduction",
    "tsne": "Dimensionality Reduction",
    "聚类": "Clustering",
    "clustering": "Clustering",
    "cell annotation": "Clustering",
    "细胞注释": "Clustering",
    "peak calling": "Peak Calling",
    "peak 检测": "Peak Calling",
    "peak annotation": "Peak Annotation",
    "motif 分析": "Motif Discovery",
    "motif discovery": "Motif Discovery",
    "motif enrichment": "Motif Enrichment Analysis",
    "标准化": "Normalization",
    "归一化": "Normalization",
    "normalization": "Normalization",
    "甲基化检测": "Methylation Calling",
    "methylation calling": "Methylation Calling",
    "甲基化差异分析": "Differential Methylation Analysis",
    "关联分析": "Association Testing",
    "association testing": "Association Testing",
    "可视化": "Visualization",
    "visualization": "Visualization",
    "trimming": "Read Trimming",
    "修剪": "Read Trimming",
    "circrna 检测": "CircRNA Detection",
    "circrna detection": "CircRNA Detection",
    "circrna 注释": "CircRNA Annotation",
    "read trimming": "Read Trimming",
    "sv calling": "SV Calling",
    "sv 检测": "SV Calling",
    "sv annotation": "SV Annotation",
    "体细胞变异检测": "Somatic Variant Calling",
    "somatic variant calling": "Somatic Variant Calling",
    "探针过滤": "Probe Filtering",
    "probe filtering": "Probe Filtering",
    "peak 注释": "Peak Annotation",
}


def extract_steps_from_answer(answer_text: str) -> list[str]:
    """
    从 Skill 输出文本中提取步骤名。
    主要匹配格式：`1. **步骤名**：描述` 形式的中文编号步骤。
    """
    if not answer_text:
        return []

    steps = []
    text = answer_text

    # Pattern 1: **粗体步骤名** 后跟 ：或 : （中文编号列表）
    bold_steps = re.findall(r'\*\*([^*\n]{1,40})\*\*', text)
    for s in bold_steps:
        s = s.strip()
        if s and len(s) <= 40:
            # 排除非步骤名（软件名、工具名、文件名等）
            skip_patterns = [
                r'^[a-z0-9\._-]+$',  # 纯英文工具名如 bwa-mem2、gatk
                r'\.v\d',             # 版本号
                r'\.py$',             # Python 文件
                r'^hg\d',             # 参考基因组
                r'^chr',              # 染色体
                r'^\./',              # 文件路径
            ]
            if any(re.search(pat, s, re.IGNORECASE) for pat in skip_patterns):
                continue
            steps.append(s)

    # Pattern 2: 编号后紧跟的文本（无粗体标记时回退）
    if not steps:
        numbered = re.findall(r'(?:^|\n)\s*\d+[\.\)、]\s*(\S[^\n]{0,50})', text)
        for s in numbered:
            s = s.strip().rstrip('：:。.,;；')
            if s and len(s) <= 60:
                steps.append(s)

    # 去重保持顺序
    seen = set()
    unique = []
    for s in steps:
        key = s.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(s)

    return unique


def fuzzy_match(extracted: str, standard: str) -> bool:
    """
    模糊匹配步骤名。支持中文关键词映射。
    """
    e = extracted.lower().strip()
    s = standard.lower().strip()

    # 直接子串匹配
    if s in e or e in s:
        return True

    # 中文→英文映射匹配
    mapped = CN_STEP_MAP.get(e)
    if mapped:
        if mapped.lower() == s:
            return True
        if mapped.lower() in s or s in mapped.lower():
            return True
        # 反向：standard 是否在 mapped 中
        if s in mapped.lower():
            return True

    return False


def evaluate(outputs: list[dict]) -> dict:
    """
    评估 Workflow Completeness。
    对每个 test case，用 expected_pipeline_id 查找标准步骤，
    计算 Skill 输出覆盖了多少标准步骤。
    """
    per_case = []
    total_covered = 0
    total_standard = 0
    case_count = 0

    for case in outputs:
        raw_id = (case.get("expected_pipeline_id") or "").strip().lower()
        pipeline_id = _normalize_pipeline_id(raw_id)
        answer = case.get("answer", "") or case.get("output", "")

        standard_steps = PIPELINE_STANDARD_STEPS.get(pipeline_id, [])

        if not standard_steps:
            per_case.append({
                "case_id": case.get("case_id", "?"),
                "pipeline_id": pipeline_id,
                "score": None,
                "note": "no standard steps defined",
            })
            continue

        extracted = extract_steps_from_answer(answer)
        matched = []
        missing = []

        for std in standard_steps:
            if any(fuzzy_match(ext, std) for ext in extracted):
                matched.append(std)
            else:
                missing.append(std)

        completeness = len(matched) / len(standard_steps) if standard_steps else 1.0
        total_covered += len(matched)
        total_standard += len(standard_steps)
        case_count += 1

        per_case.append({
            "case_id": case.get("case_id", "?"),
            "pipeline_id": pipeline_id,
            "score": round(completeness, 4),
            "standard_steps": standard_steps,
            "matched": matched,
            "missing": missing,
        })

    overall = total_covered / total_standard if total_standard > 0 else 1.0

    return {
        "metric": "workflow_completeness",
        "score": round(overall, 4),
        "total_standard_steps": total_standard,
        "total_covered_steps": total_covered,
        "cases_evaluated": case_count,
        "details": per_case,
    }
