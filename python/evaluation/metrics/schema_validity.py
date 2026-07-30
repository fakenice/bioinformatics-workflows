"""
Schema Validity — JSON Schema 合规性
检查 Skill 输出的 JSON（若为结构化输出）是否与 FlowSeq PipelineDefinition schema 一致。
纯 JSON 结构校验，零外部依赖。
"""
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS = ROOT / "benchmarks" / "test_cases.json"

# PipelineDefinition 最小合法结构
REQUIRED_TOP_KEYS = {"id", "name", "steps"}
REQUIRED_STEP_KEYS = {"tool", "command"}


def _extract_json_candidates(text: str) -> list[tuple[str, dict]]:
    """从输出文本中提取所有 JSON 候选块"""
    candidates: list[tuple[str, dict]] = []
    # 匹配 ```json / ```JSON 代码块
    for m in re.finditer(r'```(?:json|JSON)?\s*\n(.*?)```', text, re.DOTALL):
        try:
            obj = json.loads(m.group(1).strip())
            if isinstance(obj, dict):
                candidates.append(("code_block", obj))
        except json.JSONDecodeError:
            continue
    # 匹配裸 JSON 对象（用括号平衡算法提取）
    if not candidates:
        m = re.search(r'\{(?:"id"\s*:\s*"[^"]+")', text)
        if m:
            start = m.start()
            # 括号平衡扫描
            depth = 0
            end = start
            for i, ch in enumerate(text[start:], start):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            try:
                obj = json.loads(text[start:end])
                if isinstance(obj, dict) and "id" in obj:
                    candidates.append(("bare_json", obj))
            except json.JSONDecodeError:
                pass
    return candidates


def _validate_pipeline(obj: dict) -> list[str]:
    """验证单个 pipeline 对象，返回错误列表"""
    errors: list[str] = []

    # 顶层必需字段
    missing_top = REQUIRED_TOP_KEYS - set(obj.keys())
    if missing_top:
        errors.append(f"missing top-level keys: {missing_top}")

    # steps 必须是非空列表
    steps = obj.get("steps")
    if not isinstance(steps, list) or len(steps) == 0:
        errors.append("steps must be a non-empty array")
    else:
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"step[{i}] is not an object")
                continue
            missing_step = REQUIRED_STEP_KEYS - set(step.keys())
            if missing_step:
                errors.append(f"step[{i}] missing keys: {missing_step}")
            # tool 和 command 必须是非空字符串
            for k in REQUIRED_STEP_KEYS:
                if k in step:
                    if not isinstance(step[k], str) or not step[k].strip():
                        errors.append(f"step[{i}].{k} must be a non-empty string")

    return errors


def compute(outputs: dict[str, str]) -> dict[str, Any]:
    """
    Args:
        outputs: {case_id: Skill 输出文本}
    Returns:
        Schema 合规性报告
    """
    cases = json.loads(BENCHMARKS.read_text(encoding="utf-8"))
    total_json_outputs = 0
    valid_jsons = 0
    per_case: list[dict] = []

    for c in cases:
        cid = c["id"]
        text = outputs.get(cid, "")
        candidates = _extract_json_candidates(text)

        if not candidates:
            per_case.append({
                "id": cid,
                "has_json_output": False,
                "valid": None,
                "errors": ["no JSON found in output"],
            })
            continue

        case_valid = True
        case_errors: list[str] = []
        for src, obj in candidates:
            total_json_outputs += 1
            errs = _validate_pipeline(obj)
            if errs:
                case_valid = False
                case_errors.extend([f"[{src}] {e}" for e in errs])
            else:
                valid_jsons += 1

        per_case.append({
            "id": cid,
            "has_json_output": True,
            "valid": case_valid,
            "errors": case_errors,
        })

    score = valid_jsons / total_json_outputs if total_json_outputs > 0 else 1.0

    return {
        "metric": "schema_validity",
        "score": round(score, 4),
        "total_json_outputs": total_json_outputs,
        "valid_jsons": valid_jsons,
        "details": per_case,
    }
