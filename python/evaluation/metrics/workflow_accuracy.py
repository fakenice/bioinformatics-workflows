"""
Pipeline Selection Accuracy — 管线匹配准确率
纯规则匹配：将 Skill 输出的 pipeline_id 与 test_cases 的 expected_pipeline_id 比对。
不需要人工标注，不需要 LLM 判分。

语义（v1.1.0 起）：
- 只有 `expected_pipeline_id` 非空的用例进入管线准确率分母；
- 缺少预测（未解析）与显式拒答（`__uncovered__`）是两种不同的失败，二者都不算对；
- 预期为空的跨域/边界题单独统计“拒答准确率”，不再混入管线分母；
- 0 个管线用例时返回 score=None，由 runner 从 overall 中剔除。
"""
import json
from pathlib import Path
from typing import Any

from .statistics import wilson_interval

ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS = ROOT / "benchmarks" / "test_cases.json"

ABSTAIN = "__uncovered__"
_MISSING = object()


def compute(predictions: dict[str, str | None], cases: list[dict] | None = None) -> dict[str, Any]:
    """
    Args:
        predictions: {case_id: predicted_pipeline_id | None | "__uncovered__"}
                     缺失 key 表示“解析失败”，不等于拒答。
        cases: 可选，默认读取 benchmarks/test_cases.json；测试可注入。
    Returns:
        指标 report dict；score 在无管线用例时为 None。
    """
    if cases is None:
        cases = json.loads(BENCHMARKS.read_text(encoding="utf-8"))

    total = 0
    correct = 0
    unparsed = 0
    abstained = 0
    details: list[dict] = []

    out_total = 0
    out_correct = 0
    out_answered = 0
    out_unparsed = 0
    out_details: list[dict] = []

    for c in cases:
        cid = c["id"]
        expected = c["expected_pipeline_id"]
        raw = predictions.get(cid, _MISSING)

        if expected is None:
            out_total += 1
            if raw is _MISSING:
                status = "unparsed"
                out_unparsed += 1
            elif raw is None or raw == ABSTAIN:
                status = "abstained"
                out_correct += 1
            else:
                status = "answered"
                out_answered += 1
            out_details.append({
                "id": cid,
                "query": c["query"],
                "expected": None,
                "predicted": None if status in ("abstained", "unparsed") else raw,
                "ok": status == "abstained",
                "status": status,
            })
            continue

        total += 1
        if raw is _MISSING:
            status = "unparsed"
            predicted = None
            unparsed += 1
        elif raw is None or raw == ABSTAIN:
            status = "abstained"
            predicted = None
            abstained += 1
        elif raw == expected:
            status = "correct"
            predicted = raw
            correct += 1
        else:
            status = "wrong"
            predicted = raw

        details.append({
            "id": cid,
            "query": c["query"],
            "expected": expected,
            "predicted": predicted,
            "ok": status == "correct",
            "status": status,
        })

    accuracy = correct / total if total > 0 else None
    out_accuracy = out_correct / out_total if out_total > 0 else None

    return {
        "metric": "pipeline_selection_accuracy",
        "score": round(accuracy, 4) if accuracy is not None else None,
        "total": total,
        "correct": correct,
        "unparsed": unparsed,
        "abstained": abstained,
        "wilson_95": list(wilson_interval(correct, total)) if total else None,
        "out_of_scope": {
            "total": out_total,
            "correct": out_correct,
            "answered": out_answered,
            "unparsed": out_unparsed,
            "score": round(out_accuracy, 4) if out_accuracy is not None else None,
            "details": out_details,
        },
        "by_category": _by_category(details, cases),
        "details": details,
    }


def _by_category(details: list[dict], cases: list[dict]) -> dict[str, dict]:
    cat_lookup = {c["id"]: c["category"] for c in cases}
    by_cat: dict[str, dict] = {}
    for d in details:
        cat = cat_lookup[d["id"]]
        entry = by_cat.setdefault(cat, {"total": 0, "correct": 0})
        entry["total"] += 1
        if d["ok"]:
            entry["correct"] += 1
    for v in by_cat.values():
        v["accuracy"] = round(v["correct"] / v["total"], 4) if v["total"] else None
    return by_cat
