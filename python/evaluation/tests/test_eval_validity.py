"""Regression tests for evaluation validity.

The v1.0.0 evaluation counted a missing prediction as a correct abstention when the
expected pipeline was None, and averaged zero-denominator metrics (0/0 = 100%) into
the overall score. These tests pin the corrected semantics so the published numbers
cannot silently regress.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from evaluation.metrics import statistics as stats
from evaluation.metrics import workflow_accuracy as wa
from evaluation import runner

ROOT = Path(__file__).resolve().parents[2]
PY_CASES = ROOT / "evaluation" / "benchmarks" / "test_cases.json"
DOC_CASES = ROOT.parent / "evaluation" / "benchmarks" / "test_cases.json"

CASES = [
    {"id": "P1", "expected_pipeline_id": "pipeline-a", "query": "q1", "category": "dna"},
    {"id": "P2", "expected_pipeline_id": "pipeline-b", "query": "q2", "category": "rna"},
    {"id": "O1", "expected_pipeline_id": None, "query": "out of scope", "category": "edge"},
]


class WorkflowAccuracySemantics(unittest.TestCase):
    def test_out_of_scope_case_is_not_in_pipeline_denominator(self):
        result = wa.compute({"P1": "pipeline-a", "O1": wa.ABSTAIN}, cases=CASES)
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["correct"], 1)
        self.assertEqual(result["score"], 0.5)
        self.assertEqual(result["out_of_scope"]["total"], 1)
        self.assertEqual(result["out_of_scope"]["correct"], 1)

    def test_missing_prediction_is_unparsed_not_a_correct_abstention(self):
        result = wa.compute({}, cases=CASES)
        self.assertEqual(result["correct"], 0)
        self.assertEqual(result["unparsed"], 2)
        self.assertEqual(result["out_of_scope"]["unparsed"], 1)
        self.assertEqual(result["out_of_scope"]["correct"], 0)
        self.assertEqual(result["out_of_scope"]["score"], 0.0)

    def test_explicit_abstention_on_pipeline_case_is_incorrect(self):
        result = wa.compute({"P1": wa.ABSTAIN, "P2": "pipeline-b"}, cases=CASES)
        self.assertEqual(result["correct"], 1)
        self.assertEqual(result["abstained"], 1)
        self.assertEqual(result["score"], 0.5)

    def test_answered_out_of_scope_case_is_incorrect(self):
        result = wa.compute({"P1": "pipeline-a", "P2": "pipeline-b", "O1": "pipeline-a"}, cases=CASES)
        self.assertEqual(result["out_of_scope"]["correct"], 0)
        self.assertEqual(result["out_of_scope"]["answered"], 1)
        self.assertEqual(result["out_of_scope"]["score"], 0.0)


class OverallAggregation(unittest.TestCase):
    def test_zero_denominator_metric_is_excluded(self):
        results = [
            {"metric": "pipeline_selection_accuracy", "score": 0.9, "total": 20},
            {"metric": "schema_validity", "score": None, "total_json_outputs": 0},
        ]
        agg = runner.aggregate_scores(results)
        self.assertEqual(agg["overall_score"], 0.9)
        self.assertEqual(agg["excluded_metrics"], ["schema_validity"])
        self.assertEqual(agg["valid_metric_count"], 1)

    def test_all_degenerate_metrics_yield_no_overall_score(self):
        results = [{"metric": "schema_validity", "score": None, "total_json_outputs": 0}]
        agg = runner.aggregate_scores(results)
        self.assertIsNone(agg["overall_score"])
        self.assertEqual(agg["excluded_metrics"], ["schema_validity"])


class Statistics(unittest.TestCase):
    def test_wilson_interval_for_17_of_20(self):
        lo, hi = stats.wilson_interval(17, 20)
        self.assertAlmostEqual(lo, 0.640, places=3)
        self.assertAlmostEqual(hi, 0.948, places=3)

    def test_mcnemar_exact_with_one_discordant_pair_is_not_significant(self):
        self.assertAlmostEqual(stats.mcnemar_exact(1, 0), 1.0, places=9)

    def test_mcnemar_exact_matches_binomial_tail(self):
        # Two-sided exact p for 10 vs 0 discordant pairs = 2 * 0.5**10.
        self.assertAlmostEqual(stats.mcnemar_exact(10, 0), 2 * 0.5**10, places=9)

    def test_minimum_detectable_difference_shrinks_with_more_cases(self):
        small = stats.minimum_detectable_difference(20, p=0.85)
        large = stats.minimum_detectable_difference(80, p=0.85)
        self.assertGreater(small, large)
        self.assertGreater(small, 0.0)
        self.assertLess(large, 1.0)


class TestCaseMirror(unittest.TestCase):
    def test_documentation_cases_match_the_scored_cases(self):
        scored = json.loads(PY_CASES.read_text(encoding="utf-8"))
        docs = json.loads(DOC_CASES.read_text(encoding="utf-8"))["test_cases"]
        scored_by_id = {c["id"]: c for c in scored}
        docs_by_id = {c["id"]: c for c in docs}
        self.assertEqual(set(scored_by_id), set(docs_by_id))
        for cid, case in scored_by_id.items():
            self.assertEqual(docs_by_id[cid]["scenario"], case["query"], cid)
            self.assertEqual(docs_by_id[cid]["expected_pipeline"], case["expected_pipeline_id"], cid)


if __name__ == "__main__":
    unittest.main()
