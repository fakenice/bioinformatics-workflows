"""Render v1.1.0 evaluation report from the corrected runner artifacts.

v1.0.0 is kept unchanged for provenance. This report supersedes its scoring
semantics: pipeline accuracy uses only the 18 cases with an expected pipeline,
unparsed predictions are not counted as correct abstentions, and metrics with a
zero denominator are excluded from the overall instead of scoring 100%.

Usage (from the repo root):
    python evaluation/metrics/render_v1_1_report.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "python" / "evaluation" / "results"
OUT = ROOT / "evaluation" / "results" / "v1.1.0_report.md"

SKILL = "report_qwen3_14b_v1_1.json"
BASELINE = "report_qwen3_14b_noskill_v1_1.json"
COMPARISON = "comparison_report_v1_1.json"

ORDER = ["pipeline_selection_accuracy", "knowledge_grounding_rate", "parameter_correctness",
         "reference_coverage", "schema_validity"]
LABEL = {
    "pipeline_selection_accuracy": "Pipeline Selection Accuracy",
    "knowledge_grounding_rate": "Knowledge Grounding Rate",
    "parameter_correctness": "Parameter Correctness",
    "reference_coverage": "Reference Coverage",
    "schema_validity": "Schema Validity",
}


def load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def metrics_of(report: dict) -> dict[str, dict]:
    return {m["metric"]: m for m in report["details"]}


def pct(x: float | None) -> str:
    return "N/A" if x is None else f"{100 * x:.1f}%"


def counts(m: dict, metric: str) -> str:
    if metric == "pipeline_selection_accuracy":
        return f"{m['correct']}/{m['total']}"
    if metric == "knowledge_grounding_rate":
        return f"{m['total_entities_cited'] - m['total_ungrounded']}/{m['total_entities_cited']} entities"
    if metric == "parameter_correctness":
        return f"{m['total_params_checked'] - m['invalid_params']}/{m['total_params_checked']} params"
    if metric == "reference_coverage":
        return f"{m['sources_found']}/{m['total_expected_sources']}"
    if metric == "schema_validity":
        return f"{m['valid_jsons']}/{m['total_json_outputs']}"
    return "—"


def delta(a: float | None, b: float | None) -> str:
    if a is None or b is None:
        return "—"
    return f"{100 * (a - b):+.1f} pt"


def main() -> int:
    skill = load(SKILL)
    base = load(BASELINE)
    comp = load(COMPARISON)
    ms, mb = metrics_of(skill), metrics_of(base)
    stats = comp["pipeline_stats"]

    L: list[str] = []
    L.append("# FlowSeq Evaluation Report v1.1.0")
    L.append("")
    L.append("**Status**: regenerated on 2026-11-02 from the committed run artifacts "
             "(`python/evaluation/results/outputs_qwen3_14b.json` and "
             "`outputs_qwen3_14b_noskill.json`). `v1.0.0_report.md` is kept unchanged for provenance; "
             "this version supersedes its scoring semantics.")
    L.append("")
    L.append("## What changed from v1.0.0")
    L.append("")
    L.append("1. **Pipeline accuracy uses 18 cases, not 20.** TC-014 and TC-017 have no expected "
             "pipeline; they are out-of-scope cases and are scored separately as abstention behaviour.")
    L.append("2. **A missing prediction is `unparsed`, not a correct abstention.** v1.0.0 counted "
             "TC-014 as correct because both the expected label and the missing prediction were "
             "`None`. Abstention now requires an explicit `__uncovered__` marker.")
    L.append("3. **Zero-denominator metrics are excluded from the overall.** Schema validity is "
             "0/0 on this run and is reported as N/A; v1.0.0 averaged it in as 100%.")
    L.append("4. **Uncertainty is reported.** Wilson 95% intervals, an exact McNemar test on the "
             "paired pipeline cases, and a minimum-detectable-difference floor are included.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Executive summary")
    L.append("")
    L.append("| Metric | Prompt + Skill | Prompt Only | Δ | + Skill (n) | Prompt Only (n) |")
    L.append("|---|---|---|---|---|---|")
    for metric in ORDER:
        a, b = ms.get(metric), mb.get(metric)
        L.append(f"| {LABEL[metric]} | {pct(a['score'] if a else None)} | "
                 f"{pct(b['score'] if b else None)} | "
                 f"{delta(a['score'] if a else None, b['score'] if b else None)} | "
                 f"{counts(a, metric) if a else '—'} | {counts(b, metric) if b else '—'} |")
    L.append(f"| **Overall ({skill['valid_metric_count']} valid metrics)** | "
             f"**{pct(skill['overall_score'])}** | **{pct(base['overall_score'])}** | "
             f"**{delta(skill['overall_score'], base['overall_score'])}** | | |")
    L.append("")
    L.append(f"Excluded from the overall: {', '.join(skill['excluded_metrics']) or 'none'} "
             "(zero denominator). The overall is the unweighted mean of the remaining metrics and "
             "is not comparable to the v1.0.0 95.3% headline, which mixed in a 0/0 = 100% score.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 1. Pipeline Selection Accuracy")
    L.append("")
    L.append(f"- Prompt + Skill: {stats['skill_correct']}/{stats['n_pipeline_cases']} "
             f"({pct(ms['pipeline_selection_accuracy']['score'])}), "
             f"Wilson 95% CI {pct(stats['skill_wilson_95'][0])}–{pct(stats['skill_wilson_95'][1])}")
    L.append(f"- Prompt Only: {stats['baseline_correct']}/{stats['n_pipeline_cases']} "
             f"({pct(mb['pipeline_selection_accuracy']['score'])}), "
             f"Wilson 95% CI {pct(stats['baseline_wilson_95'][0])}–{pct(stats['baseline_wilson_95'][1])}")
    L.append(f"- Skill-only correct: {', '.join(stats['skill_only']) or 'none'}; "
             f"baseline-only correct: {', '.join(stats['baseline_only']) or 'none'}")
    L.append(f"- Exact McNemar p = **{stats['mcnemar_exact_p']:.3f}** on "
             f"{len(stats['skill_only']) + len(stats['baseline_only'])} discordant case(s).")
    L.append(f"- Minimum detectable difference floor at n={stats['n_pipeline_cases']}: "
             f"**{100 * stats['minimum_detectable_difference']:.1f} pt** "
             "(two independent proportions, alpha=0.05, power=0.8).")
    L.append("")
    L.append("The arms differ by one case (TC-002). The intervals overlap almost completely and the "
             "paired test is not significant; this run does **not** demonstrate a pipeline-selection "
             "gain. It also cannot rule out a difference smaller than the MDE floor above.")
    L.append("")
    L.append("## 2. Out-of-scope behaviour (separate from pipeline accuracy)")
    L.append("")
    for label, report in (("Prompt + Skill", skill), ("Prompt Only", base)):
        oos = metrics_of(report)["pipeline_selection_accuracy"]["out_of_scope"]
        cases = "; ".join(
            f"{d['id']}={d['status']}" + (f" ({d['predicted']})" if d.get("predicted") else "")
            for d in oos["details"]
        )
        L.append(f"- {label}: {oos['correct']}/{oos['total']} explicit abstentions; {cases}")
    L.append("")
    L.append("Both arms answered the out-of-scope questions instead of declining: TC-014 produced no "
             "extractable pipeline id (unparsed), and TC-017 was mapped to `scrna-seq`. These outputs "
             "may predate the repository's zero-result protection commit; do not quote this as the "
             "current behaviour without regenerating the outputs.")
    L.append("")
    L.append("## 3. Knowledge Grounding Rate")
    L.append("")
    a, b = ms["knowledge_grounding_rate"], mb["knowledge_grounding_rate"]
    L.append(f"- Prompt + Skill: {a['total_ungrounded']} ungrounded entities out of "
             f"{a['total_entities_cited']} ({pct(a['score'])}).")
    L.append(f"- Prompt Only: {b['total_ungrounded']} out of {b['total_entities_cited']} "
             f"({pct(b['score'])}).")
    L.append("")
    L.append("The denominators differ because the arms cite different numbers of entities (380 vs "
             "347); the comparison is a rate, not a fixed set of citations.")
    L.append("")
    L.append("## 4. Parameter Correctness")
    L.append("")
    a, b = ms["parameter_correctness"], mb["parameter_correctness"]
    L.append(f"- Prompt + Skill: {a['total_params_checked']} parameters checked, "
             f"{a['invalid_params']} invalid.")
    L.append(f"- Prompt Only: {b['total_params_checked']} checked, {b['invalid_params']} invalid.")
    L.append("")
    L.append("Both arms score 100%, but the denominators are 15 vs 3. This means no violation was "
             "found among the extractable parameters, not that parameter generation is correct; the "
             "asymmetry mirrors output verbosity and makes the arms non-comparable on this metric.")
    L.append("")
    L.append("## 5. Reference Coverage")
    L.append("")
    a, b = ms["reference_coverage"], mb["reference_coverage"]
    L.append(f"- Prompt + Skill: {a['sources_found']}/{a['total_expected_sources']} "
             f"({pct(a['score'])}).")
    L.append(f"- Prompt Only: {b['sources_found']}/{b['total_expected_sources']} "
             f"({pct(b['score'])}).")
    L.append("")
    L.append("This is the clearest signal in the run: the same 19 expected sources, with 4 more named "
             "by the skill arm. It is a local, single-model result and not a general guarantee.")
    L.append("")
    L.append("## 6. Schema Validity")
    L.append("")
    L.append("**N/A on this run.** Neither arm produced a structured JSON output, so the denominator "
             "is zero. The metric is excluded from the overall; it is not evidence of schema "
             "compliance.")
    L.append("")
    L.append("## Caveats")
    L.append("")
    L.append("- 18 pipeline cases: the MDE floor is about 29 pt, so only a large effect is detectable.")
    L.append("- No human expert review was conducted; the rubric in the old template is not a result.")
    L.append("- The run artifacts contain no timestamp; the wall-clock date is not asserted.")
    L.append("- The committed outputs may predate later Skill changes (including zero-result "
             "protection); this report describes the committed artifacts, not the current code path.")
    L.append("")
    L.append("## Reproduce")
    L.append("")
    L.append("```bash")
    L.append("cd python")
    L.append("python evaluation/runner.py evaluation/results/outputs_qwen3_14b.json \\")
    L.append("  -o evaluation/results/report_qwen3_14b_v1_1.json")
    L.append("python evaluation/runner.py evaluation/results/outputs_qwen3_14b_noskill.json \\")
    L.append("  -o evaluation/results/report_qwen3_14b_noskill_v1_1.json")
    L.append("python evaluation/runner.py evaluation/results/outputs_qwen3_14b.json \\")
    L.append("  --baseline evaluation/results/outputs_qwen3_14b_noskill.json \\")
    L.append("  -o evaluation/results/comparison_report_v1_1.json")
    L.append("cd ..")
    L.append("python evaluation/metrics/render_v1_1_report.py")
    L.append("```")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
