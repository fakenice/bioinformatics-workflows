"""
Evaluation Report Generator
Aggregates results from all five metrics into a structured Markdown report.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def generate_report(
    workflow_accuracy: Dict,
    hallucination: Dict,
    parameter_correctness: Dict,
    reference_coverage: Dict,
    expert_evaluation: Dict | None = None,
    output_path: str = "",
) -> str:
    """Generate a comprehensive evaluation report in Markdown."""

    lines = []
    lines.append("# FlowSeq Evaluation Report v1.0.0")
    lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Test Cases**: 20 scenarios across 14 pipelines")
    lines.append(f"**Methodology**: Blind comparison — FlowSeq Skill vs Bare LLM\n")

    lines.append("---\n")
    lines.append("## Executive Summary\n")

    wa_imp = workflow_accuracy.get("improvement_pct", "N/A")
    hall_red = hallucination.get("aggregate", {}).get("reduction", "N/A")
    pc_imp = parameter_correctness.get("improvement_pct", "N/A")
    rc_imp = reference_coverage.get("improvement", "N/A")

    lines.append("| Metric | Bare LLM | FlowSeq Skill | Improvement |")
    lines.append("|--------|----------|---------------|-------------|")
    lines.append(
        f"| Workflow Selection Accuracy | "
        f"{workflow_accuracy.get('bare_llm', {}).get('accuracy', '—')} | "
        f"{workflow_accuracy.get('flowseq_skill', {}).get('accuracy', '—')} | "
        f"↑ {wa_imp} |"
    )
    lines.append(
        f"| Hallucination Rate | "
        f"{hallucination.get('aggregate', {}).get('bare_llm', {}).get('hallucination_rate', '—')} | "
        f"{hallucination.get('aggregate', {}).get('flowseq_skill', {}).get('hallucination_rate', '—')} | "
        f"↓ {hall_red} |"
    )
    lines.append(
        f"| Parameter Correctness | "
        f"{parameter_correctness.get('bare_llm', {}).get('accuracy', '—')} | "
        f"{parameter_correctness.get('flowseq_skill', {}).get('accuracy', '—')} | "
        f"↑ {pc_imp} |"
    )
    lines.append(
        f"| Reference Coverage (avg/case) | "
        f"{reference_coverage.get('bare_llm', {}).get('average_refs_per_case', '—')} | "
        f"{reference_coverage.get('flowseq_skill', {}).get('average_refs_per_case', '—')} | "
        f"{rc_imp} |"
    )

    lines.append("\n---\n")
    lines.append("## 1. Workflow Selection Accuracy\n")
    lines.append("**Definition**: Percentage of test cases where the system correctly matches the user scenario to the right pipeline.\n")
    lines.append(f"- Bare LLM: {workflow_accuracy.get('bare_llm', {}).get('correct', '—')}/{workflow_accuracy.get('total_cases', '—')} correct")
    lines.append(f"- FlowSeq Skill: {workflow_accuracy.get('flowseq_skill', {}).get('correct', '—')}/{workflow_accuracy.get('total_cases', '—')} correct")
    lines.append(f"- Improvement: {wa_imp}")

    # Per-case details if available
    skill_details = workflow_accuracy.get("skill_details", [])
    if skill_details:
        lines.append("\n### Error Cases (FlowSeq)\n")
        errors = [d for d in skill_details if not d["correct"]]
        if errors:
            for e in errors:
                lines.append(f"- **{e['id']}**: expected `{e['expected']}`, predicted `{e['predicted']}`")
        else:
            lines.append("No errors — all cases correctly matched.")

    lines.append("\n---\n")
    lines.append("## 2. Hallucination Reduction\n")
    lines.append("**Definition**: Rate at which the system generates fabricated tool names, versions, Docker images, or parameters.\n")

    by_field = hallucination.get("by_field", {})
    if by_field:
        lines.append("| Field | LLM Hallucination Rate | Skill Hallucination Rate | Reduction |")
        lines.append("|-------|----------------------|------------------------|-----------|")
        for field, data in by_field.items():
            llm_r = data.get("bare_llm", {}).get("hallucination_rate", "—")
            skill_r = data.get("flowseq_skill", {}).get("hallucination_rate", "—")
            red = data.get("reduction_pct", "—")
            lines.append(f"| {field} | {llm_r} | {skill_r} | ↓ {red} |")

    lines.append("\n---\n")
    lines.append("## 3. Parameter Correctness\n")
    lines.append("**Definition**: Whether recommended tool parameters match official documentation and community best practices.\n")
    lines.append(f"- Bare LLM: {parameter_correctness.get('bare_llm', {}).get('correct', '—')}/{parameter_correctness.get('bare_llm', {}).get('total_checked', '—')} correct")
    lines.append(f"- FlowSeq Skill: {parameter_correctness.get('flowseq_skill', {}).get('correct', '—')}/{parameter_correctness.get('flowseq_skill', {}).get('total_checked', '—')} correct")
    lines.append(f"- Improvement: {pc_imp}")

    lines.append("\n---\n")
    lines.append("## 4. Reference Coverage\n")
    lines.append("**Definition**: Average number of verifiable references (official docs, papers, community pipelines) per output.\n")
    lines.append(f"- Bare LLM: {reference_coverage.get('bare_llm', {}).get('average_refs_per_case', '—')} refs/case ({reference_coverage.get('bare_llm', {}).get('cases_with_refs', '—')} of cases have references)")
    lines.append(f"- FlowSeq Skill: {reference_coverage.get('flowseq_skill', {}).get('average_refs_per_case', '—')} refs/case ({reference_coverage.get('flowseq_skill', {}).get('cases_with_refs', '—')} of cases have references)")

    lines.append("\n---\n")
    lines.append("## 5. Expert Evaluation\n")
    if expert_evaluation:
        lines.append(f"**Status**: {'Completed' if expert_evaluation.get('completed') else 'Pending'}")
        lines.append(f"**Evaluators**: {expert_evaluation.get('evaluator_count', 'TBD')}")
        lines.append(f"**Protocol**: Blind review (System A vs System B, randomized)")
        lines.append(f"**Rubric**: 5 dimensions × 1-5 scale, weighted sum")
    else:
        lines.append("**Status**: Pending — expert review not yet conducted.")
        lines.append("\n### Rubric\n")
        lines.append("| Dimension | Weight | Scale |")
        lines.append("|-----------|--------|-------|")
        lines.append("| Pipeline Suitability | 30% | 1 (wrong) → 5 (best) |")
        lines.append("| Tool Version Accuracy | 20% | 1 (mostly wrong) → 5 (all accurate) |")
        lines.append("| Parameter Appropriateness | 20% | 1 (all wrong) → 5 (all sound) |")
        lines.append("| QC Thresholds | 15% | 1 (wrong) → 5 (all sound) |")
        lines.append("| Explainability | 15% | 1 (none) → 5 (fully traceable) |")

    lines.append("\n---\n")
    lines.append("## Appendix: Knowledge Base Statistics\n")
    lines.append(f"- **Total pipelines**: 14 (DNA: 8, RNA: 2, Epigenetic: 2, Microbiome: 2)")
    lines.append(f"- **Reference documents**: 4 ({'study_designs.md, patterns.md, sharp_edges.md, validations.md'})")
    lines.append(f"- **Sharp edges documented**: 14 common pitfalls")
    lines.append(f"- **Code patterns**: Nextflow DSL2 + Snakemake + WDL templates")
    lines.append(f"- **Validation rules**: 14 regex-based code review checks")

    report = "\n".join(lines)

    if output_path:
        Path(output_path).write_text(report, encoding="utf-8")
        print(f"Report saved to {output_path}")

    return report


if __name__ == "__main__":
    # Placeholder data — replace with actual evaluation results
    report = generate_report(
        workflow_accuracy={
            "total_cases": 20,
            "bare_llm": {"correct": 12, "accuracy": 0.60},
            "flowseq_skill": {"correct": 19, "accuracy": 0.95},
            "improvement_pct": "35.0%",
            "skill_details": [],
        },
        hallucination={
            "aggregate": {
                "bare_llm": {"hallucination_rate": 0.32},
                "flowseq_skill": {"hallucination_rate": 0.03},
                "reduction": 0.29,
            },
            "by_field": {},
        },
        parameter_correctness={
            "bare_llm": {"correct": 45, "total_checked": 80, "accuracy": 0.56},
            "flowseq_skill": {"correct": 72, "total_checked": 80, "accuracy": 0.90},
            "improvement_pct": "34.0%",
        },
        reference_coverage={
            "bare_llm": {"average_refs_per_case": 0.3, "cases_with_refs": "15.0%"},
            "flowseq_skill": {"average_refs_per_case": 2.8, "cases_with_refs": "100.0%"},
            "improvement": "+2.5 refs/case",
        },
        output_path=str(Path(__file__).parent.parent / "results" / "v1.0.0_report.md"),
    )
    print(report[:500] + "...")
