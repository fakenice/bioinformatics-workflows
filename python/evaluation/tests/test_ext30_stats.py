"""ext30 配对统计的回归测试：保护三样东西。

1. 分辨率函数的手算值——这个函数曾经把"另一侧计数"当成二项总数传给 comb，
   导致 n_disc 较小时虚报"最小可检分裂"，测试用二项分布的闭式值把它钉死；
2. 统计产物与打分产物的一致性——README 引用的每个数字都必须能由
   `report_ext30_*.json` + `outputs_ext30_*.json` 重新算出来，不能各写一套；
3. 已知指标缺口的当前行为——`must_include_params` 未被核对、
   `schema_validity` 0/0 被剔除，这两点是文档里明写的限制，改坏了要能发现。
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from evaluation import analyze_ext30 as ax
from evaluation.metrics import statistics as stats

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
STATS = json.loads((RESULTS / "report_ext30_stats.json").read_text(encoding="utf-8"))


class PairedResolution(unittest.TestCase):
    """min_split_for_significance 对二侧精确 McNemar 的手算闭式值。"""

    def test_two_discordant_pairs_cannot_reach_alpha(self):
        r = ax.min_split_for_significance(2)
        self.assertIsNone(r["minimum_split"])
        self.assertAlmostEqual(r["p_at_minimum_split"], 0.5, places=6)  # 2*(1/4)*2

    def test_four_discordant_pairs_unanimous_is_0p125(self):
        r = ax.min_split_for_significance(4)
        self.assertIsNone(r["minimum_split"])
        self.assertAlmostEqual(r["p_at_minimum_split"], 2.0 / 16.0, places=6)

    def test_nine_discordant_pairs_needs_8_to_1(self):
        r = ax.min_split_for_significance(9)
        self.assertEqual(r["minimum_split"], "8:1")
        # 2 * (C(9,0)+C(9,1)) / 2^9 = 2*10/512，产物里保留 6 位小数
        self.assertAlmostEqual(r["p_at_minimum_split"], 20.0 / 512.0, places=5)

    def test_zero_discordant_reports_nothing_to_resolve(self):
        self.assertIn("no discordant pairs", ax.min_split_for_significance(0)["note"])

    def test_helper_is_consistent_with_min_split_search(self):
        for b, c in ((0, 3), (1, 3), (4, 5), (8, 1)):
            r = ax.min_split_for_significance(b + c)
            if r["minimum_split"] is not None:
                x, y = (int(t) for t in r["minimum_split"].split(":"))
                self.assertLess(stats.mcnemar_exact(x, y), 0.05)
                self.assertGreaterEqual(stats.mcnemar_exact(x - 1, y + 1), 0.05)


class LenientMatching(unittest.TestCase):
    def test_alias_counts_as_expected_id(self):
        self.assertTrue(ax.names_expected_id("走 trio-wgs-denovo 流程", "family-trio-wgs"))

    def test_substring_does_not_count(self):
        # `wes` 不能因为出现 western / westbound 而命中
        self.assertFalse(ax.names_expected_id("a western blot assay", "wes"))
        self.assertTrue(ax.names_expected_id("run wes with --depth 100", "wes"))


class ArtifactConsistency(unittest.TestCase):
    """统计产物必须由打分产物重算得到，且与两臂 report 的计数一致。"""

    @classmethod
    def setUpClass(cls):
        cls.recomputed = ax.analyse()

    def test_stats_file_is_reproducible(self):
        self.assertEqual(STATS["pipeline_selection"]["all_in_scope"],
                         self.recomputed["pipeline_selection"]["all_in_scope"])
        self.assertEqual(STATS["pipeline_selection"]["strict_intersection"],
                         self.recomputed["pipeline_selection"]["strict_intersection"])

    def test_all_in_scope_matches_each_arm_report(self):
        for arm in ("skill", "noskill"):
            rep = json.loads((RESULTS / f"report_ext30_{arm}.json").read_text(encoding="utf-8"))
            ps = next(x for x in rep["details"] if x["metric"] == "pipeline_selection_accuracy")
            v = STATS["pipeline_selection"]["all_in_scope"]
            self.assertEqual(v[f"{arm}_correct"], ps["correct"], arm)
            self.assertEqual(v["n"], ps["total"], arm)

    def test_strict_intersection_is_what_makes_the_headline_gap(self):
        """runner 打印的 73.08% vs 80.77% 在两臂共同解析出的题上是 19/22 vs 19/22。

        这条不是"证明 skill 无效"，而是把表观差与抽取器不对称绑定在同一份产物上：
        一旦有人改了抽取规则，这条会跟着动，提醒重算 README 的表。
        """
        inter = STATS["pipeline_selection"]["strict_intersection"]
        self.assertEqual(inter["skill_correct"], inter["noskill_correct"])
        self.assertEqual(inter["discordant"], {"skill_only": 1, "noskill_only": 1})
        self.assertGreater(inter["mcnemar_exact_two_sided_p"], 0.05)
        audit = STATS["extractor_audit"]["unparsed_counts"]
        self.assertGreater(audit["skill"], audit["noskill"])

    def test_paired_run_cannot_resolve_the_observed_gap(self):
        v = STATS["pipeline_selection"]["all_in_scope"]
        self.assertIsNone(v["paired_resolution"]["minimum_split"],
                          "n_disc=4 时精确二侧检验最小 p=0.125，README 不得写「显著」")
        self.assertGreater(v["mcnemar_exact_two_sided_p"], 0.05)

    def test_schema_validity_stays_excluded(self):
        self.assertIn("schema_validity",
                      json.loads((RESULTS / "report_ext30_skill.json").read_text(
                          encoding="utf-8"))["excluded_metrics"])


class KnownMetricGaps(unittest.TestCase):
    """README 明写的两条限制，当前行为必须与文字一致。"""

    def test_declared_params_are_not_enforced_by_the_metric(self):
        """must_include_params 里有 37 条声明，指标只核对正文碰巧出现过的受管参数。"""
        cases = json.loads((ROOT / "benchmarks" / "test_cases.json").read_text(encoding="utf-8"))
        declared = sum(len(c.get("must_include_params", [])) for c in cases)
        checked = max(
            next(x for x in json.loads((RESULTS / f"report_ext30_{arm}.json").read_text(
                encoding="utf-8"))["details"]
                   if x["metric"] == "parameter_correctness")["total_params_checked"]
            for arm in ("skill", "noskill"))
        self.assertGreater(declared, checked)
        # 声明了但正文没出现的参数不会被判错：这是"100%"不能读成"参数都对了"的原因
        from evaluation.metrics import parameter_correctness as pc
        text = "no numbers here at all"
        rep = pc.compute({"X1": text})
        self.assertEqual(rep["total_params_checked"], 0)

    def test_unscored_case_fields_are_documented_as_gaps(self):
        for name in ("README.md", "README_zh.md"):
            readme = (ROOT.parents[1] / name).read_text(encoding="utf-8")
            for token in ("must_flag_traps", "must_apply_validations"):
                self.assertIn(token, readme,
                              f"{name} 的 ext30 小节必须点名 {token} 这条未打分缺口")


class RenderedExt30Report(unittest.TestCase):
    """`evaluation/results/ext30_report.md` 必须由已提交产物渲染，且重跑不漂移。"""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT.parents[1] / "evaluation" / "metrics"))
        import importlib
        cls.renderer = importlib.import_module("render_ext30_report")
        cls.out = cls.renderer.OUT

    def test_render_is_byte_reproducible(self):
        self.assertTrue(self.out.exists(), "报告未入库，先跑 render_ext30_report.py")
        before = self.out.read_bytes()
        self.renderer.main()
        self.assertEqual(before, self.out.read_bytes())

    def test_rendered_table_carries_no_placeholder(self):
        text = self.out.read_text(encoding="utf-8")
        for bad in ("pending", "Actual evaluation", "TODO", "0.60 / 0.95"):
            self.assertNotIn(bad, text)
        self.assertIn("| strict_intersection |", text)

    def test_rendered_numbers_come_from_the_stats_artifact(self):
        """报告里管线选择那三行必须与 report_ext30_stats.json 完全对齐。"""
        text = self.out.read_text(encoding="utf-8")
        for mode in ("strict_intersection", "all_in_scope", "lenient"):
            row = STATS["pipeline_selection"][mode]
            prefix = f"| {mode} | {row['n']} | {row['skill_correct']} ("
            line = next((l for l in text.splitlines() if l.startswith(prefix)), None)
            self.assertIsNotNone(line, f"{mode}: 渲染表与 stats 的 + Skill 计数不一致")
            self.assertIn(f"| {row['noskill_correct']} (", line)
            self.assertIn(f"| {row['discordant']['skill_only']}/{row['discordant']['noskill_only']} |", line)
            self.assertIn(f"| {row['mcnemar_exact_two_sided_p']} |", line)


if __name__ == "__main__":
    unittest.main()
