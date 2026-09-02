"""
Workflow Completeness — 流程完整性
检查 Skill 输出的步骤序列是否覆盖该管线应有的标准步骤。
纯确定性指标，零外部依赖。
"""

import json
import os
import re

# 嵌套列表/粗体提取时的字段噪声词（非步骤名，需过滤）
_FIELD_NOISE = {
    "工具", "关键参数", "参数", "说明", "描述", "输入", "输出", "结果",
    "症状", "原因", "解决", "问题", "解决方案", "注意事项", "陷阱",
    "参考来源", "来源", "类型", "链接", "指标", "阈值", "版本",
    "推荐工具版本", "qc 指标", "灵敏度分析方法", "peak 质量评估指标",
}

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

    # Study designs
    "mendelian_randomization": [
        "Instrument Selection",
        "Harmonization",
        "MR Estimation",
        "Sensitivity Analysis",
        "Multivariable MR",
    ],
    "rare_variant": [
        "Variant QC",
        "Functional Annotation",
        "Null Model Fitting",
        "Aggregation Test",
        "Multiple Testing Correction",
        "ACAT",
    ],
    "prs": [
        "Data Preparation",
        "Quality Control",
        "PRS Calculation",
        "Model Evaluation",
    ],
    "metagenomics": [
        "Quality Control & Host Removal",
        "Taxonomic Annotation",
        "Functional Annotation",
        "Assembly & Binning",
        "Statistical Analysis & Visualization",
    ],
    "amplicon_16s": [
        "Data Import",
        "Denoising & ASV Inference",
        "Taxonomic Classification",
        "Phylogenetic Tree Construction",
        "Diversity Analysis",
        "Differential Abundance Analysis",
    ],
}


