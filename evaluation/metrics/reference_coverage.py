"""
Reference Coverage
Evaluates whether outputs include citations to verifiable sources (official docs,
peer-reviewed papers, community pipelines). Bare LLMs rarely provide references;
FlowSeq includes references in every pipeline definition.
"""
import json
from pathlib import Path
from typing import Dict, Any, List


class ReferenceCoverageEvaluator:
    def __init__(self, test_cases_path: str):
        with open(test_cases_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.test_cases = data["test_cases"]

    def evaluate(
        self,
        llm_references: Dict[str, List[str]],
        skill_references: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Count references per case."""
        llm_counts = []
        skill_counts = []

        for tc in self.test_cases:
            tid = tc["id"]
            llm_refs = llm_references.get(tid, [])
            skill_refs = skill_references.get(tid, [])

            llm_counts.append(len(llm_refs))
            skill_counts.append(len(skill_refs))

        llm_avg = sum(llm_counts) / len(llm_counts) if llm_counts else 0
        skill_avg = sum(skill_counts) / len(skill_counts) if skill_counts else 0

        llm_has_ref = sum(1 for c in llm_counts if c > 0) / len(llm_counts)
        skill_has_ref = sum(1 for c in skill_counts if c > 0) / len(skill_counts)

        return {
            "metric": "Reference Coverage",
            "total_cases": len(self.test_cases),
            "bare_llm": {
                "average_refs_per_case": round(llm_avg, 2),
                "cases_with_refs": f"{llm_has_ref * 100:.1f}%",
                "refs_per_case": llm_counts,
            },
            "flowseq_skill": {
                "average_refs_per_case": round(skill_avg, 2),
                "cases_with_refs": f"{skill_has_ref * 100:.1f}%",
                "refs_per_case": skill_counts,
            },
            "improvement": f"+{skill_avg - llm_avg:.1f} refs/case",
        }


if __name__ == "__main__":
    evaluator = ReferenceCoverageEvaluator(
        str(Path(__file__).parent.parent / "benchmarks" / "test_cases.json")
    )
    print(f"Reference coverage evaluator ready for {len(evaluator.test_cases)} cases.")
