[English](README.md)

# FlowSeq — 生物信息学交互式流程导航

**一个知识约束型 AI Skill，面向标准化、可溯源、可复现的生物信息学工作流生成。**

---

## 架构设计

```
┌──────────┐
│   用户   │
└────┬─────┘
     │  自然语言查询
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Skill (SKILL.md)                                            │
│                                                              │
│  步骤 1: 理解查询 → 组学类型 + 实验设计                        │
│                                                              │
│     ┌─ 是否命中快速参考表？ ─┐                                 │
│     │ 是                    │ 否                              │
│     ▼                        ▼                               │
│  步骤 2a                    步骤 2b                           │
│  预设搜索词                 通用搜索（3轮）                     │
│  (按分类关键词)             第1轮: 查找权威来源                  │
│  web_search("GATK...")     第2轮: 深入最佳来源                  │
│  web_search("nf-core...")  第3轮: 补充质控指标                  │
│     │                        │                               │
│     └────────┬───────────────┘                               │
│              ▼                                               │
│  步骤 3: 提取结构化信息                                        │
│  (步骤、工具版本、质控阈值、参考文献)                             │
│              │                                               │
│              ▼                                               │
│  步骤 4: 输出 → Markdown 表格 | FlowSeq JSON                  │
│              │                                               │
│              ▼                                               │
│  步骤 5: 知识积累（反馈闭环）                                   │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  回写到:                                              │     │
│  │  • SKILL.md 快速参考表          (步骤 2b → 2a)       │     │
│  │  • references/study_designs.md  (详细管线)            │     │
│  │  • references/sharp_edges.md    (新增陷阱)            │     │
│  │  • src/data/pipelines/{slug}.json (FlowSeq 数据源)   │     │
│  └──────────────┬──────────────────────────────────────┘     │
└─────────────────┼────────────────────────────────────────────┘
                  │  落地上下文 (references/*.md + 14 管线 JSON)
                  ▼
┌──────────────────────────────────────┐
│  知识约束                             │
│  study_designs  — 决策矩阵            │
│  patterns       — 可复用代码          │
│  sharp_edges    — 已知陷阱            │
│  validations    — QC 规则             │
│  + 语义搜索 (55 切片索引)             │
└────┬─────────────────────────────────┘
     │  受约束的上下文窗口
     ▼
┌──────────┐
│   LLM    │  落地式生成 — 无幻觉的工具或参数
└────┬─────┘
     │
     ▼
┌─────────────────────────┐
│  标准化流程              │  结构化 Markdown + FlowSeq JSON
│  + Nextflow .nf 导出     │  + 工具版本、质控阈值、DOI
└─────────────────────────┘
```

**核心洞察**：Skill 不允许 LLM 自由发挥。每个流程步骤、工具版本、质控阈值和参考文献都必须溯源到知识库。当查询命中未覆盖的领域时，通用搜索路径（步骤 2b）不仅回答用户问题，还会反馈到快速参考表（步骤 5），逐步缩小未知领域。

---

## 项目简介

一个**生物信息学工作流智能 Skill 仓库**，引导 AI 编程助手完成标准化 NGS 分析。它作为用户和 LLM 之间的约束层：Skill 拦截查询，选择正确的流程，注入领域知识（模式、陷阱、验证规则），LLM 生成有据可查、可引用的输出。

本仓库同时托管 **FlowSeq** — 交互式流程浏览器 + Skill 文档前端，已部署至：

