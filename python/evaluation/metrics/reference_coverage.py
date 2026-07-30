"""
Reference Coverage — 引用完整性
检查 Skill 输出中每个步骤是否都提供了可追溯的引用来源（URL/DOI/工具文档链接）。
零外部依赖，纯正则检查。
"""
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS = ROOT / "benchmarks" / "test_cases.json"


def compute(outputs: dict[str, str]) -> dict[str, Any]:
    """
    Args:
        outputs: {case_id: Skill 输出文本}
    Returns:
        引用覆盖率报告
    """
    cases = json.loads(BENCHMARKS.read_text(encoding="utf-8"))
    total_steps_identified = 0
    steps_with_refs = 0
    per_case: list[dict] = []

    for c in cases:
        cid = c["id"]
        text = outputs.get(cid, "")
        expected_sources = set(c.get("expected_sources", []))

        # 检测步骤（按标题/编号/Nextflow process 名分割）
        steps = re.split(r'\n(?=#|(?:Step|Process)\s*\d+|process\s+\w+)', text)

        case_ref_count = 0
        case_step_count = len([s for s in steps if s.strip()])

        for step in steps:
            if not step.strip():
                continue
            total_steps_identified += 1
            has_ref = bool(
                re.search(r'10\.\d{4,}/[^\s"\'<>]+', step)  # DOI
                or re.search(r'https?://[^\s"\'<>\[\]()]+', step)  # URL
                or re.search(r'\[[^\]]+\]\([^)]+\)', step)  # Markdown link
            )
            if has_ref:
                steps_with_refs += 1
                case_ref_count += 1

        # 还需检查 expected_sources 是否都被引用到
        sources_found = []
        sources_missed = []
        for src in expected_sources:
            if re.search(re.escape(src), text, re.IGNORECASE):
                sources_found.append(src)
            else:
                sources_missed.append(src)

        per_case.append({
            "id": cid,
            "steps_total": case_step_count,
            "steps_with_refs": case_ref_count,
            "expected_sources": list(expected_sources),
            "sources_found": sources_found,
            "sources_missed": sources_missed,
        })

    coverage = steps_with_refs / total_steps_identified if total_steps_identified > 0 else 0.0

    return {
        "metric": "reference_coverage",
        "score": round(coverage, 4),
        "total_steps": total_steps_identified,
        "steps_with_references": steps_with_refs,
        "details": per_case,
    }