# Pipeline ID aliases (normalized → standard key)
PIPELINE_ALIASES = {
    "family-trio-wgs": "trio_wgs",
    "trio-wgs-denovo": "trio_wgs",
    "wgs-germline": "small_variant_wgs",
    "wgs-somatic": "somatic_wgs",
    "wes": "small_variant_wes",
    "scrna-seq": "scrna_seq",
    "single-cell-rna": "scrna_seq",
    "scatac-seq": "single_cell_atac",
    "sc-atac": "single_cell_atac",
    "circrna": "circrna_seq",
    "wgb": "wgb",
    "wgbs": "wgb",
    "epic-array": "methylation_epic_array",
    "mendelian-randomization": "mendelian_randomization",
    "rare-variant": "rare_variant",
    "prs": "prs",
    "metagenomics": "metagenomics",
    "16s": "amplicon_16s",
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
    # amplicon_16s
    "数据导入": "Data Import",
    "去噪": "Denoising & ASV Inference",
    "去噪与 asv 推断": "Denoising & ASV Inference",
    "asv 推断": "Denoising & ASV Inference",
    "asv 检测": "Denoising & ASV Inference",
    "物种注释": "Taxonomic Classification",
    "分类学注释": "Taxonomic Classification",
    "系统发育树": "Phylogenetic Tree Construction",
    "系统发育树构建": "Phylogenetic Tree Construction",
    "多样性分析": "Diversity Analysis",
    "差异丰度分析": "Differential Abundance Analysis",
    # metagenomics
    "功能注释": "Functional Annotation",
    "组装": "Assembly & Binning",
    "分箱": "Assembly & Binning",
    "组装与分箱": "Assembly & Binning",
    "统计分析": "Statistical Analysis & Visualization",
    # rare_variant
    "变异 qc": "Variant QC",
    "零模型拟合": "Null Model Fitting",
    "聚合检验": "Aggregation Test",
    "多重检验校正": "Multiple Testing Correction",
    # mendelian_randomization
    "工具变量选择": "Instrument Selection",
    "数据协调": "Harmonization",
    "mr 估计": "MR Estimation",
    "灵敏度分析": "Sensitivity Analysis",
    "多变量 mr": "Multivariable MR",
    # prs
    "数据准备": "Data Preparation",
    "prs 计算": "PRS Calculation",
    "模型评估": "Model Evaluation",
    # 全大写缩写（避免被 skip_patterns 误伤，同时可作步骤名）
    "acat": "ACAT",
    # 补充：WGBS / 16S / JSON 输出常见表述
    "亚硫酸氢盐比对": "Read Alignment",
    "甲基化提取": "Methylation Calling",
    "差异甲基化分析": "Differential Methylation Analysis",
    "sequence alignment": "Read Alignment",
    # fix3：真实输出常用步骤名补词（此前导致误判为缺口）
    "结果解读": "Visualization",          # GWAS 第4步（Manhattan/QQ plot）
    "数据预处理": "Quality Control",      # scRNA-seq 第1步（含低质量细胞过滤）
    "motif 富集": "Motif Discovery",      # ChIP-seq 第6步（HOMER/MEME-ChIP）
    "分类学注释": "Taxonomic Annotation", # metagenomics 第2步（MetaPhlAn）
    "统计分析与可视化": "Statistical Analysis & Visualization",  # metagenomics 第5步
    # fix3b：真实输出步骤名补词（内容已覆盖，仅命名差异）
    "选择工具变量": "Instrument Selection",   # MR 第1步
    "敏感性分析": "Sensitivity Analysis",     # MR 第4步
    "haplotypecaller": "Variant Calling",     # WES 第4步（工具名作步骤名）
    "准备数据": "Data Preparation",           # PRS 第1步
    "拟合空模型": "Null Model Fitting",       # rare-variant 第3步
    # fix4：Markdown 标题格式输出补词（## 1. 步骤名 / ### 1. **步骤名**）
    "曼哈顿图": "Visualization",              # GWAS 可视化（Manhattan plot）
    "qq 图": "Visualization",                 # GWAS 可视化（Q-Q plot）
    "主成分分析": "Dimensionality Reduction", # GWAS 人群分层 PCA
    "协变量": "Association Testing",          # GWAS 加入协变量做关联分析
    "skat-o": "Aggregation Test",             # rare-variant SKAT-O 聚合检验
    "burden": "Aggregation Test",             # rare-variant Burden 检验
    "负担检验": "Aggregation Test",           # rare-variant 负担检验
    "结果解释与可视化": "Visualization",      # rare-variant 结果解释
    "质量控制与验证": "Quality Control",      # PRS 质量控制与验证
    # fix5：16S / rare-variant 组合步骤名补词
    "分类注释": "Taxonomic Classification",   # 16S 第4步（SILVA 分类注释）
    "otu 聚类": "Denoising & ASV Inference",  # 16S OTU 聚类 ≈ ASV 推断
    "otu聚类": "Denoising & ASV Inference",
    "聚类序列": "Denoising & ASV Inference",  # 16S 聚类序列
    "基因/区域注释": "Functional Annotation", # rare-variant 构建基因/区域注释
    "基因注释": "Functional Annotation",
    # fix6：步骤名变体补词（内容已覆盖，仅命名差异）
    "功能注释与下游分析": "Peak Annotation",   # ChIP-seq 第10步（含 motif 分析）
    "甲基化位点识别": "Methylation Calling",   # WGBS 第3步
    "表达量估计": "Expression Quantification", # RNA-seq 第3步
    "mr 分析": "MR Estimation",                # MR 第3步（IVW/MR-Egger）
    "分类分析": "Taxonomic Annotation",        # metagenomics 第3步（Kraken2）
    "细胞注释": "Cell Type Annotation",        # scRNA-seq 第5步（Seurat/SingleR）
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

    # Pattern 0: JSON 格式输出（如 Nextflow pipeline JSON，含 "steps" 数组）
    # 支持：{"steps": [...]}、纯数组 [...]、Markdown 代码块中的 JSON（```json ... ```）
    # 解析每个 step 的 name / id / description / title / step_name 字段作为步骤名
    stripped = text.strip()
    json_candidates = []
    if stripped.startswith("{") or stripped.startswith("["):
        json_candidates.append(stripped)
    for m in re.finditer(r'```(?:json)?\s*(.*?)```', text, re.DOTALL):
        json_candidates.append(m.group(1).strip())
    for cand in json_candidates:
        try:
            data = json.loads(cand)
        except (json.JSONDecodeError, AttributeError):
            continue
        if isinstance(data, dict):
            json_steps = data.get("steps", data.get("pipeline", []))
            if isinstance(json_steps, dict):
                json_steps = json_steps.get("steps", [])
        elif isinstance(data, list):
            json_steps = data
        else:
            json_steps = []
        for st in json_steps:
            if isinstance(st, dict):
                for key in ("name", "id", "description", "title", "step_name", "step"):
                    val = st.get(key)
                    if val and isinstance(val, str):
                        val = val.strip()
                        if val and len(val) <= 60:
                            steps.append(val)
                        break
        if steps:
            return steps

    # Pattern 1: **粗体步骤名** 后跟 ：或 : （中文编号列表）
    bold_steps = re.findall(r'\*\*([^*\n]{1,40})\*\*', text)
    for s in bold_steps:
        s = s.strip()
        # 去掉编号前缀，如 "1. xxx" / "1、xxx" / "1) xxx"
        s = re.sub(r'^\d+[\.\)、]\s*', '', s)
        if s and len(s) <= 40:
            # 排除非步骤名（软件名、工具名、文件名等）
            # 注意：全大写缩写（ACAT/QC/PCA/SV/MR 等）可能是步骤名，不跳过；
            # 仅跳过含小写字母的纯英文词（工具名如 bwa-mem2、gatk 通常小写）
            skip_patterns = [
                r'\.v\d',             # 版本号
                r'\.py$',             # Python 文件
                r'^hg\d',             # 参考基因组
                r'^chr',              # 染色体
                r'^\./',              # 文件路径
            ]
            if any(re.search(pat, s, re.IGNORECASE) for pat in skip_patterns):
                continue
            if re.fullmatch(r'[a-z0-9\._-]+', s) and any(c.islower() for c in s):
                continue  # 含小写字母的纯英文词 → 工具名，跳过
            steps.append(s)

    # Pattern 2: 编号后紧跟的文本（与 Pattern 1 合并，不设门控——
    # 避免 Pattern 1 提取到"关键参数/说明"等噪声粗体后跳过标题步骤）
    # 优先匹配 Markdown 标题 + 编号：## 1. 步骤名 / ### 1. **步骤名**
    numbered = re.findall(
        r'(?:^|\n)\s*#{1,6}\s*\d+[\.\)、]\s*(?:\*\*)?([^*\n]{0,50})', text)
    if not numbered:
        numbered = re.findall(r'(?:^|\n)\s*\d+[\.\)、]\s*(\S[^\n]{0,50})', text)
    for s in numbered:
        s = s.strip().rstrip('：:。.,;；')
        s = re.sub(r'^\d+[\.\)、]\s*', '', s)
        s = s.replace('**', '')
        if s and len(s) <= 60:
            steps.append(s)

    # Pattern 3: Markdown 嵌套列表步骤名（- 步骤名 / - **步骤名** /   - 步骤名：描述）
    # 3a: - **步骤名**（粗体列表项）
    nested_bold = re.findall(r'(?:^|\n)\s*[-*]\s+\*\*([^*\n]{1,40})\*\*', text)
    # 3b: - 步骤名：描述（无粗体，冒号前文本）
    nested_plain = re.findall(r'(?:^|\n)\s*[-*]\s+([^*\n：:]{1,40}?)\s*[：:]', text)
    for s in nested_bold + nested_plain:
        s = s.strip()
        s = re.sub(r'^\d+[\.\)、]\s*', '', s)
        if s and len(s) <= 40:
            if s in _FIELD_NOISE:
                continue
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
    模糊匹配步骤名。支持中文关键词映射与子词拆分。
    子词拆分：将提取步骤按 +、/、空格等分隔符拆开，
    任一子词命中 CN_STEP_MAP 即视为匹配（解决"单样本GVCF"等组合名查不到的问题）。
    """
    e = extracted.lower().strip()
    s = standard.lower().strip()

    # 直接子串匹配
    if s in e or e in s:
        return True

    # 标准步骤含 QC 缩写（如 Variant QC）时，提取步骤含 qc/质控/质量控制 即匹配
    if re.search(r'\bqc\b', s):
        if re.search(r'\bqc\b|质控|质量控制', e):
            return True

    # 候选词：整体 + 按分隔符拆分的子词
    candidates = [e] + [w for w in re.split(r'[\s+/、,，;；&]+', e) if w]

    for cand in candidates:
        mapped = CN_STEP_MAP.get(cand)
        if not mapped:
            continue
        m = mapped.lower()
        if m == s or m in s or s in m:
            return True
        # 词级重叠：映射结果与标准步骤共享 ≥2 个单词
        # （如 Differential Expression Analysis vs Differential Abundance Analysis，
        #   Quality Control vs Quality Control & Host Removal）
        m_words = set(m.split())
        s_words = set(s.split())
        if len(m_words & s_words) >= 2:
            return True

    # fix3：中文子串包含匹配——提取步骤整体包含 CN_STEP_MAP 的键时，
    # 用该键的映射参与匹配（解决"过滤体细胞变异"含"过滤"、"质控 + 修剪"含"质控"等组合名）
    # 按键长度降序遍历，优先匹配最长键（如"分类注释"优先于"注释"）
    for key, mapped in sorted(CN_STEP_MAP.items(), key=lambda kv: len(kv[0]), reverse=True):
        if key and key in e:
            m = mapped.lower()
            if m == s or m in s or s in m:
                return True
            m_words = set(m.split())
            s_words = set(s.split())
            if len(m_words & s_words) >= 2:
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


def _load_merged_cases(outputs_path: str) -> list[dict]:
    """Merge outputs.json ({case_id: text}) with expected_pipeline_id from test_cases.json."""
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    cases_path = root / "benchmarks" / "test_cases.json"
    test_cases = json.loads(cases_path.read_text(encoding="utf-8"))

    raw = json.loads(Path(outputs_path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    # dict format: {case_id: output text}
    expected_by_id = {c["id"]: c.get("expected_pipeline_id") for c in test_cases}
    return [
        {
            "case_id": cid,
            "expected_pipeline_id": expected_by_id.get(cid),
            "answer": text,
        }
        for cid, text in raw.items()
    ]


if __name__ == "__main__":
    import argparse
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Workflow Completeness metric")
    default_outputs = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "outputs.json")
    parser.add_argument("outputs", nargs="?", default=default_outputs, help="Path to outputs.json")
    parser.add_argument("--output", "-o", default=None, help="Report output path")
    args = parser.parse_args()

    if not os.path.exists(args.outputs):
        print(f"[ERROR] outputs file not found: {args.outputs}")
        sys.exit(1)

    report = evaluate(_load_merged_cases(args.outputs))

    out_path = args.output or os.path.join(os.path.dirname(args.outputs), "workflow_completeness_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"workflow_completeness: {report['score']:.2%} "
          f"({report['total_covered_steps']}/{report['total_standard_steps']} steps, "
          f"{report['cases_evaluated']} cases)")
    print(f"Report: {out_path}")
