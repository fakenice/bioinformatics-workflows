"""
FlowSeq ResearchAgent

A vertical domain agent that orchestrates Planning → Tool Calling → Execution
for bioinformatics workflow generation. Designed to be invoked by LLM agents
as a specialized tool for bioinformatics pipeline tasks.
"""

from dataclasses import dataclass, field
from typing import Optional

# Support both direct script execution (python agent/research_agent.py)
# and package import (from python.agent.research_agent import ResearchAgent).
try:
    from .tools import (
        PipelineDefinition,
        SharpEdge,
        ValidationResult,
        search_pipeline,
        check_traps,
        validate_script,
        export_workflow,
        predict_pipeline,
        web_search_fallback,
    )
except ImportError:
    from tools import (
        PipelineDefinition,
        SharpEdge,
        ValidationResult,
        search_pipeline,
        check_traps,
        validate_script,
        export_workflow,
        predict_pipeline,
        web_search_fallback,
    )


@dataclass
class SubTask:
    """A single step in the agent's execution plan."""
    step_id: int
    name: str
    tool: str  # Name of the tool to call
    description: str


@dataclass
class AgentPlan:
    """A sequence of sub-tasks generated during the Planning phase."""
    user_query: str
    omics_type: str = ""
    study_design: str = ""
    sub_tasks: list[SubTask] = field(default_factory=list)
    # OPTIMIZATION #6: semantic-search driver fields (filled by plan()).
    recommended_pipeline_id: str = field(default="")
    semantic_pipeline_id: str = field(default="")
    semantic_hits: list[str] = field(default_factory=list)
    # True when BOTH keyword and semantic search miss: triggers Step 2b
    # (README) generic web-search fallback in run().
    uncovered_domain: bool = field(default=False)


@dataclass
class AgentResult:
    """Final result returned by the agent after Execution."""
    pipeline: Optional[PipelineDefinition] = None
    traps: list[SharpEdge] = field(default_factory=list)
    validation_results: list[ValidationResult] = field(default_factory=list)
    nextflow_script: str = ""
    plan: Optional[AgentPlan] = None
    errors: list[str] = field(default_factory=list)
    # Step 2b fallback: populated when the local KB misses the query.
    web_fallback: Optional[object] = None

    @property
    def success(self) -> bool:
        return self.pipeline is not None and len(self.errors) == 0


_SEMANTIC_SEARCHER_CACHE: Optional[object] = None

# Minimum aggregated similarity for a semantic hit to drive the pipeline
# recommendation. Scores below this are treated as "KB does not cover this
# query" → triggers the README Step 2b web-search fallback instead of blindly
# forcing the least-dissimilar pipeline.
# Calibrated on real queries (2026-09):
#   true hits >= 0.660, blind-spot fallback >= 0.536, off-topic ~0.401.
SEMANTIC_MIN_SCORE = 0.45


def _semantic_searcher():
    """Lazily build a cached SemanticSearcher; None if unavailable.

    Caches the real (non-Dummy) searcher across plan() calls so the bge
    embedding model is loaded only once per process. Any failure or the
    Dummy fallback degrades plan() back to pure keyword planning.
    """
    global _SEMANTIC_SEARCHER_CACHE
    if _SEMANTIC_SEARCHER_CACHE is not None:
        return _SEMANTIC_SEARCHER_CACHE
    try:
        from vector_store.semantic_search import SemanticSearcher
        searcher = SemanticSearcher()
        if type(searcher.embedder).__name__ == "DummyEmbedder":
            print("[plan] 语义 embedder 降级为 Dummy，回退关键词规划")
            return None
        _SEMANTIC_SEARCHER_CACHE = searcher
        return searcher
    except Exception as exc:  # pragma: no cover
        print(f"[plan] 语义检索不可用（{exc.__class__.__name__}），回退关键词规划")
        return None


