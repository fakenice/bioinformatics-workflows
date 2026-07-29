"""
FlowSeq ResearchAgent

A vertical domain agent that orchestrates Planning → Tool Calling → Execution
for bioinformatics workflow generation. Designed to be invoked by LLM agents
as a specialized tool for bioinformatics pipeline tasks.
"""

from dataclasses import dataclass, field
from typing import Optional

from tools import (
    PipelineDefinition,
    SharpEdge,
    ValidationResult,
    search_pipeline,
    check_traps,
    validate_script,
    export_workflow,
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


@dataclass
class AgentResult:
    """Final result returned by the agent after Execution."""
    pipeline: Optional[PipelineDefinition] = None
    traps: list[SharpEdge] = field(default_factory=list)
    validation_results: list[ValidationResult] = field(default_factory=list)
    nextflow_script: str = ""
    plan: Optional[AgentPlan] = None
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.pipeline is not None and len(self.errors) == 0


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

        # Build sub-task sequence
        sub_tasks = [
            SubTask(step_id=1, name="需求解析", tool="plan",
                    description=f"识别组学类型={omics_type}, 研究设计={study_design}"),
            SubTask(step_id=2, name="管线匹配", tool="search_pipeline",
                    description="在知识库中匹配最佳分析管线"),
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
            # Tool 1: search_pipeline
            pipeline = search_pipeline(user_query, knowledge_base_dir)
            if pipeline is None:
                errors.append("No matching pipeline found in knowledge base.")
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

        if result.errors:
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
