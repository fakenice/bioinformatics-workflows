# Agent Workflow（智能体工作流）

FlowSeq 不仅是一个知识库，更是一个可被 LLM Agent 调用的**垂直领域智能体**。其工作流遵循标准的 **Planning → Tool Calling → Execution** 范式：

## Planning（规划层）

当用户提出一个生物信息学分析需求时，Agent 将其拆解为子任务序列：

```
用户需求: "我有 trio WGS 数据，想找 de novo 突变"
    ↓
Planning:
  ├── [1] 需求解析 → 识别组学类型 (DNA)、研究设计 (家系 trio)
  ├── [2] 管线匹配 → 查找 knowledge base 中最合适的管线
  ├── [3] 陷阱检查 → 检索该管线相关的 sharp edges
  ├── [4] 代码审查 → 对生成的脚本执行 validation 规则检查
  └── [5] 脚本生成 → 输出 Nextflow DSL2 可执行脚本
```

## Tool Calling（工具层）

Agent 通过以下 4 个 Tool 与 FlowSeq 知识库交互。每个 Tool 有明确的 schema、输入输出类型和边界条件：

| Tool | 功能 | 输入 | 输出 |
|------|------|------|------|
| `search_pipeline` | 根据场景描述匹配最佳管线 | `scenario: str` | `PipelineDefinition` 或 `null` |
| `check_traps` | 检索管线相关的已知陷阱 | `pipeline_id: str` | `List[SharpEdge]` |
| `validate_script` | 对生成的脚本执行规则检查 | `script: str, pipeline_id: str` | `List[ValidationResult]` |
| `export_workflow` | 生成 Nextflow DSL2 可执行脚本 | `pipeline_id: str, params: dict` | `str` (Nextflow .nf 文件) |

Tool 定义和实现见 `python/agent/tools.py`。

## Execution（执行层）

Agent 按 Planning 生成的子任务序列依次调用 Tool，最终产出：

1. **管线推荐**：最匹配的 PipelineDefinition（含工具、版本、参数、QC 阈值）
2. **陷阱警告**：该管线的已知 pitfalls 列表
3. **代码审查报告**：对生成脚本的 validation 扫描结果
4. **可执行脚本**：Nextflow DSL2 `.nf` 文件（含容器声明、资源限制、`set -euo pipefail`）

## Agent 集成示例

```python
from agent.tools import search_pipeline, check_traps, validate_script, export_workflow
from agent.research_agent import ResearchAgent

agent = ResearchAgent()

# Step 1: Planning
plan = agent.plan(user_query="我有 trio WGS 数据，想找 de novo 突变")

# Step 2: Tool Calling
pipeline = search_pipeline(plan.scenario)       # → family-trio-wgs
traps = check_traps(pipeline.id)                 # → VQSR pitfalls, mappability traps
script = export_workflow(pipeline.id, params)    # → trio_de_novo.nf
report = validate_script(script, pipeline.id)    # → 5 passed, 1 warning

# Step 3: Execution — return structured result to user
```

## Semantic Search（语义检索层）

FlowSeq 增加了语义检索能力，可对 references/ 下的领域知识文档和管线定义执行自然语言查询。当用户提出模糊的、跨管线的检索需求时（如"如何处理批次效应"、"哪些管线需要 IDR"、"肿瘤分析的陷阱有哪些"），Agent 可通过语义检索快速定位最相关的文档片段：

```
用户查询: "GWAS 人群分层怎么处理"
    ↓
语义检索 → Top-K 相关文档块 (score + source_file + line_range)
    ↓
返回精准溯源结果 — 可直接定位到 references/xxx.md:L123-L456
```

**架构**：Chunker（语义切片）→ Embedder（向量化）→ VectorStore（NumPy 存储 + sklearn 余弦相似度）→ SemanticSearcher（统一入口）

详细实现见 `python/vector_store/` 目录。

## 与 JD 的对应关系

| JD 要求 | FlowSeq Agent 实现 |
|----------|-------------------|
| 智能体（Agent）常识与探索欲 | Planning → Tool Calling → Execution 三层架构 |
| 将复杂任务拆解并向 AI 提问 | `plan()` 方法自动分解用户需求为子任务序列 |
| 设计 Prompt 与工作流构建垂直领域智能体 | 4 个 Tool 的 schema 定义 + `ResearchAgent` 工作流编排 |
| 代码调试（Debug）习惯 | `validate_script` 自动扫描 14 条 validation 规则 |