class ResearchAgent:
    """
    A vertical domain agent for bioinformatics workflow research.

    Usage:
        agent = ResearchAgent()
        result = agent.run("我有 trio WGS 数据，想找 de novo 突变")
        if result.success:
            print(f"Found pipeline: {result.pipeline.name}")
            print(f"Traps: {len(result.traps)}")
            print(f"Script:\n{result.nextflow_script}")
    """

    def plan(self, user_query: str) -> AgentPlan:
        """
        Planning phase: decompose user query into sub-tasks.

        The agent identifies the omics type and study design from the query,
        then generates a sequence of Tool Calling steps.
        """
        query_lower = user_query.lower()

        # Detect omics type
        omics_type = ""
        if any(kw in query_lower for kw in ["dna", "wgs", "wes", "变异", "gwas", "trio", "家系", "somatic", "germline"]):
            omics_type = "DNA"
        elif any(kw in query_lower for kw in ["rna", "转录", "expression", "差异表达", "单细胞", "scrna"]):
            omics_type = "RNA"
        elif any(kw in query_lower for kw in ["chip", "atac", "甲基化", "methylation", "wgbs", "表观"]):
            omics_type = "Epigenetic"
        elif any(kw in query_lower for kw in ["16s", "宏基因", "metagenom", "微生物", "microbiome", "菌群"]):
            omics_type = "Microbiome"

        # Detect study design
        study_design = ""
        if any(kw in query_lower for kw in ["trio", "家系", "de novo", "denovo", "父母", "先证者"]):
            study_design = "Family Trio Analysis"
        elif any(kw in query_lower for kw in ["gwas", "病例对照", "case-control"]):
            study_design = "GWAS Case-Control"
        elif any(kw in query_lower for kw in ["孟德尔", "mendelian", "mr", "因果"]):
            study_design = "Mendelian Randomization"
        elif any(kw in query_lower for kw in ["prs", "多基因", "risk score"]):
            study_design = "Polygenic Risk Score"
        elif any(kw in query_lower for kw in ["罕见", "rare variant", "skat"]):
            study_design = "Rare Variant Aggregation"

        # ── Semantic layer (OPTIMIZATION #6) ─────────────────────────────
        # Query the local embedding KB for the best pipeline. The semantic
        # recommendation drives the downstream search_pipeline() call in run().
        # Falls back to pure keyword planning when semantic search is absent.
        semantic_pipeline = ""
        semantic_hits_desc: list[str] = []
        searcher = _semantic_searcher()
        if searcher is not None:
            try:
                res = searcher.search(user_query, n_results=5)
                agg: dict[str, float] = {}
                for h in res.hits:
                    for pid in (h.pipeline_ids or []):
                        agg[pid] = max(agg.get(pid, 0.0), float(h.score))
                if agg:
                    best_pid = max(agg, key=agg.get)
                    # Confidence gate: below SEMANTIC_MIN_SCORE the "hit" is
                    # just the least-dissimilar pipeline and carries no signal.
                    if agg[best_pid] >= SEMANTIC_MIN_SCORE:
                        semantic_pipeline = best_pid
                    else:
                        print(f"[plan] 语义最高分 {agg[best_pid]:.3f} < {SEMANTIC_MIN_SCORE}，"
                              f"视为未覆盖")
                semantic_hits_desc = [f"{h.score:.3f}  {h.section_title}" for h in res.hits[:3]]
                print(f"[plan] 语义命中 {len(res.hits)} 块, 推荐管线: {semantic_pipeline or '(无)'}")
            except Exception as exc:  # pragma: no cover
                print(f"[plan] 语义检索执行失败（{exc.__class__.__name__}），回退关键词规划")

        keyword_pipeline = predict_pipeline(user_query)
        # Hybrid decision: keyword-authoritative + semantic fallback.
        #  - A stable keyword hit wins: it avoids pipeline_ids tag noise in the
        #    chunk labels (e.g. rare-variant blocks tagged family-trio-wgs).
        #  - The semantic recommendation only drives when keywords miss, which
        #    is the real OPT #6 increment (novel wording / new pipelines).
        # Divergence is recorded and surfaced in format_result for transparency.
        semantic_pipeline_id = semantic_pipeline
        if keyword_pipeline:
            recommended_pipeline = keyword_pipeline
            if semantic_pipeline and semantic_pipeline != keyword_pipeline:
                print(f"[plan] 语义推荐={semantic_pipeline} vs 关键词={keyword_pipeline}，"
                      f"采用关键词（分歧已记录）")
        else:
            recommended_pipeline = semantic_pipeline

        # Step 2b (README): both keyword and semantic missed → flag uncovered
        # so run() can materialize the generic 3-round web-search plan instead
        # of silently failing.
        uncovered_domain = not recommended_pipeline

        # Build sub-task sequence
        match_desc = "在知识库中匹配最佳分析管线"
        if recommended_pipeline:
            match_desc += f"（推荐: {recommended_pipeline}）"
        sub_tasks = [
            SubTask(step_id=1, name="需求解析", tool="plan",
                    description=f"识别组学类型={omics_type}, 研究设计={study_design}"),
            SubTask(step_id=2, name="管线匹配", tool="search_pipeline",
                    description=match_desc),
            SubTask(step_id=3, name="陷阱检查", tool="check_traps",
                    description="检索该管线的已知 pitfalls"),
            SubTask(step_id=4, name="脚本生成", tool="export_workflow",
                    description="生成 Nextflow DSL2 可执行脚本"),
            SubTask(step_id=5, name="代码审查", tool="validate_script",
                    description="对生成的脚本执行 validation 规则扫描"),
        ]

        return AgentPlan(
            user_query=user_query,
            omics_type=omics_type,
            study_design=study_design,
            sub_tasks=sub_tasks,
            recommended_pipeline_id=recommended_pipeline,
            semantic_pipeline_id=semantic_pipeline_id,
            semantic_hits=semantic_hits_desc,
            uncovered_domain=uncovered_domain,
        )

    def run(self, user_query: str, knowledge_base_dir: Optional[str] = None) -> AgentResult:
        """
        Full Planning → Tool Calling → Execution cycle.

        Args:
            user_query: Natural language bioinformatics analysis request.
            knowledge_base_dir: Optional override for pipeline JSON directory.

        Returns:
            AgentResult with pipeline, traps, validation, and Nextflow script.
        """
        result = AgentResult()
        errors: list[str] = []

        # Phase 1: Planning
        try:
            plan = self.plan(user_query)
            result.plan = plan
        except Exception as e:
            errors.append(f"Planning failed: {e}")
            result.errors = errors
            return result

        # Phase 2: Tool Calling
        pipeline_id = ""

        try:
            # Tool 1: search_pipeline — the semantic recommendation (from plan)
            # is authoritative: pass the recommended pipeline ID so it loads the
            # exact pipeline (search_pipeline's direct-ID path). Falls back to
            # keyword matching on the raw query when no recommendation exists.
            target = user_query
            if result.plan and getattr(result.plan, "recommended_pipeline_id", ""):
                target = result.plan.recommended_pipeline_id
            pipeline = search_pipeline(target, knowledge_base_dir)
            if pipeline is None:
                # Step 2b (README): local KB missed (keyword + semantic both
                # empty) → materialize the generic 3-round web-search plan for
                # the calling LLM agent to execute; surface it instead of a
                # bare failure.
                omics = getattr(result.plan, "omics_type", "") if result.plan else ""
                design = getattr(result.plan, "study_design", "") if result.plan else ""
                result.web_fallback = web_search_fallback(user_query, omics, design)
                errors.append(
                    "No matching pipeline found in knowledge base; "
                    "Step 2b generic web-search fallback planned."
                )
                result.errors = errors
                return result
            result.pipeline = pipeline
            pipeline_id = pipeline.id
        except Exception as e:
            errors.append(f"search_pipeline failed: {e}")

        try:
            # Tool 2: check_traps
            if pipeline_id:
                result.traps = check_traps(pipeline_id)
        except Exception as e:
            errors.append(f"check_traps failed: {e}")

        try:
            # Tool 3: export_workflow
            if pipeline_id:
                result.nextflow_script = export_workflow(pipeline_id, {}, knowledge_base_dir)
        except Exception as e:
            errors.append(f"export_workflow failed: {e}")

        try:
            # Tool 4: validate_script
            if result.nextflow_script:
                result.validation_results = validate_script(result.nextflow_script, pipeline_id)
        except Exception as e:
            errors.append(f"validate_script failed: {e}")

        result.errors = errors
        return result

    def format_result(self, result: AgentResult) -> str:
        """Format an AgentResult into a human-readable summary."""
        lines = []
        lines.append("# FlowSeq Agent 分析结果\n")

        if result.plan:
            lines.append(f"**分析类型**: {result.plan.omics_type or '未识别'}")
            lines.append(f"**研究设计**: {result.plan.study_design or '未识别'}")
            if getattr(result.plan, "recommended_pipeline_id", ""):
                sem_id = getattr(result.plan, "semantic_pipeline_id", "")
                note = ""
                if sem_id and sem_id != result.plan.recommended_pipeline_id:
                    note = f"（语义推荐 `{sem_id}`，分歧以关键词为准）"
                lines.append(f"**推荐管线 ID**: `{result.plan.recommended_pipeline_id}`{note}"
                             f"（关键词默认: `{predict_pipeline(result.plan.user_query)}`）")
            if getattr(result.plan, "semantic_hits", None):
                lines.append("\n**语义检索命中 Top-3**")
                for hit in result.plan.semantic_hits:
                    lines.append(f"- {hit}")
            lines.append("")

        if result.pipeline:
            p = result.pipeline
            lines.append(f"## 推荐管线: {p.name_zh}\n")
            lines.append(f"- ID: `{p.id}`")
            lines.append(f"- 分类: {p.category}")
            lines.append(f"- 标签: {', '.join(p.tags)}")
            lines.append(f"- {p.overview}")

            lines.append("\n### 流程步骤\n")
            for source in p.sources:
                lines.append(f"**来源: {source.name}**\n")
                for step in source.steps:
                    tool_names = [t.name for t in step.tools]
                    lines.append(f"- {step.name}: {', '.join(tool_names)}")
                lines.append("")

        if result.traps:
            lines.append("## 已知陷阱\n")
            for trap in result.traps:
                lines.append(f"### [{trap.severity.upper()}] {trap.summary}")
                if trap.symptoms:
                    for s in trap.symptoms:
                        lines.append(f"- {s}")
                lines.append(f"**解决**: {trap.solution}")
                lines.append("")

        if result.validation_results:
            passed = sum(1 for vr in result.validation_results if vr.passed)
            total = len(result.validation_results)
            lines.append(f"## 代码审查 ({passed}/{total} 通过)\n")
            for vr in result.validation_results:
                icon = "PASS" if vr.passed else "FAIL"
                lines.append(f"- [{icon}] [{vr.severity}] {vr.message}")

        if result.web_fallback is not None:
            wf = result.web_fallback
            uncovered = getattr(result.plan, "uncovered_domain", False)
            lines.append("\n## 未覆盖领域 — Step 2b 联网兜底\n")
            lines.append(f"- 双轨落空: **{'是' if uncovered else '否'}**（本地知识库未命中）")
            lines.append(f"- 原因: {wf.reason}\n")
            for r in wf.rounds:
                lines.append(f"- **Round {r.round_no}**（{r.goal}）: `{r.query}`")
            lines.append("\n由上层 Agent 依 SKILL.md 执行上述 web_search（3 轮），"
                         "命中结果按 Step 5 回写知识库，缩小盲区。")
            lines.append("\n**零结果保护（SKILL.md 最高优先级）**：若 3 轮仍未检索到权威/官方来源"
                         "（无官方文档、无 nf-core、无核心文献），禁止编造工具/参数/步骤——"
                         "改为诚实返回「未找到官方标准流程」，列出社区/博客等非权威来源链接，"
                         "并在 overview 标注「暂无官方标准化流程」。")
        elif result.errors:
            lines.append("\n## 错误\n")
            for err in result.errors:
                lines.append(f"- {err}")

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Demo: run as standalone
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "我有 trio WGS 数据，想找 de novo 突变"

    agent = ResearchAgent()
    result = agent.run(query)

    print(agent.format_result(result))

    if result.nextflow_script:
        print("\n" + "=" * 60)
        print("GENERATED NEXTFLOW SCRIPT")
        print("=" * 60)
        print(result.nextflow_script[:500])
