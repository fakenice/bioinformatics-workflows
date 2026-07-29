"""
Workflow Selection Accuracy
Evaluates whether the Skill correctly matches a user scenario to the right pipeline.
Compares FlowSeq-guided selection vs bare LLM selection.
"""
import json
from pathlib import Path
from typing import Dict, Any


class WorkflowAccuracyEvaluator:
    def __init__(self, test_cases_path: str):
        with open(test_cases_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.test_cases = data["test_cases"]
        self.total = len(self.test_cases)

    def evaluate(
        self,
        llm_predictions: Dict[str, str],
        skill_predictions: Dict[str, str],
    ) -> Dict[str, Any]:
        """Compare predictions against ground truth."""
        llm_correct = 0
        skill_correct = 0
        llm_details = []
        skill_details = []

        for tc in self.test_cases:
            tid = tc["id"]
            expected = tc["expected_pipeline"]

            llm_pred = llm_predictions.get(tid, "")
            skill_pred = skill_predictions.get(tid, "")

            llm_ok = llm_pred == expected
            skill_ok = skill_pred == expected

            if llm_ok:
                llm_correct += 1
            if skill_ok:
                skill_correct += 1

            llm_details.append({
                "id": tid,
                "expected": expected,
                "predicted": llm_pred,
                "correct": llm_ok,
            })
            skill_details.append({
                "id": tid,
                "expected": expected,
                "predicted": skill_pred,
                "correct": skill_ok,
            })

        llm_accuracy = llm_correct / self.total
        skill_accuracy = skill_correct / self.total
        improvement = skill_accuracy - llm_accuracy

        return {
            "metric": "Workflow Selection Accuracy",
            "total_cases": self.total,
            "bare_llm": {
                "correct": llm_correct,
                "accuracy": round(llm_accuracy, 4),
            },
            "flowseq_skill": {
                "correct": skill_correct,
                "accuracy": round(skill_accuracy, 4),
            },
            "improvement": round(improvement, 4),
            "improvement_pct": f"{improvement * 100:.1f}%",
            "llm_details": llm_details,
            "skill_details": skill_details,
        }


if __name__ == "__main__":
    evaluator = WorkflowAccuracyEvaluator(
        str(Path(__file__).parent.parent / "benchmarks" / "test_cases.json")
    )
    print(f"Loaded {evaluator.total} test cases for Workflow Selection Accuracy evaluation.")
