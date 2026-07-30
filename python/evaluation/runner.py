"""
Evaluation Runner — 一键运行全部 6 个确定性指标 + Baseline 对比
用法:
    python runner.py                            # 读取 results/outputs.json
    python runner.py outputs.json               # 指定输出文件
    python runner.py --output report.json       # 指定报告输出路径
    python runner.py --baseline baseline.json   # 对比 Prompt Only vs Skill 效果
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
METRICS_DIR = ROOT / "metrics"
RESULTS_DIR = ROOT / "results"

sys.path.insert(0, str(ROOT.parent))  # python/

from evaluation.metrics import workflow_accuracy, knowledge_grounding, parameter_correctness
from evaluation.metrics import reference_coverage, schema_validity


def load_outputs(path: Path) -> dict[str, str]:
    """
    加载 Skill 输出文件。
    格式: {"case_id": "output text", ...}
    或:   [{"id": "...", "output": "..."}, ...]
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        return {item["id"]: item.get("output", "") for item in raw}
    raise ValueError("outputs must be dict or list")


def run(outputs_path: Path | None = None, report_path: Path | None = None):
    if outputs_path is None:
        outputs_path = RESULTS_DIR / "outputs.json"

    if not outputs_path.exists():
        # 没有真实输出时，使用 dummies 跑通框架
        print(f"[WARN] {outputs_path} not found, running with dummy outputs")
        outputs = _dummy_outputs()
    else:
        outputs = load_outputs(outputs_path)

    # 运行 5 个核心指标（workflow_completeness 不计入）
    results: list[dict] = []
    results.append(workflow_accuracy.compute(_to_predictions(outputs)))
    results.append(knowledge_grounding.compute(outputs))
    results.append(parameter_correctness.compute(outputs))
    results.append(reference_coverage.compute(outputs))
    results.append(schema_validity.compute(outputs))

    # 汇总
    scores = [r["score"] for r in results]
    overall = round(sum(scores) / len(scores), 4) if scores else 0.0

    report = {
        "overall_score": overall,
        "scores": {r["metric"]: r["score"] for r in results},
        "details": results,
    }

    # 写报告
    if report_path is None:
        report_path = RESULTS_DIR / "report.json"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # 打印摘要
    print(f"\n{'='*50}")
    print("  Evaluation Complete")
    print(f"{'='*50}")
    for r in results:
        bar = "█" * int(r["score"] * 20) + "░" * (20 - int(r["score"] * 20))
        print(f"  {r['metric']:<28} {r['score']:.2%}  {bar}")
    print(f"  {'─'*48}")
    print(f"  {'Overall':<28} {overall:.2%}")
    print(f"{'='*50}")
    print(f"  Report: {report_path}")
    print()

    return report


def _to_predictions(outputs: dict[str, str]) -> dict[str, str | None]:
    """从输出文本中提取 pipeline_id"""
    import re
    preds: dict[str, str | None] = {}

    # 关键词→pipeline_id 映射（按 specificity 降序，长模式优先）
    keyword_map = [
        ("wgs-germline",     ["BQSR.*陷阱", "BQSR.*坑", "BQSR.*最佳实践", "WGS.*可复现", "可复现.*WGS", "set -euo pipefail"]),
        ("family-trio-wgs",  ["Trio WGS", "trio.*de novo", "de novo.*trio", "PossibleDeNovo", "slivar", "家系.*WGS"]),
        ("wgs-somatic",      ["Mutect2.*肿瘤", "肿瘤.*Mutect2", "体细胞突变", "somatic", "FilterMutectCalls"]),
        ("mendelian-randomization", ["孟德尔随机化", "TwoSampleMR", "MR-PRESSO", "IVW.*MR-Egger"]),
        ("rare-variant",     ["罕见变异", "SKAT-O", "SKAT.*聚合", "Burden test"]),
        ("prs",              ["多基因风险", "PRSice", "LDpred2", "PRS-CS", "C\\+T.*PRS"]),
        ("wes",              ["WES", "外显子", "exome", "CollectHsMetrics", "ACMG"]),
        ("scrna-seq",        ["scRNA-seq", "scRNA", "single.?cell", "Cell Ranger", "细胞注释"]),
        ("chip-seq",         ["ChIP-seq.*ATAC", "ATAC.*ChIP-seq", "ChIP-seq", "FRiP", "IDR", "HOMER.*findMotifs"]),
        ("wgbs",             ["WGBS", "Bismark", "亚硫酸氢盐", "bismark_methylation"]),
        ("16s",              ["16S rRNA", "QIIME", "DADA2", "扩增子", "ASV"]),
        ("metagenomics",     ["宏基因组", "MetaPhlAn", "HUMAnN", "shotgun.*宏"]),
        ("gwas",             ["GWAS", "PLINK.*关联", "SAIGE", "REGENIE", "病例对照", "人群分层", "Manhattan plot"]),
        ("rna-seq",          ["RNA-seq.*差异", "DESeq2 vs edgeR", "DESeq2.*edgeR", "差异表达.*DESeq2"]),
    ]

    for cid, text in outputs.items():
        # 1. JSON 中的 "id": "xxx" 或 "pipeline_id": "xxx"（排除 step/通用词）
        m = re.search(r'"(?:pipeline_)?id"\s*:\s*"([a-zA-Z0-9_-]+)"', text)
        if m and m.group(1) not in ("step-1", "step", "gatk", "source", "step-2", "step-3", "step-4", "step-5", "step-6", "step-7", "fastqc", "trim", "align", "markdup", "bqsr", "haplotypecaller", "genomicsdb", "genotype", "vqsr", "denovo", "annotate", "slivar"):
            preds[cid] = m.group(1)
            continue
        # 2. 文本标注: Pipeline: xxx 或 Pipeline ID: xxx
        m = re.search(r'Pipeline(?: ID)?[:：]\s*`?([a-zA-Z0-9_-]+)`?', text)
        if m:
            preds[cid] = m.group(1)
            continue
        # 3. Markdown 标题: ## family-trio-wgs
        m = re.search(r'^#{1,3}\s+([a-z][a-z0-9_-]{3,30})\s*$', text, re.MULTILINE)
        if m:
            preds[cid] = m.group(1)
            continue
        # 3.5 首段异常声明检测：回答开头明确说"not covered" → 直接标记 None
        if cid not in preds:
            first_paragraph = text.split("\n\n")[0] if "\n\n" in text else text[:200]
            if re.search(r'(?:not (?:currently )?cover|不在.*范围|暂不.*支持|不在当前知识库)', first_paragraph, re.IGNORECASE):
                preds[cid] = None
                continue
        # 4. 关键词回退匹配（按 specificity 从高到低）
        if cid not in preds:
            for pid, keywords in keyword_map:
                for kw in keywords:
                    if re.search(kw, text, re.IGNORECASE):
                        preds[cid] = pid
                        break
                if cid in preds:
                    break
        # 5. 兜底：关键词无匹配 + 文本声明"not covered" → None（与 expected=None 对齐）
        if cid not in preds:
            if re.search(r'(?:not (?:currently )?cover|不在.*范围|暂不.*支持|不在当前知识库)', text, re.IGNORECASE):
                preds[cid] = None
    # 后处理：ID 别名归一化
    alias_map = {"trio-wgs-denovo": "family-trio-wgs"}
    for cid in preds:
        if preds[cid] in alias_map:
            preds[cid] = alias_map[preds[cid]]
    return preds


