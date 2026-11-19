# Extended 30-case evaluation report (skill vs prompt-only ablation)

Rendered by `evaluation/metrics/render_ext30_report.py` from the committed artifacts `python/evaluation/results/report_ext30_{skill,noskill}.json`, `report_ext30_stats.json` and `outputs_ext30_*_meta.json`. No model call and no hard-coded number happens here; regenerate with `python analyze_ext30.py` from `python/evaluation/` before rendering.

## Protocol

- **skill**: `qwen3:14b` via http://localhost:11434/api/generate (arm=skill), `think=False`, `temperature=0.3`, system prompt 7475 chars, sha256 `33d105c117a2…`, 30 cases, generated 2026-11-19T23:18:20 (2353.3 s)
- **prompt_only**: `qwen3:14b` via http://localhost:11434/api/generate (arm=noskill), `think=False`, `temperature=0.3`, system prompt 158 chars, sha256 `3851f8ec415a…`, 30 cases, generated 2026-11-19T23:55:10 (2208.8 s)
- Cases: 30 total, 26 with an expected pipeline, 4 uncovered (TC-014, TC-017, TC-028, TC-029). Scoring path: runner.load_outputs -> runner._to_predictions -> workflow_accuracy.compute; reference coverage read back from the committed per-case report details.

## Pipeline selection, three paired ways

| Mode | Cases | + Skill | Prompt only | Δ (pt) | McNemar b/c | exact p | Wilson 95% (skill / prompt) | What the design can resolve |
|---|---|---|---|---|---|---|---|---|
| strict_intersection | 22 | 19 (86.36 %) | 19 (86.36 %) | +0.00 | 1/1 | 1.0 | 66.7–95.2 % / 66.7–95.2 % | even a unanimous split of the 2 discordant cases gives p = 0.5 |
| all_in_scope | 26 | 19 (73.08 %) | 21 (80.77 %) | -7.69 | 1/3 | 0.625 | 53.9–86.3 % / 62.1–91.5 % | even a unanimous split of the 4 discordant cases gives p = 0.125 |
| lenient | 26 | 19 (73.08 %) | 22 (84.62 %) | -11.54 | 0/3 | 0.25 | 53.9–86.3 % / 66.5–93.8 % | even a unanimous split of the 3 discordant cases gives p = 0.25 |

The runner prints 19/26 vs 21/26, which is **not** a paired comparison: the two 26-case denominators are not the same 26 cases: the extractor resolved a different subset in each arm.

## Extractor audit (why the printed denominators differ)

- Unresolved in-scope answers: + Skill 4, prompt only 2. unparsed means the extractor could not pull a pipeline id out of the answer, not that generation failed; see text_names_expected_id for how many of those answers in fact name the expected pipeline
- + Skill TC-020: expected `family-trio-wgs`, extractor status `unparsed`, answer names the expected id in text: False
- + Skill TC-021: expected `rna-seq`, extractor status `unparsed`, answer names the expected id in text: False
- + Skill TC-024: expected `wgs-germline`, extractor status `unparsed`, answer names the expected id in text: False
- + Skill TC-025: expected `wgs-germline`, extractor status `unparsed`, answer names the expected id in text: False
- prompt only TC-024: expected `wgs-germline`, extractor status `unparsed`, answer names the expected id in text: False
- prompt only TC-025: expected `wgs-germline`, extractor status `unparsed`, answer names the expected id in text: False

## Out-of-scope questions (abstention)

- + Skill: answered 1/4 (TC-014=unparsed, TC-017=unparsed, TC-028=answered, TC-029=unparsed)
- prompt only: answered 3/4 (TC-014=unparsed, TC-017=answered, TC-028=answered, TC-029=answered)
- No case produced `__uncovered__`, so abstention credit is 0 for both arms and the uncovered path in `python/evaluation/metrics/workflow_accuracy.py` remains untested against real output.

## Reference coverage (paired at case level)

- Cases with expected sources: 23; any-source hit + Skill 17, prompt only 18; discordant 4/5, exact p = 1.0; needs at least 8:1 of 9 (p = 0.039062).
- case-level any-source hit; the runner aggregate 18/28 vs 17/28 averages source-level recall inside cases and is not paired

## Sensitivity

- unpaired sensitivity floor, kept only as a magnitude reference; the paired design's resolution is pipeline_selection.*.paired_resolution — computed as: with n = 26 per arm, p = 0.5, α = 0.05 and power = 0.80, the smallest two-proportion gap this design could detect at all is 38.9 pt. Use the per-row `paired_resolution` above, not this number, to judge any claim.

## Per-arm metric tables

| Metric | + Skill | Prompt only |
|---|---|---|
| Pipeline Selection Accuracy | 73.08 % (19/26) | 80.77 % (21/26) |
| Knowledge Grounding Rate | 96.81 % (637/658 entities) | 93.39 % (721/772 entities) |
| Parameter Correctness | 100.00 % (12 valid/12 checked) | 100.00 % (17 valid/17 checked) |
| Reference Coverage | 64.29 % (18/28) | 60.71 % (17/28) |
| Schema Validity | — (0/0) | — (0/0) |
- skill: overall 83.55 % over 4 valid metrics; excluded: schema_validity
- prompt_only: overall 83.72 % over 4 valid metrics; excluded: schema_validity

## Declared case fields that no metric scores

- `must_flag_traps` and `must_apply_validations` exist on every case and are referenced by no metric module in `python/evaluation/metrics/`; they are not part of any score above.
- `must_include_params` declares per-case parameter constraints, but `parameter_correctness.py` range-checks only its own hardcoded parameter names where they appear in the answer text, so its 100 % means "nothing extractable was out of range".
- `parameter_correctness.py` defines an unused `PIPELINES_DIR` that points at a directory which does not exist in this repository.

