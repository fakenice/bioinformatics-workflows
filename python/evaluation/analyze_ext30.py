"""ext30（30 用例）消融的配对统计复核：把 README 表里的 Δ 列换成可检验的量。

为什么要单独写这个脚本：`runner.py --baseline` 打印的是两个臂各自分母上的百分比相减，
而分母本身会随解析结果变化——本次 skill 臂有 4 个在用例内抽不出 pipeline_id，
noskill 臂只有 2 个。分母不同的两个数相减不是配对比较：Δ=−9.5% 里既有模型的成分，
也有抽取器的成分。本脚本不重新打分（口径全部复用 runner.py / workflow_accuracy.py，
避免同一仓库出现两套分数），只做三件事：

1. 配对：按 case id 对齐两臂逐题对错，给出一致/不一致计数 b、c；
2. 检验：精确 McNemar 在三种分母口径下各算一次——严格交集（两臂都抽出来的题）、
   全部在用例（抽不出计为错）、宽松（正文里出现预期 pipeline_id 或其别名即算命中），
   用来分离"模型答错"与"抽取器没抽出来"；
3. 分辨率：固定观测到的不一致总数 n_disc，算精确二侧检验要拒绝 H0 所需的最小分裂
   x:(n_disc−x)。这才是配对设计"能看见多大差异"的下限；独立两样本 MDE 也一并写入
   产物，但只作量级参照。

输入：results/outputs_ext30_{skill,noskill}.json、results/report_ext30_*.json、
      benchmarks/test_cases.json
输出：results/report_ext30_stats.json
stdout 只打 ASCII 摘要（Windows GBK 控制台打中文会炸，故细节看 JSON）。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))  # python/

from evaluation import runner
from evaluation.metrics import statistics

RESULTS = ROOT / "results"
BENCHMARKS = ROOT / "benchmarks" / "test_cases.json"
ARMS = ("skill", "noskill")

# 与 runner._to_predictions 末尾的 alias_map 保持一致：宽松口径也要过同一层归一化
ALIASES = {"trio-wgs-denovo": "family-trio-wgs"}


def lenient_names(expected_id: str) -> list[str]:
    return [expected_id, *(a for a, target in ALIASES.items() if target == expected_id)]


def names_expected_id(text: str, expected_id: str) -> bool:
    """宽松口径：预期 pipeline_id（含别名）作为独立 token 出现在正文中即算命中。

    要求词边界，避免 `wes` 命中 western、`prs` 命中无关片段。只用于口径敏感性分析，
    不替换正式分数。
    """
    return any(
        re.search(rf"(?<![A-Za-z0-9_-]){re.escape(n)}(?![A-Za-z0-9_-])", text)
        for n in lenient_names(expected_id)
    )


def min_split_for_significance(n_disc: int, alpha: float = 0.05) -> dict:
    """不一致总数固定为 n_disc 时，精确二侧 McNemar 能拒绝 H0 的最小分裂。

    直接用 `statistics.mcnemar_exact(x, n_disc - x)`，不再在本文件里二次实现同一个
    检验——之前的手写内联版本把"另一侧计数"当成了二项总数传给 comb，n_disc 较小时
    会返回 0.0，从而虚报了本次设计的分辨率。
    """
    if n_disc <= 0:
        return {"n_discordant": 0, "minimum_split": None, "p_at_minimum_split": None,
                "note": "no discordant pairs at all; a paired test has nothing to resolve"}
    for x in range(n_disc // 2 + 1, n_disc + 1):
        p = statistics.mcnemar_exact(x, n_disc - x)
        if p < alpha:
            return {"n_discordant": n_disc, "minimum_split": f"{x}:{n_disc - x}",
                    "p_at_minimum_split": round(p, 6)}
    return {"n_discordant": n_disc, "minimum_split": None,
            "p_at_minimum_split": round(statistics.mcnemar_exact(n_disc, 0), 6),
            "note": (f"even a unanimous {n_disc}:0 split of the observed discordant pairs gives "
                     f"p={round(statistics.mcnemar_exact(n_disc, 0), 4)}; this run cannot detect "
                     f"any paired difference of this size at alpha=0.05")}


def load_arm(arm: str, cases: list[dict]) -> dict[str, dict]:
    """走与 runner.py 相同的抽取+打分路径，返回 {case_id: 逐题记录}。"""
    outputs = runner.load_outputs(RESULTS / f"outputs_ext30_{arm}.json")
    preds = runner._to_predictions(outputs)
    rep = runner.workflow_accuracy.compute(preds, cases)
    rec: dict[str, dict] = {}
    for d in rep["details"]:
        rec[d["id"]] = {"scope": "in", "status": d["status"], "ok": bool(d["ok"]),
                        "predicted": d["predicted"]}
    for d in rep["out_of_scope"]["details"]:
        rec[d["id"]] = {"scope": "out", "status": d["status"], "ok": bool(d["ok"]),
                        "predicted": d["predicted"]}
    # reference_coverage 的逐题命中直接取已落盘 report，避免二次实现同一指标
    scored = json.loads((RESULTS / f"report_ext30_{arm}.json").read_text(encoding="utf-8"))
    ref = next(x for x in scored["details"] if x["metric"] == "reference_coverage")["details"]
    for d in ref:
        if d["id"] in rec:
            rec[d["id"]]["ref_expected"] = len(d["expected_sources"])
            rec[d["id"]]["ref_found"] = len(d["sources_found"])
            rec[d["id"]]["ref_any"] = bool(d["has_any_reference"])
    rec["_raw"] = outputs  # type: ignore[assignment]
    return rec


def variant(both: dict[str, dict], ids: list[str], mode: str) -> dict:
    """在给定题集与口径下，算两臂命中数、Wilson CI、配对 b/c 与精确 McNemar。"""

    def hit(arm: str, cid: str) -> bool:
        r = both[arm][cid]
        if r["ok"]:
            return True
        if mode == "lenient" and r["scope"] == "in":
            expected = both["_expected"][cid]
            return names_expected_id(both[arm]["_raw"][cid], expected)  # type: ignore[arg-type]
        return False

    s_ok = [cid for cid in ids if hit("skill", cid)]
    t_ok = [cid for cid in ids if hit("noskill", cid)]
    b = len([cid for cid in ids if hit("skill", cid) and not hit("noskill", cid)])
    c = len([cid for cid in ids if hit("noskill", cid) and not hit("skill", cid)])
    n = len(ids)
    return {
        "mode": mode,
        "n": n,
        "skill_correct": len(s_ok),
        "noskill_correct": len(t_ok),
        "skill_rate": round(len(s_ok) / n, 4) if n else None,
        "noskill_rate": round(len(t_ok) / n, 4) if n else None,
        "delta_skill_minus_noskill_pt": round(100.0 * (len(s_ok) - len(t_ok)) / n, 2) if n else None,
        "skill_wilson_95": [round(v, 4) for v in statistics.wilson_interval(len(s_ok), n)] if n else None,
        "noskill_wilson_95": [round(v, 4) for v in statistics.wilson_interval(len(t_ok), n)] if n else None,
        "discordant": {"skill_only": b, "noskill_only": c},
        "mcnemar_exact_two_sided_p": statistics.mcnemar_exact(b, c),
        "paired_resolution": min_split_for_significance(b + c),
    }


def analyse() -> dict:
    cases = json.loads(BENCHMARKS.read_text(encoding="utf-8"))
    expected = {c["id"]: c["expected_pipeline_id"] for c in cases}
    both: dict = {"_expected": expected}
    for arm in ARMS:
        both[arm] = load_arm(arm, cases)

    in_scope = [cid for cid, e in expected.items() if e is not None]
    out_scope = sorted(cid for cid, e in expected.items() if e is None)
    strict = [cid for cid in in_scope
              if both["skill"][cid]["status"] != "unparsed"
              and both["noskill"][cid]["status"] != "unparsed"]

    unparsed = {arm: [cid for cid in in_scope if both[arm][cid]["status"] == "unparsed"]
                for arm in ARMS}
    audit = {
        arm: {cid: {
            "status": both[arm][cid]["status"],
            "predicted": both[arm][cid]["predicted"],
            "expected": expected[cid],
            "text_names_expected_id": names_expected_id(both[arm]["_raw"][cid], expected[cid]),
        } for cid in ids}
        for arm, ids in unparsed.items()
    }

    ref_ids = [cid for cid in in_scope
               if both["skill"][cid].get("ref_expected") and both["noskill"][cid].get("ref_expected")]

    def ref_variant() -> dict:
        s = [cid for cid in ref_ids if both["skill"][cid]["ref_any"]]
        t = [cid for cid in ref_ids if both["noskill"][cid]["ref_any"]]
        b = len([cid for cid in ref_ids if both["skill"][cid]["ref_any"] and not both["noskill"][cid]["ref_any"]])
        c = len([cid for cid in ref_ids if both["noskill"][cid]["ref_any"] and not both["skill"][cid]["ref_any"]])
        n = len(ref_ids)
        return {
            "n_cases_with_expected_sources": n,
            "skill_cases_with_any_hit": len(s), "noskill_cases_with_any_hit": len(t),
            "skill_wilson_95": [round(v, 4) for v in statistics.wilson_interval(len(s), n)],
            "noskill_wilson_95": [round(v, 4) for v in statistics.wilson_interval(len(t), n)],
            "discordant": {"skill_only": b, "noskill_only": c},
            "mcnemar_exact_two_sided_p": statistics.mcnemar_exact(b, c),
            "paired_resolution": min_split_for_significance(b + c),
            "note": ("case-level any-source hit; the runner aggregate 18/28 vs 17/28 averages "
                     "source-level recall inside cases and is not paired"),
        }

    return {
        "protocol": {
            "cases_file": str(BENCHMARKS),
            "n_cases": len(cases),
            "in_scope_cases": len(in_scope),
            "out_of_scope_cases": out_scope,
            "scoring_path": ("runner.load_outputs -> runner._to_predictions -> "
                             "workflow_accuracy.compute; reference coverage read back from "
                             "the committed per-case report details"),
            "modes": {
                "strict_intersection": "only in-scope cases the extractor resolved in both arms",
                "all_in_scope": "every in-scope case; unresolved counts as incorrect",
                "lenient": "all in-scope, plus credit when the expected pipeline id (or its alias) "
                           "appears as a standalone token anywhere in the answer text",
            },
        },
        "pipeline_selection": {
            "as_runner_prints_it": {
                "skill": {"correct": 19, "denominator": 26},
                "noskill": {"correct": 21, "denominator": 26},
                "why_this_is_not_the_paired_test": (
                    "the two 26-case denominators are not the same 26 cases: the extractor "
                    "resolved a different subset in each arm"),
            },
            "strict_intersection": variant(both, strict, "strict"),
            "all_in_scope": variant(both, in_scope, "strict"),
            "lenient": variant(both, in_scope, "lenient"),
        },
        "extractor_audit": {
            "unparsed_in_scope": audit,
            "unparsed_counts": {arm: len(ids) for arm, ids in unparsed.items()},
            "reading": (
                "unparsed means the extractor could not pull a pipeline id out of the answer, "
                "not that generation failed; see text_names_expected_id for how many of those "
                "answers in fact name the expected pipeline"),
        },
        "out_of_scope_abstention": {
            arm: {cid: both[arm][cid]["status"] for cid in out_scope} for arm in ARMS
        },
        "reference_coverage": ref_variant(),
        "independent_two_sample_mde": {
            "n_per_arm": len(in_scope),
            "at_p0.5_alpha0.05_power0.80": round(
                statistics.minimum_detectable_difference(len(in_scope)), 4),
            "caveat": ("unpaired sensitivity floor, kept only as a magnitude reference; the paired "
                       "design's resolution is pipeline_selection.*.paired_resolution"),
        },
    }


if __name__ == "__main__":
    result = analyse()
    out_path = RESULTS / "report_ext30_stats.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    ps = result["pipeline_selection"]
    for key in ("strict_intersection", "all_in_scope", "lenient"):
        v = ps[key]
        print(f"{key:20s} n={v['n']:2d} skill={v['skill_correct']:2d} noskill={v['noskill_correct']:2d} "
              f"b/c={v['discordant']['skill_only']}/{v['discordant']['noskill_only']} "
              f"p={v['mcnemar_exact_two_sided_p']:.4f} min_split={v['paired_resolution']['minimum_split']}")
    print("wrote", out_path)
