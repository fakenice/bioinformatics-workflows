"""Render the 30-case extended evaluation report from committed run artifacts.

Same rule as ``render_report_from_results.py``: this file reads JSON and writes
Markdown. It performs no model call, no network access and contains no hard-coded
result number — when an artifact is missing it prints a MISSING line instead of a
value, so a reader can tell an unrun check from a measured one.

Usage (from the repo root)
--------------------------
    python evaluation/metrics/render_ext30_report.py

Output: evaluation/results/ext30_report.md
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "python" / "evaluation" / "results"
OUT = ROOT / "evaluation" / "results" / "ext30_report.md"

STATS = "report_ext30_stats.json"
ARM_FILES = {"skill": "report_ext30_skill.json", "prompt_only": "report_ext30_noskill.json"}
META_FILES = {"skill": "outputs_ext30_skill_meta.json", "prompt_only": "outputs_ext30_noskill_meta.json"}

METRIC_ORDER = [
    ("pipeline_selection_accuracy", "Pipeline Selection Accuracy"),
    ("knowledge_grounding_rate", "Knowledge Grounding Rate"),
    ("parameter_correctness", "Parameter Correctness"),
    ("reference_coverage", "Reference Coverage"),
    ("schema_validity", "Schema Validity"),
]
# Which count keys each metric uses for its "x/y", so the table shows denominators.
METRIC_DENOM = {
    "pipeline_selection_accuracy": ("correct", "total"),
    "knowledge_grounding_rate": ("total_entities_cited", None),
    "parameter_correctness": ("total_params_checked", None),
    "reference_coverage": ("sources_found", "total_expected_sources"),
    "schema_validity": ("valid_jsons", "total_json_outputs"),
}


def load(name: str) -> dict[str, Any] | None:
    path = RESULTS / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def arm_details(report: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not report:
        return {}
    return {d.get("metric", "?"): d for d in report.get("details", []) if isinstance(d, dict)}


def pct(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.2f} %"


def count(metric: str, detail: dict[str, Any] | None) -> str:
    if not detail:
        return "—"
    num_key, den_key = METRIC_DENOM[metric]
    num = detail.get(num_key)
    if num is None:
        return "—"
    if den_key is None:
        # grounding and parameter correctness report the checked total and the
        # failing subset under different names; show what the artifact carries.
        if metric == "knowledge_grounding_rate":
            return f"{num - detail.get('total_ungrounded', 0)}/{num} entities"
        return f"{num - detail.get('invalid_params', 0)} valid/{num} checked"
    den = detail.get(den_key)
    return f"{num}/{den}"


def wilson(pair: list[float] | None) -> str:
    if not pair:
        return "—"
    return f"{pair[0] * 100:.1f}–{pair[1] * 100:.1f} %"


def resolution(row: dict[str, Any]) -> str:
    res = row.get("paired_resolution", {})
    split = res.get("minimum_split")
    if split is None:
        return f"even a unanimous split of the {res.get('n_discordant')} discordant cases gives p = {res.get('p_at_minimum_split')}"
    return f"needs at least {split} of {res.get('n_discordant')} (p = {res.get('p_at_minimum_split')})"


def main() -> int:
    stats = load(STATS)
    arms = {arm: load(name) for arm, name in ARM_FILES.items()}
    metas = {arm: load(name) for arm, name in META_FILES.items()}

    L: list[str] = []
    L.append("# Extended 30-case evaluation report (skill vs prompt-only ablation)")
    L.append("")
    L.append("Rendered by `evaluation/metrics/render_ext30_report.py` from the committed artifacts "
              "`python/evaluation/results/report_ext30_{skill,noskill}.json`, "
              "`report_ext30_stats.json` and `outputs_ext30_*_meta.json`. "
              "No model call and no hard-coded number happens here; regenerate with "
              "`python analyze_ext30.py` from `python/evaluation/` before rendering.")
    L.append("")
    if stats is None:
        L.append(f"**MISSING**: `{STATS}` — run `python analyze_ext30.py` in `python/evaluation/`.")
        OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
        print(f"wrote {OUT} (stats artifact missing)")
        return 0

    proto = stats["protocol"]
    L.append("## Protocol")
    L.append("")
    for arm in ("skill", "prompt_only"):
        meta = metas.get(arm)
        if not meta:
            L.append(f"- **{arm}**: MISSING `{META_FILES[arm]}`")
            continue
        L.append(
            f"- **{arm}**: `{meta.get('model')}` via {meta.get('endpoint')} "
            f"(arm={meta.get('arm')}), `think={meta.get('think')}`, `temperature={meta.get('temperature')}`, "
            f"system prompt {meta.get('system_prompt_chars')} chars, "
            f"sha256 `{str(meta.get('system_prompt_sha256'))[:12]}…`, "
            f"{meta.get('n_cases')} cases, generated {meta.get('generated_at')} "
            f"({meta.get('wall_seconds_total_this_invocation')} s)"
        )
    L.append(
        f"- Cases: {proto['n_cases']} total, {proto['in_scope_cases']} with an expected pipeline, "
        f"{len(proto['out_of_scope_cases'])} uncovered ({', '.join(proto['out_of_scope_cases'])}). "
        f"Scoring path: {proto['scoring_path']}."
    )
    L.append("")

    L.append("## Pipeline selection, three paired ways")
    L.append("")
    L.append("| Mode | Cases | + Skill | Prompt only | Δ (pt) | McNemar b/c | exact p | Wilson 95% (skill / prompt) | What the design can resolve |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    ps = stats["pipeline_selection"]
    runner_row = ps["as_runner_prints_it"]
    for mode in ("strict_intersection", "all_in_scope", "lenient"):
        row = ps[mode]
        L.append(
            f"| {mode} | {row['n']} | {row['skill_correct']} ({pct(row['skill_rate'])}) | "
            f"{row['noskill_correct']} ({pct(row['noskill_rate'])}) | {row['delta_skill_minus_noskill_pt']:+.2f} | "
            f"{row['discordant']['skill_only']}/{row['discordant']['noskill_only']} | "
            f"{row['mcnemar_exact_two_sided_p']} | {wilson(row.get('skill_wilson_95'))} / {wilson(row.get('noskill_wilson_95'))} | "
            f"{resolution(row)} |"
        )
    L.append("")
    L.append(f"The runner prints {runner_row['skill']['correct']}/{runner_row['skill']['denominator']} vs "
              f"{runner_row['noskill']['correct']}/{runner_row['noskill']['denominator']}, which is **not** a paired "
              f"comparison: {runner_row['why_this_is_not_the_paired_test']}.")
    L.append("")

    audit = stats["extractor_audit"]
    L.append("## Extractor audit (why the printed denominators differ)")
    L.append("")
    L.append(f"- Unresolved in-scope answers: + Skill {audit['unparsed_counts']['skill']}, "
              f"prompt only {audit['unparsed_counts']['noskill']}. "
              f"{audit['reading']}")
    for arm_key, label in (("skill", "+ Skill"), ("noskill", "prompt only")):
        for cid, info in sorted(audit["unparsed_in_scope"].get(arm_key, {}).items()):
            L.append(
                f"- {label} {cid}: expected `{info['expected']}`, "
                f"extractor status `{info['status']}`, "
                f"answer names the expected id in text: {info['text_names_expected_id']}"
            )
    L.append("")

    abst = stats["out_of_scope_abstention"]
    L.append("## Out-of-scope questions (abstention)")
    L.append("")
    for arm_key, label in (("skill", "+ Skill"), ("noskill", "prompt only")):
        states = abst[arm_key]
        answered = sum(1 for v in states.values() if v == "answered")
        L.append(f"- {label}: answered {answered}/{len(states)} ({', '.join(f'{k}={v}' for k, v in sorted(states.items()))})")
    L.append("- No case produced `__uncovered__`, so abstention credit is 0 for both arms and the uncovered "
              "path in `python/evaluation/metrics/workflow_accuracy.py` remains untested against real output.")
    L.append("")

    rc = stats["reference_coverage"]
    L.append("## Reference coverage (paired at case level)")
    L.append("")
    L.append(f"- Cases with expected sources: {rc['n_cases_with_expected_sources']}; any-source hit "
              f"+ Skill {rc['skill_cases_with_any_hit']}, prompt only {rc['noskill_cases_with_any_hit']}; "
              f"discordant {rc['discordant']['skill_only']}/{rc['discordant']['noskill_only']}, "
              f"exact p = {rc['mcnemar_exact_two_sided_p']}; {resolution(rc)}.")
    L.append(f"- {rc['note']}")
    L.append("")

    mde = stats["independent_two_sample_mde"]
    L.append("## Sensitivity")
    L.append("")
    L.append(f"- {mde['caveat']} — computed as: with n = {mde['n_per_arm']} per arm, p = 0.5, α = 0.05 and power = 0.80, "
              f"the smallest two-proportion gap this design could detect at all is "
              f"{mde['at_p0.5_alpha0.05_power0.80'] * 100:.1f} pt. Use the per-row `paired_resolution` above, not this "
              "number, to judge any claim.")
    L.append("")

    L.append("## Per-arm metric tables")
    L.append("")
    L.append("| Metric | + Skill | Prompt only |")
    L.append("|---|---|---|")
    details = {arm: arm_details(report) for arm, report in arms.items()}
    for key, label in METRIC_ORDER:
        cells = []
        for arm in ("skill", "prompt_only"):
            rep = arms[arm]
            if rep is None:
                cells.append(f"MISSING `{ARM_FILES[arm]}`")
                continue
            score = rep.get("scores", {}).get(key)
            cells.append(f"{pct(score)} ({count(key, details[arm].get(key))})")
        L.append(f"| {label} | {cells[0]} | {cells[1]} |")
    for arm in ("skill", "prompt_only"):
        rep = arms[arm]
        if rep:
            L.append(
                f"- {arm}: overall {pct(rep.get('overall_score'))} over "
                f"{rep.get('valid_metric_count')} valid metrics; excluded: "
                f"{', '.join(rep.get('excluded_metrics', [])) or 'none'}"
            )
    L.append("")

    L.append("## Declared case fields that no metric scores")
    L.append("")
    L.append("- `must_flag_traps` and `must_apply_validations` exist on every case and are referenced by no "
              "metric module in `python/evaluation/metrics/`; they are not part of any score above.")
    L.append("- `must_include_params` declares per-case parameter constraints, but "
              "`parameter_correctness.py` range-checks only its own hardcoded parameter names where they "
              "appear in the answer text, so its 100 % means \"nothing extractable was out of range\".")
    L.append("- `parameter_correctness.py` defines an unused `PIPELINES_DIR` that points at a directory "
              "which does not exist in this repository.")
    L.append("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
