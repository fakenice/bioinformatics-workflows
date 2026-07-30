"""
Parameter Correctness — 参数合理性检查
对每个 test case，检查 Skill 输出的参数是否在知识库定义的合理范围内。
纯规则匹配，零成本。
"""
import json
import re
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PIPELINES_DIR = SKILL_ROOT / "pipelines"

# 预定义的参数阈值规则（来自知识库）
_PARAM_RULES: dict[str, dict[str, Any]] = {
    "MAF":       {"min": 0.0, "max": 0.5, "unit": "fraction"},
    "HWE":       {"min": 1e-12, "max": 1.0, "unit": "p-value"},
    "minDP":     {"min": 1, "max": 1000, "unit": "integer", "allow_null": True},
    "minGQ":     {"min": 0, "max": 99, "unit": "integer"},
    "threads":   {"min": 1, "max": 256, "unit": "integer"},
    "resolution":{"min": 0.1, "max": 5.0, "unit": "float"},
    "nCount_RNA": {"min": 0, "max": 100000, "unit": "integer", "allow_null": True},
    "FRiP":      {"min": 0.0, "max": 1.0, "unit": "fraction"},
    "IDR":       {"min": 0.0, "max": 1.0, "unit": "fraction"},
    "F-statistic": {"min": 1.0, "max": 100000.0, "unit": "float"},
    "log2FC":    {"min": -20.0, "max": 20.0, "unit": "float"},
    "q-value":   {"min": 0.0, "max": 1.0, "unit": "p-value"},
    "min-coverage": {"min": 1, "max": 10000, "unit": "integer"},
}


def _extract_numeric_params(text: str) -> dict[str, list[float]]:
    """从输出文本中提取参数名和数值列表"""
    found: dict[str, list[float]] = {}
    for param in _PARAM_RULES:
        p = re.findall(
            rf'{re.escape(param)}\s*[>:=\s]+\s*([\d.]+(?:\s*[-–]\s*[\d.]+)?)',
            text, re.IGNORECASE,
        )
        for val_str in p:
            nums = re.findall(r'[\d.]+', val_str)
            for n in nums:
                v = float(n)
                # 百分比修正：若紧跟 %，除以 100
                full_match = re.search(
                    rf'{re.escape(param)}\s*[>:=\s]+\s*{re.escape(val_str)}\s*%',
                    text, re.IGNORECASE,
                )
                if full_match:
                    v = v / 100.0
                found.setdefault(param, []).append(v)
    return found


def compute(outputs: dict[str, str]) -> dict[str, Any]:
    """
    Args:
        outputs: {case_id: Skill 输出文本}
    Returns:
        参数合理性报告
    """
    total_params = 0
    invalid_params = 0
    per_case: list[dict] = []

    for cid, text in outputs.items():
        extracted = _extract_numeric_params(text)
        violations: list[dict] = []

        for param, values in extracted.items():
            rules = _PARAM_RULES.get(param)
            if not rules:
                continue
            total_params += len(values)
            for v in values:
                ok = True
                reason = ""
                if v < rules.get("min", float("-inf")):
                    ok = False
                    reason = f"{param}={v} < min {rules['min']}"
                elif v > rules.get("max", float("inf")):
                    ok = False
                    reason = f"{param}={v} > max {rules['max']}"
                if not ok:
                    invalid_params += 1
                    violations.append({"param": param, "value": v, "reason": reason})

        per_case.append({
            "id": cid,
            "params_extracted": extracted,
            "violations": violations,
            "param_count": sum(len(v) for v in extracted.values()),
            "violation_count": len(violations),
        })

    correctness = 1.0 - (invalid_params / total_params) if total_params > 0 else 1.0

    return {
        "metric": "parameter_correctness",
        "score": round(correctness, 4),
        "total_params_checked": total_params,
        "invalid_params": invalid_params,
        "details": per_case,
    }