def compare(skill_path: Path, baseline_path: Path, report_path: Path | None = None):
    """对比 Prompt Only (Baseline) vs Prompt + Skill 的效果"""
    for label, path in [("Skill", skill_path), ("Baseline", baseline_path)]:
        if not path.exists():
            print(f"[ERROR] {label} file not found: {path}")
            sys.exit(1)

    skill_outputs = load_outputs(skill_path)
    baseline_outputs = load_outputs(baseline_path)

    # 共同指标：pipeline_selection_accuracy, parameter_correctness, reference_coverage
    def _eval_compare(outputs: dict[str, str]) -> dict[str, float]:
        preds = _to_predictions(outputs)
        return {
            "pipeline_selection_accuracy": workflow_accuracy.compute(preds)["score"],
            "parameter_correctness": parameter_correctness.compute(outputs)["score"],
            "reference_coverage": reference_coverage.compute(outputs)["score"],
        }

    skill_scores = _eval_compare(skill_outputs)
    baseline_scores = _eval_compare(baseline_outputs)

    # 构建对比报告
    rows = []
    for metric in skill_scores:
        s = skill_scores[metric]
        b = baseline_scores[metric]
        delta = round(s - b, 4)
        if b > 0:
            delta_pct = f"{round((s - b) / b * 100, 1):+.1f}%"
        else:
            delta_pct = "N/A" if s == 0 else "+∞"
        rows.append({
            "metric": metric,
            "prompt_only": b,
            "prompt_plus_skill": s,
            "delta": delta,
            "delta_pct": delta_pct,
        })

    comparison = {
        "description": "Prompt Only vs Prompt + Skill 对比",
        "baseline_file": str(baseline_path),
        "skill_file": str(skill_path),
        "comparison": rows,
    }

    if report_path is None:
        report_path = RESULTS_DIR / "comparison_report.json"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8")

    # 打印对比表
    print(f"\n{'='*70}")
    print("  Baseline 对比: Prompt Only vs Prompt + Skill")
    print(f"{'='*70}")
    print(f"  {'Metric':<30} {'Prompt Only':>12} {'+ Skill':>12} {'Delta':>12}")
    print(f"  {'─'*66}")
    for r in rows:
        b = r["prompt_only"]
        s = r["prompt_plus_skill"]
        d = r["delta_pct"]
        print(f"  {r['metric']:<30} {b:>11.2%} {s:>11.2%} {d:>12}")
    print(f"{'='*70}")
    print(f"  Report: {report_path}")
    print()

    return comparison


def _dummy_outputs() -> dict[str, str]:
    """生成占位输出，用于框架验证"""
    cases = json.loads(
        (ROOT / "benchmarks" / "test_cases.json").read_text(encoding="utf-8")
    )
    return {
        c["id"]: f"Dummy output for: {c['query']}\n"
        f"Pipeline: {c['expected_pipeline_id'] or 'unknown'}\n"
        f"Tools: {', '.join(c.get('must_include_tools', []))}\n"
        f"Params: {', '.join(c.get('must_include_params', []))}"
        for c in cases
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bioinformatics Evaluation Runner")
    parser.add_argument("outputs", nargs="?", help="Path to outputs.json")
    parser.add_argument("--output", "-o", default=None, help="Report output path")
    parser.add_argument("--baseline", "-b", default=None, help="Baseline outputs.json for comparison")
    args = parser.parse_args()

    if args.baseline:
        skill = Path(args.outputs) if args.outputs else RESULTS_DIR / "outputs.json"
        compare(skill, Path(args.baseline), Path(args.output) if args.output else None)
    else:
        outputs = Path(args.outputs) if args.outputs else None
        report = Path(args.output) if args.output else None
        run(outputs, report)