**[https://fakenice.github.io/bioinformatics-workflows](https://fakenice.github.io/bioinformatics-workflows)**

---

## Skill 能力

### 管线知识库

| 分类 | 管线 | ID |
|----------|----------|----|
| DNA | WGS 种系变异 | `wgs-germline` |
| DNA | WGS 体细胞变异 | `wgs-somatic` |
| DNA | 家系三人组 WGS | `family-trio-wgs` |
| DNA | WES 捕获测序 | `wes` |
| DNA | GWAS 关联分析 | `gwas` |
| DNA | PRS 多基因风险评分 | `prs` |
| DNA | 罕见变异关联 | `rare-variant` |
| RNA | RNA-seq 差异表达 | `rna-seq` |
| RNA | 单细胞 RNA-seq | `scrna-seq` |
| 表观遗传 | ChIP-seq / CUT&RUN | `chip-seq` |
| 表观遗传 | 全基因组亚硫酸盐 WGBS | `wgbs` |
| 微生物组 | 宏基因组 | `metagenomics` |
| 微生物组 | 16S rRNA | `16s` |
| 遗传流行病 | 孟德尔随机化 | `mendelian-randomization` |

### 参考知识

| 文件 | 内容 |
|------|---------|
| `references/study_designs.md` | 14 种 NGS 实验设计决策矩阵 |
| `references/patterns.md` | 可复用的 Nextflow/Snakemake/WDL 代码模式 |
| `references/sharp_edges.md` | 已知陷阱、边界情况和规避策略 |
| `references/validations.md` | 输出质量验证规则和检查清单 |

### 语义搜索

知识库之上的轻量级检索增强层。79 个文档切片（65 个来自 references + 14 个管线 JSON）已完成嵌入和索引，支持自然语言查询如"如何处理批次效应"或"哪些管线需要 IDR"，检索延迟亚毫秒级，并带有完整溯源（`source_file:L123-L456`）。

**真实语义向量**：嵌入由 `BAAI/bge-small-zh-v1.5`（512 维，中文优化）经 `fastembed` 本地 ONNX 推理生成，无需 GPU 与 API key。首次运行会经 HF 镜像下载模型（`HF_ENDPOINT=https://hf-mirror.com` + `HF_HUB_DISABLE_XET=1`）至 `python/.hf_cache`，之后离线可用。`SemanticSearcher` 默认即使用该嵌入器，仅在未安装 `fastembed` 时回退到哈希向量（仅测试用）。

实现：`python/vector_store/` —— `chunker.py` + `embedder.py` + `chroma_client.py`（NumPy + sklearn 余弦）+ `fastembed_provider.py`。依赖：`fastembed`、`numpy`、`scikit-learn`。

重建索引：`python python/vector_store/build_semantic_index.py --build`。

**已接入 Agent（OPTIMIZATION #6）**：`ResearchAgent.plan()` 现在会查询语义知识库并记录推荐管线与 Top-3 语义命中；`run()` 将推荐结果传入 `search_pipeline()`（新增按 ID 直载路径 `_load_pipeline`），使检索真正驱动业务调用。决策规则为"关键词优先 + 语义兜底"：关键词有稳定命中时以其为准（规避共享切片上 `pipeline_ids` 标签噪声，如 rare-variant 块被标成 `family-trio-wgs`）；仅当关键词漏检（新说法 / 新增管线）时由语义推荐驱动，分歧会在 `format_result()` 中显式呈现。Python 3.11 兼容：`export_workflow` 中含反斜杠的 f-string 表达式已改为预绑定默认值（PEP 701 为 3.12+ 语法）。

**Step 2b 已落进代码**：流程图中的"通用联网搜索（3 轮）"现在由 Python 层实现。当关键词匹配与语义推荐**双双落空**（语义最高聚合分 < `SEMANTIC_MIN_SCORE = 0.45`，按真实查询校准：真命中 ≥ 0.66、盲区兜底 ≥ 0.536、离题约 0.40）时，`ResearchAgent.plan()` 置 `uncovered_domain` 标记，`run()` 产出 `WebFallbackPlan`——一条可直接执行的 3 轮 `web_search` 计划（找权威源 → 深入最佳来源 → 补质控指标），由上层 LLM Agent 依 SKILL.md 执行，命中结果按 Step 5 回写知识库。Python 层仅物化计划与 grounded 契约，自身不发起网络请求。

**检索质量**（bge-small-zh-v1.5 索引评测）：MR 工具变量多词查询 TOP1/TOP2 命中 0.714/0.694；家系三人家系 *de novo* 查询正确命中 `wgs-germline/trio`；Mutect2 查询命中 `wgs-somatic`（0.715）。残余偏差主要为知识覆盖缺口（如 `qc_standards.md` 过薄），非 embedding 问题。

### 质量评估

6 个确定性指标对 Skill 输出做自动化评估，零 API 调用，一键运行。评测模型为 **qwen3:14b**（本地 Ollama，`think=False`，`temperature=0.3`），共 20 个测试用例（14 条管线 + 6 个跨域/边界用例；用例集现已扩至 30 例，扩展运行见下文单独一节），在无联网基线上做 **Prompt + Skill**（SKILL.md 作 system prompt）vs **纯 Prompt**（中性 system prompt）消融对比——隔离 SKILL.md 纯文本贡献，无联网时两组差异纯粹来自 skill 指令本身，控制变量更干净。

**消融结果**（Prompt + Skill vs 纯 Prompt，无联网基线）：

| 指标 | + Skill | 纯 Prompt | 提升 |
|--------|---------|---------|---|
| 管线选择准确率（18 道管线题） | 94.4%（17/18） | 88.9%（16/18） | +5.5 pt |
| 知识落地率 | 96.8% | 94.0% | +2.9 pt |
| 参数正确率 | 100%（15 个参数） | 100%（3 个参数） | 0 |
| 参考文献覆盖率 | 89.5%（17/19） | 68.4%（13/19） | +21.1 pt |
| Schema 有效性 | N/A（0/0） | N/A（0/0） | — |
| **综合（4 项有效指标）** | **95.2%** | **87.8%** | **+7.4 pt** |
| 流程完整性 | 75.6% | 72.0% | +3.7 pt |

管线分母是 18 而不是 20：TC-014 与 TC-017 没有预期管线，单独按“跨域题是否显式拒答”统计；Schema 本轮为 0/0，已从综合分剔除。管线只差 1 例，**不显著**（McNemar 精确检验 p = 1.0；Wilson 95% 区间 74.2–99.0% vs 67.2–96.9%）；修正后的口径与最小可检测差异见 [`evaluation/results/v1.1.0_report.md`](evaluation/results/v1.1.0_report.md)。

```bash
cd python/evaluation
python runner.py                     # 5 项指标评估（results/outputs.json）
python runner.py results/outputs_qwen3_14b.json -o results/report_qwen3_14b_baseline.json
python runner.py results/outputs_qwen3_14b_noskill.json -o results/report_qwen3_14b_noskill.json

# 30 例扩展运行（见下文小节）：重生成回答、评分、配对统计与渲染报告
python generate_outputs.py --cases benchmarks/test_cases.json --out results/outputs_ext30_skill.json --arm skill
python generate_outputs.py --cases benchmarks/test_cases.json --out results/outputs_ext30_noskill.json --arm noskill
python runner.py results/outputs_ext30_skill.json -o results/report_ext30_skill.json
python runner.py results/outputs_ext30_noskill.json -o results/report_ext30_noskill.json
python analyze_ext30.py              # 配对统计 -> results/report_ext30_stats.json
python ../../evaluation/metrics/render_ext30_report.py   # -> evaluation/results/ext30_report.md
```

流程完整性（第 6 项指标）通过 `metrics/workflow_completeness.py` 单独评估——18 个管线用例 × 标准步骤覆盖率（共 82 个标准步骤）。

**上表数据来源**——每个数字都能对应到 `python/evaluation/results/` 下已提交的文件：

| 表中列 | 模型原始输出 | 报告文件 | 实测值 |
|---|---|---|---|
| + Skill | `outputs_qwen3_14b.json` | `report_qwen3_14b_baseline.json` | 0.90 / 0.9684 / 1.0 / 0.8947 / 1.0 → 综合 **0.9526** |
| 纯 Prompt | `outputs_qwen3_14b_noskill.json` | `report_qwen3_14b_noskill.json` | 0.85 / 0.9395 / 1.0 / 0.6842 / 1.0 → 综合 **0.8947** |
| 流程完整性（+ Skill） | — | `workflow_completeness_qwen3_14b_fix4.json` | 62 / 82 标准步骤 = **0.7561** |
| 流程完整性（纯 Prompt） | — | `workflow_completeness_qwen3_14b_noskill_fix4.json` | 59 / 82 = **0.7195** |

每行的指标顺序：管线选择准确率 / 知识落地率 / 参数正确性 / 参考文献覆盖率 / 结构有效性。

**已渲染的报告**：`evaluation/results/v1.0.0_report.md` 由 `python evaluation/metrics/render_report_from_results.py` 从上述文件生成（无 GPU、无网络）。它逐项记录分子与分母，并标出上表显示不出的退化项：**结构有效性本轮是 0/0**（没有任何结构化 JSON 产出，故按"无待检项"存成 100%）、**参数正确性只有 15 与 3 个可抽取参数**、**管线选择准确率的两组只差 1 个用例**（两组都错在 TC-009 与 TC-017）。分母可比的只有参考文献覆盖率（17/19 vs 13/19）与知识落地率（368/380 vs 326/347）——引用综合分时请带上这条口径。

**不要直接运行 `evaluation/metrics/report.py`**：它只是格式化器，`__main__` 里还留着示例占位数字（0.60 / 0.95 等，来自任何真实运行之外的演示值），一旦调用就会把 `results/v1.0.0_report.md` 覆写成占位内容。请使用上面那个渲染脚本。

`results/` 目录下的其他文件属于**另外的运行，不要与上表混用**：`report.json`（综合 0.9823）与 `comparison_report_final.json` 是更早的对比运行，且报告文件内部没有记录各自的输入 outputs。本文引用上表作为对外结论，因为它是控制最严格的设定——同一模型、无联网基线、唯一变量是 SKILL.md。

实现：`python/evaluation/` — 30 个测试用例 × 6 项确定性指标，无外部 API，无需人工标注。上表是已公开的 v1.1.0 运行（20 例）；2026-11-19 新增的 10 例（TC-021…TC-030）单独列在下面，因为它们改变了结论。这 10 例分别是：三批次 RNA-seq 的批次效应与 DESeq2 design 怎么设（TC-021）、只有肿瘤组织、没有配对外周血的体细胞 WGS（TC-022）、提取阴性对照读段数超过临床样本的低生物量 16S（TC-023）、十年前比对到 hg19 的 BAM 要和新测的 hg38 样本一起联合分型（TC-024）、单样本 `-ERC GVCF` 直接拿去注释的风险（TC-025）、用欧洲人群 summary statistics 在中国队列算多基因风险评分（TC-026）、只有一个生物学重复的 ChIP-seq 还能不能用 IDR（TC-027）、以及 10x Multiome 配对单细胞和 PacBio HiFi 结构变异这两道知识库未覆盖的题（TC-028—TC-029）、病例 3000/对照 30000 用 PLINK 卡方检验的 GWAS（TC-030）。

#### 30 例扩展运行（回答生成于 2026-11-19，评分于 2026-11-20）：skill 的效应测不出来

模型与设置与上表完全一致（本地 Ollama `qwen3:14b`，`think=False`，`temperature=0.3`）；两组唯一差别是 system prompt 用 SKILL.md（7,475 字符，`system_prompt_sha256` 33d105c1…）还是中性提示（158 字符，3851f8ec…）。生成耗时 2,353.3 秒（+ Skill）与 2,208.8 秒（纯 Prompt）。溯源文件：`results/outputs_ext30_*_meta.json`；两组各自的原始评分：`results/report_ext30_{skill,noskill}.json`；配对统计：`results/report_ext30_stats.json`，由 `python analyze_ext30.py` 重新生成——它复用 `runner._to_predictions` 和各指标模块，不重新打分。本节的渲染版一并入库：[`evaluation/results/ext30_report.md`](evaluation/results/ext30_report.md)（`python evaluation/metrics/render_ext30_report.py`）——它只读上述四个 JSON 与两份 meta，逐项打印分子分母，产物缺失时写 MISSING 而不填数，内部不含任何写死的结果数字，重跑逐字节一致。

| 指标 | + Skill | 纯 Prompt | 配对检验说明 |
|---|---|---|---|
| 管线选择（runner 口径，各用自己的分母） | 73.08%（19/26） | 80.77%（21/26） | 不是配对比较，见下 |
| 管线选择，两组都解析出答案的 22 例 | 19/22 | 19/22 | McNemar b/c = 1/1，p = 1.0 |
| 管线选择，全部 26 例（未解析算错） | 19/26 | 21/26 | b/c = 1/3，p = 0.625 |
| 管线选择，宽松口径（正文出现预期 id） | 19/26 | 22/26 | b/c = 0/3，p = 0.25 |
| 参考文献覆盖率，按用例任一来源命中 | 17/23 | 18/23 | b/c = 4/5，p = 1.0 |
| 知识落地率（实体级，不可配对） | 637/658 = 96.81% | 721/772 = 93.39% | 没有逐用例配对定义 |
| 参数正确率 | 100%（检出 12 个） | 100%（检出 17 个） | 区分不了两组 |
| Schema 有效性 | 0/0，已剔除 | 0/0，已剔除 | 提示词从未要求 JSON |
| 综合（4 项有效指标） | 83.55% | 83.72% | — |

四条结论，全部是负结果：

1. **看起来的 −9.5 pt 劣势是抽取器造成的。** `runner.py --baseline` 相减的两个百分比来自*不同*的 26 例分母：关键词/正则抽取器在 + Skill 组有 4 个在域用例没解析出管线 id，纯 Prompt 组只有 2 个（`extractor_audit.unparsed_in_scope`）。在两组都解析出答案的 22 例上，结果是 19/22 对 19/22。同一抽取不对称再加上逐用例配对之后，v1.1.0 那个 +21.1 pt 的参考文献覆盖率优势也没能复现：本轮来源级覆盖是 18/28 对 17/28，配对到用例层面是 17/23 对 18/23，p = 1.0。
2. **管线选择这一项，本轮样本量判不出任何差异。** 三种口径的不一致用例数是 2、4、3，全部偏向同一边也只有 p = 0.5、0.125、0.25（每行的 `paired_resolution`），怎么排都到不了 α = 0.05。参考文献覆盖率有 9 例不一致，理论上能判出 8:1（p = 0.039），但本轮实测是 4:5，p = 1.0。非配对口径下的灵敏度下限是 38.9 pt 差距，所以任何结论都要对着配对灵敏度这条线检查，而不是那个数字。诚实的说法是"本轮两个方向都测不出 skill 效应"，不是"skill 拖后腿"。
3. **两组都不会在未覆盖题上主动拒答。** 4 道没有预期管线的题里，+ Skill 组答了 1 道、留下 3 道未解析，纯 Prompt 组答了 3 道、留下 1 道；拒答加分两边都是 0/4，所以 `workflow_accuracy.py` 里的 `__uncovered__` 分支至今没有被真实模型输出检验过。
4. **若干用例声明的字段根本没被评分，它们的 100% 比看起来轻。** `must_flag_traps` 与 `must_apply_validations` 在 30 个用例上都有，但没有任何指标模块引用。`must_include_params` 声明了 37 条参数约束，而参数指标只对硬编码的 13 个参数名做区间检查、且只统计正文里恰好出现的次数（+ Skill 检出 12 处、纯 Prompt 检出 17 处）；它的 `PIPELINES_DIR` 常量（`metrics/parameter_correctness.py:12`）指向一个不存在的目录，也从未被读取。所以 100% 的含义是"抽出来的数都没越界"，不是"声明的参数都用了"。

引用已公开运行请用上面的 v1.1.0 表，引用 30 例运行请用本节。两者都不能作为 skill 有增益的证据：20 例上管线选择只差 1 例、本就不显著（p = 1.0），30 例上配对之后两个方向表面的差异都被消掉了。

### Agent 工作流

Skill 通过 4 个工具暴露 **规划 → 工具调用 → 执行** 循环：

| 工具 | 功能 |
|------|----------|
| `search_pipeline` | 从知识库匹配最佳流程 |
| `check_traps` | 检索指定流程的已知陷阱 |
| `validate_script` | 对生成的脚本执行验证规则 |
| `export_workflow` | 生成可执行 Nextflow DSL2 `.nf` 脚本 |

实现：`python/agent/`

### 自更新

Skill 自动将新发现的流程信息写回仓库（SKILL.md 步骤 5）：新的 `references/` 章节、新的 `src/data/pipelines/*.json` 文件以及索引注册。

### 构建系统

`scripts/build-pipelines.ts` 在每次构建时从结构化模板生成 5 个实验设计管线 JSON。9 个标准组学管线为手动编写 JSON。全部 14 个统一输出到 `index.ts` 和 `versions.json` 供 FlowSeq 前端使用。

---

## FlowSeq — 流程浏览器与文档站点

一个交互式 Web 前端，用于浏览和验证所有 Skill 内容。

### 功能特性

- **分类导航**：支持 DNA 分析、RNA 分析、表观遗传、微生物组四大领域，每个领域下设细分方向子分类（如 DNA → 种系变异 / 体细胞变异 / 关联分析，微生物组 → 宏基因组 / 16S 扩增子等），支持按分类筛选管线
- **智能搜索**：`Ctrl+K` 快捷键唤起搜索框，支持管线名称模糊搜索
- **管线详情**：每个管线展示标准化分析步骤链、推荐工具及版本、参考权威文献（含 DOI 可点击跳转）
- **中英文切换**：右上角 `EN` / `中` 按钮，支持界面语言即时切换
- **管线对比**：选中多条管线进行工具链对比分析
- **本地启动**：双击 `FlowSeq.lnk` 一键启动，自动安装依赖并打开浏览器
- **导出功能**：支持将管线信息导出为 Markdown 或 JSON 格式

### 技术栈

| 层级 | 选型 |
|-------|--------|
| 框架 | React 19 + TypeScript |
| 构建 | Vite |
| Markdown | react-markdown + remark-gfm |
| 样式 | Tailwind CSS 4 |
| 状态 | Zustand 5 |
| 路由 | React Router 7 |
| i18n | 自定义 Context（轻量） |
| 部署 | GitHub Pages + Actions |

### 本地使用

**开发模式（推荐）：**

```bash
npm run dev -- --host --open
```

支持热更新。双击 `FlowSeq.lnk` 一键启动。

**生产构建：**

```bash
npm install
npm run build
npm run preview
```

---

## 项目结构

```
├── SKILL.md                      # Skill 指令文件
├── README.md                     # 英文文档
├── README_zh.md                  # 中文文档
├── references/                   # 知识库文档
│   ├── study_designs.md
│   ├── patterns.md
│   ├── sharp_edges.md
│   ├── validations.md
│   ├── schema.md
│   ├── search_strategies.md
│   ├── qc_standards.md
│   ├── category_tree.md
│   └── architecture.md
├── python/                       # Python 模块 (RAG + Agent)
│   ├── vector_store/             # 语义搜索（切片器 + 嵌入器 + 向量存储）
│   ├── agent/                    # Agent 工作流（工具 + 研究 agent）
│   └── evaluation/               # 评估框架（基准 + 指标）
├── scripts/
│   └── build-pipelines.ts        # 构建时管线 JSON 生成
├── src/                          # FlowSeq 前端
│   ├── i18n/                     # 国际化 (en / zh)
│   ├── components/               # PipelineMarkdown, SourceSwitcher, SearchOverlay 等
│   ├── pages/                    # HomePage, PipelinePage, DocsPage, ComparePage
│   ├── data/pipelines/           # 14 个管线 JSON + index.ts + versions.json
│   ├── store/                    # Zustand 状态管理
│   └── types/                    # TypeScript 类型定义
├── .github/workflows/
│   └── deploy.yml                # 自动部署到 GitHub Pages
├── public/
└── start_flowseq.bat             # 一键开发服务器启动器 (Windows)
```

---

### Agent 与 RAG 集成

当前实现通过本地 Python 工具注册表暴露生物信息学能力，支持基于智能体的工作流编排。其模块化架构与传输层无关，可无缝扩展至 MCP、REST API 或其他 Agent 协议，无需修改底层知识层。语义检索（RAG）可作为检索后端集成，同时保持仓库知识约束的工作流生成范式。

---

## 外部对照

`docs/external_baselines.md` 收集了可与本仓库对照的已发表数字，每个数字都在
2026-11-18 回到原文重新核对，并注明出处与表号；同时列出明确**不可比**的维度
（任务域、结局指标、分母、多重比较校正）。该文件还记录两个负面结果：生物信息
学领域目前没有已发表的 skill 消融定量基线；而为核对引用的几条线索（nf-core
"mass deployment" 论文、两个具名复现工具）查无发表记录，已列入禁止引用清单。

---

## 引用方式

机器可读引用元数据见仓库根目录 `CITATION.cff`（GitHub 会在侧栏自动展示引用建议）。若复用本仓库的流程知识库，请同时注明所索引的上游管线项目的出处与许可。

```bibtex
@software{wu2026flowseq,
  author  = {Wu, Yiting},
  title   = {FlowSeq: A knowledge-constrained AI skill for standardized, traceable and reproducible bioinformatics workflow generation},
  url     = {https://github.com/fakenice/bioinformatics-workflows}
}
```

---

## 许可协议

MIT
