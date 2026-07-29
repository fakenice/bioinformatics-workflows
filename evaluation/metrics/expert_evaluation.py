"""
Expert Evaluation Framework
Defines the blind review protocol for domain experts to evaluate FlowSeq vs bare LLM.
Outputs a structured scoring rubric and evaluation template.
"""
import json
from pathlib import Path
from typing import Dict, Any


EXPERT_RUBRIC = {
    "pipeline_suitability": {
        "weight": 0.30,
        "question": "推荐的管线是否适合该场景？",
        "scale": {"1": "完全不适合", "2": "部分相关", "3": "基本适合", "4": "很好", "5": "最佳方案"},
    },
    "tool_version_accuracy": {
        "weight": 0.20,
        "question": "推荐的工具版本号是否准确且最新？",
        "scale": {"1": "多数错误", "2": "少数正确", "3": "基本正确", "4": "多数正确", "5": "全部准确"},
    },
    "parameter_appropriateness": {
        "weight": 0.20,
        "question": "参数推荐是否符合领域最佳实践？",
        "scale": {"1": "全部不当", "2": "多数不当", "3": "部分合理", "4": "多数合理", "5": "全部合理"},
    },
    "qc_thresholds": {
        "weight": 0.15,
        "question": "QC 阈值的设置是否合理？",
        "scale": {"1": "全部不合理", "2": "多数不合理", "3": "部分合理", "4": "多数合理", "5": "全部合理"},
    },
    "explainability": {
        "weight": 0.15,
        "question": "输出是否有清晰的解释和溯源？",
        "scale": {"1": "无解释", "2": "模糊", "3": "基本清晰", "4": "较清晰", "5": "非常清晰可溯源"},
    },
}


def generate_evaluation_sheet() -> Dict[str, Any]:
    return {
        "protocol": "Blind Expert Review",
        "version": "1.0.0",
        "evaluators_required": "2-3 domain experts",
        "blinding": "Each evaluator receives anonymized output pairs (System A / System B), randomized per case.",
        "cases_per_evaluator": 10,
        "rubric": EXPERT_RUBRIC,
        "scoring": {
            "per_case": "weighted sum across 5 dimensions (range: 1-5 per dimension)",
            "final": "average across evaluators and cases",
            "interpretation": {
                ">=4.5": "Excellent — production-ready recommendations",
                "3.5-4.4": "Good — usable with minor corrections",
                "2.5-3.4": "Fair — needs significant revision",
                "<2.5": "Poor — not usable",
            },
        },
    }


if __name__ == "__main__":
    rubric = generate_evaluation_sheet()
    print(json.dumps(rubric, ensure_ascii=False, indent=2))
