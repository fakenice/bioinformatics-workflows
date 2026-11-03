"""Regenerate the documentation copy of the test cases from the scored copy.

The repository used to ship two `test_cases.json` files with the same ids but
different scenarios and expected pipelines (17 of 20 labels disagreed). The
runner scores `python/evaluation/benchmarks/test_cases.json`; this script makes
`evaluation/benchmarks/test_cases.json` a generated mirror so the README and the
scored run cannot drift apart.

Usage (from the repo root):
    python evaluation/metrics/sync_doc_cases.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "python" / "evaluation" / "benchmarks" / "test_cases.json"
DST = ROOT / "evaluation" / "benchmarks" / "test_cases.json"


def main() -> int:
    scored = json.loads(SRC.read_text(encoding="utf-8"))
    docs = []
    for c in scored:
        docs.append({
            "id": c["id"],
            "scenario": c["query"],
            "expected_pipeline": c["expected_pipeline_id"],
            "expected_tools": c.get("must_include_tools", []),
            "expected_params": c.get("must_include_params", []),
            "expected_traps": c.get("must_flag_traps", []),
            "expected_validations": c.get("must_apply_validations", []),
            "category": c.get("category"),
            "difficulty": c.get("difficulty"),
        })

    payload = {
        "meta": {
            "version": "1.1.0",
            "generated": "2026-11-02",
            "description": (
                "Generated mirror of python/evaluation/benchmarks/test_cases.json, "
                "which is the file the runner scores. Do not edit by hand; run "
                "evaluation/metrics/sync_doc_cases.py."
            ),
            "source": "python/evaluation/benchmarks/test_cases.json",
            "total_pipelines": 14,
            "total_cases": len(docs),
        },
        "test_cases": docs,
    }
    DST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {DST} ({len(docs)} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
