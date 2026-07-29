"""
Hallucination Reduction
Evaluates whether the Skill suppresses fabricated tool versions, Docker images,
and parameter names that do not exist in reality.

Bare LLMs frequently hallucinate tool versions (e.g., "GATK 5.0") or Docker tags
(e.g., "biocontainers/gatk:latest") that are not real. FlowSeq constrains output
to a verified knowledge base.
"""
import json
from pathlib import Path
from typing import Dict, Any, List


class HallucinationEvaluator:
    """Checks predictions for hallucinated tool info against ground truth."""

    def __init__(self, test_cases_path: str):
        with open(test_cases_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.test_cases = data["test_cases"]

    @staticmethod
    def _check_field_hallucination(
        predicted_values: List[str],
        expected_values: List[str],
    ) -> int:
        """Count how many predicted values do NOT appear in expected."""
        if not expected_values:
            return 0  # No ground truth → skip this field
        hallucinated = 0
        for pred in predicted_values:
            if pred not in expected_values and pred != "":
                hallucinated += 1
        return hallucinated

    def evaluate(
        self,
        llm_predictions: Dict[str, Dict[str, List[str]]],
        skill_predictions: Dict[str, Dict[str, List[str]]],
    ) -> Dict[str, Any]:
        """
        Each prediction dict maps case_id -> {tools, versions, docker, params}.
        Count hallucinated values per field.
        """
        fields = ["tools", "versions", "docker", "params", "qc"]
        results = {}

        for field in fields:
            llm_total = 0
            llm_hallucinated = 0
            skill_total = 0
            skill_hallucinated = 0

            for tc in self.test_cases:
                tid = tc["id"]
                expected_key = {
                    "tools": "expected_tools",
                    "versions": "expected_versions",
                    "docker": "expected_docker",
                    "params": "expected_params",
                    "qc": "expected_qc",
                }.get(field, "")

                if isinstance(expected := tc.get(expected_key, {}), dict):
                    expected_list = list(expected.values()) if field == "versions" else list(expected.keys())
                elif isinstance(expected, list):
                    expected_list = expected
                else:
                    expected_list = []

                llm_pred = llm_predictions.get(tid, {}).get(field, [])
                skill_pred = skill_predictions.get(tid, {}).get(field, [])

                llm_total += len(llm_pred)
                skill_total += len(skill_pred)

                llm_hallucinated += self._check_field_hallucination(llm_pred, expected_list)
                skill_hallucinated += self._check_field_hallucination(skill_pred, expected_list)

            llm_rate = llm_hallucinated / max(llm_total, 1)
            skill_rate = skill_hallucinated / max(skill_total, 1)
            reduction = llm_rate - skill_rate

            results[field] = {
                "bare_llm": {
                    "total_predictions": llm_total,
                    "hallucinated": llm_hallucinated,
                    "hallucination_rate": round(llm_rate, 4),
                },
                "flowseq_skill": {
                    "total_predictions": skill_total,
                    "hallucinated": skill_hallucinated,
                    "hallucination_rate": round(skill_rate, 4),
                },
                "reduction": round(reduction, 4),
                "reduction_pct": f"{reduction * 100:.1f}%",
            }

        # Aggregate
        llm_agg = sum(r["bare_llm"]["total_predictions"] for r in results.values())
        llm_hall = sum(r["bare_llm"]["hallucinated"] for r in results.values())
        skill_agg = sum(r["flowseq_skill"]["total_predictions"] for r in results.values())
        skill_hall = sum(r["flowseq_skill"]["hallucinated"] for r in results.values())

        return {
            "metric": "Hallucination Reduction",
            "by_field": results,
            "aggregate": {
                "bare_llm": {
                    "total_predictions": llm_agg,
                    "hallucinated": llm_hall,
                    "hallucination_rate": round(llm_hall / max(llm_agg, 1), 4),
                },
                "flowseq_skill": {
                    "total_predictions": skill_agg,
                    "hallucinated": skill_hall,
                    "hallucination_rate": round(skill_hall / max(skill_agg, 1), 4),
                },
                "reduction": round((llm_hall / max(llm_agg, 1) - skill_hall / max(skill_agg, 1)), 4),
            },
        }


if __name__ == "__main__":
    evaluator = HallucinationEvaluator(
        str(Path(__file__).parent.parent / "benchmarks" / "test_cases.json")
    )
    print(f"Hallucination evaluator ready for {len(evaluator.test_cases)} test cases.")
