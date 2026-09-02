"""
Reference Coverage — 引用完整性
检查 Skill 输出是否附上了准确的参考来源（expected_sources 命中率）。
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
    total_expected = 0
    total_found = 0
    per_case: list[dict] = []

    for c in cases:
        cid = c["id"]
        text = outputs.get(cid, "")
        expected_sources = set(c.get("expected_sources", []))

        # 检查 expected_sources 是否都被引用到（准确参考来源命中）
        sources_found = []
        sources_missed = []
        for src in expected_sources:
            if re.search(re.escape(src), text, re.IGNORECASE):
                sources_found.append(src)
            else:
                sources_missed.append(src)

        # 无 expected_sources 的 case：检查是否附了任意参考来源（URL/DOI/Markdown link）
        has_any_ref = bool(
            re.search(r'10\.\d{4,}/[^\s"\'<>]+', text)  # DOI
            or re.search(r'https?://[^\s"\'<>\[\]()]+', text)  # URL
            or re.search(r'\[[^\]]+\]\([^)]+\)', text)  # Markdown link
        )

        if expected_sources:
            total_expected += len(expected_sources)
            total_found += len(sources_found)

        per_case.append({
            "id": cid,
            "expected_sources": list(expected_sources),
            "sources_found": sources_found,
            "sources_missed": sources_missed,
            "has_any_reference": has_any_ref,
        })

    coverage = total_found / total_expected if total_expected > 0 else 0.0

    return {
        "metric": "reference_coverage",
        "score": round(coverage, 4),
        "total_expected_sources": total_expected,
        "sources_found": total_found,
        "details": per_case,
    }
