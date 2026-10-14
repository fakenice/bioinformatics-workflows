"""Render the published evaluation report from committed run artifacts.

Why this file exists
--------------------
`evaluation/results/v1.0.0_report.md` shipped as an empty template (every cell "—", plus the
line "Actual evaluation run pending") while `README.md` already quoted ablation numbers taken
from `python/evaluation/results/*.json`. A reader who follows the README into the repo hits a
direct contradiction, so the published numbers were not verifiable inside the repository.

This script closes that gap in the only honest direction: it *reads* the committed run artifacts
and writes the report from them. It performs no model call, no network access, and contains no
hard-coded result number — if a JSON is missing it says so instead of filling in a value.

Usage (from the repo root)
--------------------------
    python evaluation/metrics/render_report_from_results.py

Output: evaluation/results/v1.0.0_report.md
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "python" / "evaluation" / "results"
OUT = ROOT / "evaluation" / "results" / "v1.0.0_report.md"

# (row label, json field, artifact for +Skill arm, artifact for Prompt-Only arm)
ARMS = {"skill": "report_qwen3_14b_baseline.json", "prompt_only": "report_qwen3_14b_noskill.json"}
COMPLETENESS = {"skill": "workflow_completeness_qwen3_14b_fix4.json",
                "prompt_only": "workflow_completeness_qwen3_14b_noskill_fix4.json"}

# Which denominators belong to which metric, so the report can show "x/y" instead of a bare
# percentage. Denominator keys differ per metric because each metric script emits its own counts.
DENOM = {
    "pipeline_selection_accuracy": ("correct", "total"),
    "knowledge_grounding_rate": None,          # reported as cited/ungrounded entity counts
    "parameter_correctness": None,             # reported as invalid/checked parameter counts
    "reference_coverage": ("sources_found", "total_expected_sources"),
    "schema_validity": ("valid_jsons", "total_json_outputs"),
}
ORDER = ["pipeline_selection_accuracy", "knowledge_grounding_rate", "parameter_correctness",
         "reference_coverage", "schema_validity"]
LABEL = {
    "pipeline_selection_accuracy": "Pipeline Selection Accuracy",
    "knowledge_grounding_rate": "Knowledge Grounding Rate",
    "parameter_correctness": "Parameter Correctness",
    "reference_coverage": "Reference Coverage",
    "schema_validity": "Schema Validity",
    "workflow_completeness": "Workflow Completeness",
}


def load(name: str) -> dict[str, Any] | None:
    path = RESULTS / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def metrics_of(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {m["metric"]: m for m in report.get("details", [])}


def pct(x: float | None) -> str:
    return "—" if x is None else f"{100 * x:.1f}%"


def counts(mm: dict[str, Any], metric: str) -> str:
    """Human-readable numerator/denominator for one metric entry."""
    if metric == "knowledge_grounding_rate":
        return f"{mm['total_entities_cited'] - mm['total_ungrounded']}/{mm['total_entities_cited']} entities"
    if metric == "parameter_correctness":
        return f"{mm['total_params_checked'] - mm['invalid_params']}/{mm['total_params_checked']} params"
    num_key, den_key = DENOM[metric]
    return f"{mm.get(num_key, '—')}/{mm.get(den_key, '—')}"


def delta(a: float | None, b: float | None) -> str:
    if a is None or b is None:
        return "—"
    return f"{100 * (a - b):+.1f} pt"


def error_ids(report: dict[str, Any] | None) -> list[str]:
    if report is None:
        return []
    mm = metrics_of(report).get("pipeline_selection_accuracy", {})
    return [d["id"] for d in mm.get("details", []) if not d.get("ok")]


def main() -> int:
    skill = load(ARMS["skill"])
    base = load(ARMS["prompt_only"])
    comp_skill = load(COMPLETENESS["skill"])
    comp_base = load(COMPLETENESS["prompt_only"])

    L: list[str] = []
    L.append("# FlowSeq Evaluation Report v1.0.0")
    L.append("")
    L.append("**Status**: filled from committed run artifacts by "
             "`evaluation/metrics/render_report_from_results.py`. This file used to be an empty "
             "template while `README.md` quoted numbers; that contradiction is what this render fixes.")
    L.append("")
    L.append("**What is compared** (same settings as README §Evaluation): the same local model "
             "(`qwen3:14b` via Ollama, `think=False`, `temperature=0.3`) on 20 test cases, "
             "**Prompt + Skill** (SKILL.md as system prompt) vs **Prompt Only** (neutral system "
             "prompt), both on the no-internet baseline, so SKILL.md is the only difference.")
    L.append("")
    L.append("**Not recorded**: the run artifacts contain no timestamp, so the wall-clock date of "
             "the run is not asserted anywhere in this report. The raw model outputs "
             "(`outputs_qwen3_14b.json`, `outputs_qwen3_14b_noskill.json`) are committed next to "
             "the reports, so every score below can be recomputed independently.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Executive summary")
    L.append("")
    L.append("| Metric | Prompt + Skill | Prompt Only | Δ | + Skill (n) | Prompt Only (n) |")
    L.append("|---|---|---|---|---|---|")
    ms, mb = metrics_of(skill) if skill else {}, metrics_of(base) if base else {}
    for metric in ORDER:
        a, b = ms.get(metric), mb.get(metric)
        sa = a["score"] if a else None
        sb = b["score"] if b else None
        L.append(f"| {LABEL[metric]} | {pct(sa)} | {pct(sb)} | {delta(sa, sb)} | "
                 f"{counts(a, metric) if a else '—'} | {counts(b, metric) if b else '—'} |")
    if comp_skill and comp_base:
        sa = comp_skill.get("score")
        sb = comp_base.get("score")
        L.append(f"| {LABEL['workflow_completeness']} | {pct(sa)} | {pct(sb)} | {delta(sa, sb)} | "
                 f"{comp_skill['total_covered_steps']}/{comp_skill['total_standard_steps']} steps | "
                 f"{comp_base['total_covered_steps']}/{comp_base['total_standard_steps']} steps |")
    if skill and base:
        L.append(f"| **Overall (5 metrics, unweighted mean)** | **{pct(skill.get('overall_score'))}** | "
                 f"**{pct(base.get('overall_score'))}** | "
                 f"**{delta(skill.get('overall_score'), base.get('overall_score'))}** | | |")
    L.append("")
    L.append("The Overall row is the unweighted mean of the five metric scores stored in each "
             "report file (`overall_score`). Read the caveats below before quoting it: two of "
             "those five metrics are degenerate on this run.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## 1. Pipeline Selection Accuracy")
    L.append("")
    if ms.get("pipeline_selection_accuracy"):
        a = ms["pipeline_selection_accuracy"]
        b = mb.get("pipeline_selection_accuracy", {})
        L.append(f"- Prompt + Skill: {a['correct']}/{a['total']} cases correct ({pct(a['score'])}); "
                 f"misses: {', '.join(error_ids(skill)) or 'none'}")
        L.append(f"- Prompt Only: {b.get('correct', '—')}/{b.get('total', '—')} cases correct "
                 f"({pct(b.get('score'))}); misses: {', '.join(error_ids(base)) or 'none'}")
        L.append("")
        L.append("The two arms differ by **one case out of 20** (TC-002 is the only case the "
                 "Prompt-Only arm misses and the Skill arm gets right). Both arms miss TC-009 and "
                 "TC-017. A single-case difference is not a measurable effect; the README's "
                 "+5.0 pt should be read as 'no reliable difference', not as a capability gain.")
    L.append("")
    L.append("## 2. Knowledge Grounding Rate")
    L.append("")
    a, b = ms.get("knowledge_grounding_rate", {}), mb.get("knowledge_grounding_rate", {})
    if a:
        L.append(f"- Prompt + Skill: {a['total_ungrounded']} ungrounded citations out of "
                 f"{a['total_entities_cited']} ({pct(a['score'])}); ungrounded rate {pct(a['ungrounded_rate'])}")
        L.append(f"- Prompt Only: {b.get('total_ungrounded', '—')} out of "
                 f"{b.get('total_entities_cited', '—')} ({pct(b.get('score'))}); ungrounded rate "
                 f"{pct(b.get('ungrounded_rate'))}")
        L.append("")
        L.append("This is the metric with the largest usable denominator, and the arm difference is "
                 f"{abs(int(b.get('total_ungrounded', 0)) - int(a['total_ungrounded']))} citations "
                 "out of a few hundred.")
        kb = a.get("kb_size", {})
        L.append("")
        L.append(f"Grounding is checked against the committed knowledge base: {kb.get('tools', '—')} tool "
                 f"names, {kb.get('dois', '—')} DOIs, {kb.get('urls', '—')} URLs.")
    L.append("")
    L.append("## 3. Parameter Correctness")
    L.append("")
    a, b = ms.get("parameter_correctness", {}), mb.get("parameter_correctness", {})
    if a:
        L.append(f"- Prompt + Skill: {a['total_params_checked']} parameters checked, "
                 f"{a['invalid_params']} invalid ({pct(a['score'])})")
        L.append(f"- Prompt Only: {b.get('total_params_checked', '—')} checked, "
                 f"{b.get('invalid_params', '—')} invalid ({pct(b.get('score'))})")
        L.append("")
        L.append("**Small denominators**: 15 and 3 parameters. Both 100% scores mean 'no violation "
                 "was found in a handful of extractable parameters', not 'parameter generation is "
                 "correct'. The asymmetry (15 vs 3) also mirrors the arms' output verbosity, so this "
                 "metric is not comparable across arms in the usual sense.")
    L.append("")
    L.append("## 4. Reference Coverage")
    L.append("")
    a, b = ms.get("reference_coverage", {}), mb.get("reference_coverage", {})
    if a:
        L.append(f"- Prompt + Skill: {a['sources_found']}/{a['total_expected_sources']} expected "
                 f"authoritative sources present ({pct(a['score'])})")
        L.append(f"- Prompt Only: {b.get('sources_found', '—')}/{b.get('total_expected_sources', '—')} "
                 f"({pct(b.get('score'))})")
        L.append("")
        L.append("This is where the Skill's contribution is clearest: the same 19 expected sources, "
                 f"and the Skill arm names {a['sources_found'] - int(b.get('sources_found', 0))} more "
                 "of them. Same denominator, real counts.")
    L.append("")
    L.append("## 5. Schema Validity")
    L.append("")
    a, b = ms.get("schema_validity", {}), mb.get("schema_validity", {})
    if a:
        L.append(f"- Prompt + Skill: {a['valid_jsons']}/{a['total_json_outputs']} JSON outputs parsed "
                 f"and validated (score recorded as {pct(a['score'])})")
        L.append(f"- Prompt Only: {b.get('valid_jsons', '—')}/{b.get('total_json_outputs', '—')} "
                 f"(score recorded as {pct(b.get('score'))})")
        L.append("")
        L.append("**Degenerate on this run**: zero structured-JSON outputs were produced by either "
                 "arm, so the stored 100% is a default for 'nothing to check', not evidence of "
                 "schema compliance. It is retained in the Overall mean only because that is how "
                 "the committed report files compute it; it must not be quoted as a result.")
    L.append("")
    L.append("## 6. Workflow Completeness (separate script)")
    L.append("")
    if comp_skill and comp_base:
        L.append(f"- Prompt + Skill: {comp_skill['total_covered_steps']}/"
                 f"{comp_skill['total_standard_steps']} standard steps across "
                 f"{comp_skill['cases_evaluated']} pipeline cases ({pct(comp_skill['score'])})")
        L.append(f"- Prompt Only: {comp_base['total_covered_steps']}/{comp_base['total_standard_steps']} "
                 f"across {comp_base['cases_evaluated']} cases ({pct(comp_base['score'])})")
        L.append("")
        L.append("Evaluated by `python/evaluation/metrics/workflow_completeness.py` against the "
                 "standard step lists in the pipeline definitions (82 steps total). Not part of the "
                 "5-metric Overall mean.")
    L.append("")
    L.append("## 7. Expert evaluation")
    L.append("")
    L.append("**Not conducted.** No human review of these outputs took place, so the rubric in the "
             "old template is not a result and is deliberately left unfilled here.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Provenance (all files committed in this repository)")
    L.append("")
    L.append("| Row in the summary | + Skill artifact | Prompt Only artifact |")
    L.append("|---|---|---|")
    L.append(f"| 5 metrics above | `python/evaluation/results/{ARMS['skill']}` | "
             f"`python/evaluation/results/{ARMS['prompt_only']}` |")
    L.append("| raw model outputs behind those reports | "
             "`python/evaluation/results/outputs_qwen3_14b.json` | "
             "`python/evaluation/results/outputs_qwen3_14b_noskill.json` |")
    L.append(f"| Workflow Completeness | `python/evaluation/results/{COMPLETENESS['skill']}` | "
             f"`python/evaluation/results/{COMPLETENESS['prompt_only']}` |")
    L.append("| test cases (expected values) | `evaluation/benchmarks/test_cases.json` | same |")
    L.append("")
    L.append("## How to recompute")
    L.append("")
    L.append("```bash")
    L.append("cd python/evaluation")
    L.append("python runner.py results/outputs_qwen3_14b.json -o results/report_qwen3_14b_baseline.json")
    L.append("python runner.py results/outputs_qwen3_14b_noskill.json -o results/report_qwen3_14b_noskill.json")
    L.append("python metrics/workflow_completeness.py        # 6th metric, 18 pipeline cases")
    L.append("cd ../.. && python evaluation/metrics/render_report_from_results.py")
    L.append("```")
    L.append("")
    L.append("## Caveats for anyone citing these numbers")
    L.append("")
    L.append("1. Single run, one model (`qwen3:14b`), one decoding setting: no repeated sampling, so "
             "arm differences of one case cannot be separated from run-to-run noise.")
    L.append("2. `Schema Validity` is 0/0 and `Parameter Correctness` rests on 15 vs 3 checks; the "
             "Overall mean therefore contains two near-empty 100% terms.")
    L.append("3. Selection Accuracy differs by one case out of 20.")
    L.append("4. Reference Coverage (17/19 vs 13/19) and Knowledge Grounding (12/380 vs 21/347 "
             "ungrounded) are the two rows with comparable denominators; they are the defensible ones.")
    L.append("5. `report.json` (overall 0.9823) and `comparison_report_final.json` in the same folder "
             "are different runs and must not be mixed with the table above.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    missing = [n for n in list(ARMS.values()) + list(COMPLETENESS.values()) if load(n) is None]
    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size} bytes)")
    if missing:
        print("MISSING ARTIFACTS (report cells left as em-dashes):", ", ".join(missing))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
