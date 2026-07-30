"""
Pipeline Selection Accuracy — 管线匹配准确率
纯规则匹配：将 Skill 输出的 pipeline_id 与 test_cases 的 expected_pipeline_id 比对。
不需要人工标注，不需要 LLM 判分。
"""
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS = ROOT / "benchmarks" / "test_cases.json"


def compute(predictions: dict[str, str | None]) -> dict[str, Any]:
    """
    Args:
        predictions: {case_id: predicted_pipeline_id | None}
                     若 Skill 回答"I don't know" → None
                     若 Skill 未覆盖 → "__uncovered__"
    Returns:
        指标 report dict
    """
    cases = json.loads(BENCHMARKS.read_text(encoding="utf-8"))
    total = len(cases)
    correct = 0
    details: list[dict] = []

    for c in cases:
        cid = c["id"]
        expected = c["expected_pipeline_id"]
        predicted = predictions.get(cid)

        ok = predicted == expected
        if ok:
            correct += 1

        details.append({
            "id": cid,
            "query": c["query"],
            "expected": expected,
            "predicted": predicted,
            "ok": ok,
        })

    accuracy = correct / total if total > 0 else 0.0
    return {
        "metric": "pipeline_selection_accuracy",
        "score": round(accuracy, 4),
        "total": total,
        "correct": correct,
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
        v["accuracy"] = round(v["correct"] / v["total"], 4) if v["total"] else 0.0
    return by_cat
