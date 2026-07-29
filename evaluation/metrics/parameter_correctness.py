"""
Parameter Correctness
Evaluates whether recommended tool parameters match official documentation.
FlowSeq parameters are sourced from verified pipeline JSON files and
nf-core/community best practices, not LLM memorization.
"""
import json
from pathlib import Path
from typing import Dict, Any, List


class ParameterCorrectnessEvaluator:
    def __init__(self, test_cases_path: str):
        with open(test_cases_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.test_cases = data["test_cases"]

    @staticmethod
    def _param_match(predicted: str, expected: str) -> bool:
        """Fuzzy parameter matching allowing minor whitespace differences."""
        if not predicted or not expected:
            return False
        return predicted.strip().lower() == expected.strip().lower()

    def evaluate(
        self,
        llm_predictions: Dict[str, List[Dict[str, str]]],
        skill_predictions: Dict[str, List[Dict[str, str]]],
    ) -> Dict[str, Any]:
        """
        Each prediction is Dict[case_id, List[{tool, param, value}]].
        """
        known_params = {
            # Tool → param → expected value (sourced from pipeline JSONs)
            "GATK": {"version": "4.4+"},
            "STAR": {"--twopassMode": "Basic", "version": "2.7.11"},
            "Salmon": {"version": "1.10"},
            "DESeq2": {"version": "1.44", "design": "~ condition"},
            "Seurat": {"min.cells": "3", "min.features": "200", "version": "5.1"},
            "Cell Ranger": {"version": "8.0"},
            "FastQC": {"version": "0.12.1"},
            "Trim Galore": {"version": "0.6.10", "params": "--fastqc"},
            "PLINK": {"--mind": "0.03", "--geno": "0.02", "--maf": "0.01", "--hwe": "1e-6"},
            "SAIGE": {"version": "1.3+"},
            "REGENIE": {"version": "3.4+"},
            "clusterProfiler": {"version": "4.10"},
            "SingleR": {"version": "2.0"},
            "CellTypist": {"version": "1.0"},
            "Seurat SCTransform": {"vars.to.regress": "percent.mt"},
            "Seurat FindClusters": {"resolution": "0.5"},
            "Seurat RunPCA + RunUMAP": {"dims": "1:30"},
            "PLINK --king": {"--king-cutoff": "0.0884"},
            "PLINK --logistic": {"covar": "PC1-PC5", "ci": "0.95"},
            "VEP": {"version": "110+"},
            "Bismark": {},
            "MACS2": {},
            "QIIME2": {},
            "DADA2": {},
        }

        llm_correct = 0
        llm_total = 0
        skill_correct = 0
        skill_total = 0

        for tc in self.test_cases:
            tid = tc["id"]
            llm_tool_params = llm_predictions.get(tid, [])
            skill_tool_params = skill_predictions.get(tid, [])

            for entry in llm_tool_params:
                tool = entry.get("tool", "")
                param = entry.get("param", "")
                value = entry.get("value", "")
                expected = (known_params.get(tool, {}) or {}).get(param, "")
                llm_total += 1
                if expected and self._param_match(value, expected):
                    llm_correct += 1

            for entry in skill_tool_params:
                tool = entry.get("tool", "")
                param = entry.get("param", "")
                value = entry.get("value", "")
                expected = (known_params.get(tool, {}) or {}).get(param, "")
                skill_total += 1
                if expected and self._param_match(value, expected):
                    skill_correct += 1

        llm_rate = llm_correct / max(llm_total, 1)
        skill_rate = skill_correct / max(skill_total, 1)

        return {
            "metric": "Parameter Correctness",
            "bare_llm": {
                "total_checked": llm_total,
                "correct": llm_correct,
                "accuracy": round(llm_rate, 4),
            },
            "flowseq_skill": {
                "total_checked": skill_total,
                "correct": skill_correct,
                "accuracy": round(skill_rate, 4),
            },
            "improvement": round(skill_rate - llm_rate, 4),
            "improvement_pct": f"{(skill_rate - llm_rate) * 100:.1f}%",
        }


if __name__ == "__main__":
    evaluator = ParameterCorrectnessEvaluator(
        str(Path(__file__).parent.parent / "benchmarks" / "test_cases.json")
    )
    print(f"Parameter correctness evaluator ready for {len(evaluator.test_cases)} cases.")
