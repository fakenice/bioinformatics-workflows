---
name: "bioinformatics-workflows"
description: "Search official standard bioinformatics analysis pipelines (GATK, nf-core, ENCODE, etc.) and output FlowSeq structured JSON. Covers all omics types and study designs. Invoke when user asks for 分析规范流程, 主流分析方式, standard pipeline, best practices, official workflow, or any bioinformatics analysis method."
---

# Bioinformatics Workflows — 官方分析流程检索

## 核心能力

1. **搜索官方标准流程**：当用户询问某种组学分析类型的标准流程时，使用 web_search 搜索官方来源（GATK Best Practices、nf-core、ENCODE、Broad Institute 等），获取最新版本信息
2. **FlowSeq 结构化输出**：以标准化 JSON schema 输出，可直接作为 FlowSeq 的数据源
3. **内置领域知识**：无需搜索即可提供 Nextflow/Snakemake/WDL 代码模式、容器策略、HPC 配置、常见陷阱和代码审查规则

## 支持的组学类型快速参考

| 组学类型 | category | 推荐 nf-core 流程 | 官方金标准来源 | 关键工具 |
|---------|----------|------------------|--------------|---------|
| WGS 种系变异 | dna | nf-core/sarek | GATK Best Practices (Germline) | BWA-MEM2, GATK HaplotypeCaller |
| WES 种系变异 | dna | nf-core/sarek | GATK Best Practices (Germline) | BWA-MEM2, GATK HaplotypeCaller |
| 体细胞变异 (Tumor-Normal) | dna | nf-core/sarek | GATK Best Practices (Somatic/Mutect2) | BWA-MEM2, GATK Mutect2, Strelka2 |
| RNA-seq 转录组 | rna | nf-core/rnaseq | ENCODE RNA-seq Pipeline | STAR/HISAT2, Salmon, RSEM |
| 单细胞 RNA-seq | rna | nf-core/scrnaseq | Bioconductor OSCA/Seurat | Cell Ranger, STARsolo, Scanpy |
| ChIP-seq (TF/组蛋白) | epigenetics | nf-core/chipseq | ENCODE ChIP-seq Pipeline | BWA, MACS2, PHANTOMpeaktools |
| ATAC-seq | epigenetics | nf-core/ataacseq | ENCODE ATAC-seq Pipeline | Bowtie2, MACS2, IDR |
| DNA 甲基化 (WGBS/RRBS) | epigenetics | nf-core/methylseq | Bismuth/Singer lab guidelines | Bismark, methylKit |
| 微生物组 (16S/宏基因组) | microbiome | nf-core/ampliseq, nf-core/mag | QIIME2, EBI Metagenomics | QIIME2, MetaPhlAn, HUMAnN |
| 长读长测序 | dna | nf-core/nanoseq | ONT/PacBio guidelines | Minimap2, Clair3, Sniffles |
| 结构变异 (SV/CNV) | dna | nf-core/sarek (--tools) | GATK-gCNV, Manta, Lumpy, AnnotSV | Manta, Lumpy, GATK gCNV, AnnotSV |
| 免疫组库 | dna | nf-core/airrflow | AIRR Community standards | MiXCR, IgBlast |

## 研究设计标准流程快速参考

| 研究设计 | category | 推荐来源 | 关键工具 | 详细参考 |
|---------|----------|---------|---------|---------|
| 家系/Trio 分析 (de novo) | dna | GATK GenotypeRefinement, DeNovoGear | GATK HaplotypeCaller, GenotypeGVCFs, VEP | study_designs.md § 家系分析 |
| 病例对照 GWAS | dna | PLINK GWAS, SAIGE, REGENIE | PLINK 2.0, SAIGE, REGENIE, BOLT-LMM, GCTA | study_designs.md § 病例对照 GWAS |
| 孟德尔随机化 (MR) | dna | TwoSampleMR (MRC IEU) | TwoSampleMR R包, MR-PRESSO, IVW, MR-Egger | study_designs.md § 孟德尔随机化 |
| 多基因风险评分 (PRS) | dna | PRSice-2, LDpred2, PRS-CS | PRSice-2, LDpred2, PRS-CS, bigsnpr | study_designs.md § 多基因风险评分 |
| 罕见变异聚合检验 | dna | SKAT/ACAT | SKAT R包, ACAT, EPACTS | study_designs.md § 罕见变异分析 |
| 连锁分析 (Linkage) | dna | MERLIN, Minimac | MERLIN, SimWalk, Allegro | - |
| PCA/群体遗传 | dna | GCTA, ADMIXTURE | GCTA, ADMIXTURE, PLINK PCA | - |

## 输出格式

### 默认格式：结构化 Markdown（人类易读）

默认输出扁平的 Markdown，分为 4 个信息块，一目了然：

```
# <流程中文名>

<来源名称> | <来源版本>

## 流程步骤

| # | 步骤 | 工具 (版本) | 输入 → 输出 | 备注 |
|---|------|------------|------------|------|
| 1 | 序列比对 | BWA-MEM2 (2.2.1) | fastq → bam | 添加 -R read group |
| 2 | 排序去重 | GATK MarkDuplicates (4.4) | bam → bam | 重复率 < 20% |
| 3 | ... | ... | ... | ... |

## QC 阈值

| 指标 | 阈值 | 说明 |
|------|------|------|
| 覆盖度 | ≥ 30x (WGS) | ... |
| Q30 比例 | > 85% | ... |
| ... | ... | ... |

## 官方来源

| 来源 | 类型 | 版本 | 链接 |
|------|------|------|------|
| GATK Best Practices | official | 4.4+ | https://... |
| nf-core/sarek | community | 3.2.3 | https://... |

## 参考文献

- Poplin et al., "Scaling accurate genetic variant discovery...", Nat Biotechnol, 2018. doi:10.1038/...
```

**输出规范：**
- 流程步骤：用表格呈现，每行一个步骤，包含步骤名、工具+版本、输入→输出、备注（陷阱/调参）
- QC 阈值：独立表格呈现，不埋在 notes 中，阈值一目了然
- 官方来源：表格列出所有来源，标注 official/community/paper 类型
- 参考文献：列表形式，含标题、作者、期刊、DOI
- overview：用一句话开头概括流程目标和适用场景
- 简洁原则：docker 镜像名、position 坐标等程序化字段不在 Markdown 中展示

### 可选格式：FlowSeq JSON（程序消费）

当用户明确要求 JSON 格式、或需要导入 FlowSeq 等工具时，输出以下结构化 JSON：

```typescript
interface PipelineDefinition {
  id: string;          // 唯一标识，如 "wgs-germline"
  name: string;        // 英文名
  nameZH: string;      // 中文名
  category: "dna" | "rna" | "epigenetics" | "microbiome";
  tags: string[];      // 如 ["家系分析", "GATK", "BWA"]
  overview: string;    // 一段话概述（中文）
  icon: string;        // "dna" | "microscope" | "layers" | "bacteria"
  sources: PipelineSource[];
}

interface PipelineSource {
  id: string;
  name: string;        // 来源名称，如 "GATK Best Practices"
  type: "official" | "community" | "paper";
  url: string;         // 官方文档 URL
  version: string;     // 来源版本/日期，如 "GATK 4.4+"
  steps: PipelineStep[];
  references: Reference[];
}

interface PipelineStep {
  id: string;
  name: string;        // 步骤中文名
  description: string; // 步骤说明
  tools: {
    name: string;
    version: string;
    params: string;    // 关键参数
    docker: string;     // Docker/Singularity 镜像
  }[];
  inputs: string[];     // 输入文件类型
  outputs: string[];    // 输出文件类型
  notes: string;       // 实用备注（陷阱/调参建议）
  position: { x: number; y: number }; // 流程图坐标 (y 递增 120)
}

interface Reference {
  title: string;
  url: string;
  type: "official" | "paper" | "community";
  doi?: string;         // 文献 DOI
}
```

## 工作流程

## Language Detection（语言检测）

Detect the user's language from their query. If the user writes in Chinese, respond and generate pipeline code with Chinese comments, parameter descriptions, and documentation. If in English, use English throughout. No need to explicitly ask the user which language they prefer.

根据用户输入的语言自动判断：中文输入则用中文生成管线代码、注释、参数说明和文档；英文输入则全部用英文。无需显式询问用户语言偏好。

### Step 1: 理解用户需求
确定分析类型 → 分类（DNA/RNA/表观遗传/微生物组/研究设计）→ 查阅上方"快速参考表"判断是否属于内置覆盖范围

### Step 2a: 已覆盖流程 → 使用预设搜索策略
如果分析类型在"快速参考表"中，使用下方预设策略。**核心原则：已知官方文档 URL 的工具，优先使用 WebFetch 直接抓取官方页面，WebSearch 仅作为补充手段（用于工具对比、版本搜索、QC 阈值等无固定官方页面的信息）。**

**DNA 变异检测：**
- WebFetch: `https://gatk.broadinstitute.org/hc/en-us/articles/360035531212` → GATK Germline SNPs/Indels 最佳实践
- WebFetch: `https://gatk.broadinstitute.org/hc/en-us/articles/360035894711` → GATK Somatic (Mutect2) 最佳实践
- WebFetch: `https://nf-co.re/sarek/latest` → nf-core/sarek 流程文档（步骤、参数、输出）
- WebFetch: `https://github.com/broadinstitute/gatk` → GATK GitHub（最新版本、release notes）
- WebSearch 补充: `"GATK Best Practices" <germline|somatic|Mutect2> <年份>` → 版本更新和社区讨论
- WebSearch 补充: `"Broad Institute" <分析类型> workflow WDL` → WDL 脚本

**RNA 分析：**
- WebFetch: `https://nf-co.re/rnaseq/latest` → nf-core/rnaseq 流程文档
- WebFetch: `https://nf-co.re/scrnaseq/latest` → nf-core/scrnaseq 流程文档
- WebFetch: `https://www.encodeproject.org/rna-seq/` → ENCODE RNA-seq 标准
- WebFetch: `https://bioconductor.org/books/release/OSCA/` → Bioconductor OSCA 单细胞分析教程
- WebSearch 补充: `"nf-core rnaseq" pipeline steps <年份>` → 版本更新
- WebSearch 补充: `"Bioconductor" scRNA-seq workflow` → R 包更新

**表观遗传：**
- WebFetch: `https://www.encodeproject.org/atac-seq/` → ENCODE ATAC-seq 标准
- WebFetch: `https://www.encodeproject.org/chip-seq/` → ENCODE ChIP-seq 标准
- WebFetch: `https://nf-co.re/chipseq/latest` → nf-core/chipseq 流程文档
- WebFetch: `https://nf-co.re/atacseq/latest` → nf-core/atacseq 流程文档
- WebFetch: `https://nf-co.re/methylseq/latest` → nf-core/methylseq 流程文档
- WebSearch 补充: `"<分析类型> data standards" library complexity IDR` → QC 阈值细节

**微生物组：**
- WebFetch: `https://docs.qiime2.org/` → QIIME2 官方文档（16S/宏基因组）
- WebFetch: `https://nf-co.re/ampliseq/latest` → nf-core/ampliseq 流程文档
- WebFetch: `https://nf-co.re/mag/latest` → nf-core/mag 流程文档
- WebFetch: `https://huttenhower.sph.harvard.edu/humann` → HUMAnN 官方文档
- WebSearch 补充: `"QIIME2" <16S|shotgun> workflow official` → 版本更新

**研究设计（家系/GWAS/MR/PRS）：**
- WebFetch: `https://gatk.broadinstitute.org/hc/en-us/articles/360035531212` → GATK GenotypeRefinement（家系/Trio）
- WebFetch: `https://www.cog-genomics.org/plink/2.0/` → PLINK 2.0 官方文档（GWAS QC、关联分析）
- WebFetch: `https://github.com/weizhouUMN/SAIGE` → SAIGE 官方文档（大样本 GWAS）
- WebFetch: `https://rgcgithub.github.io/regenie/` → REGENIE 官方文档（两步法 GWAS）
- WebFetch: `https://mrcieu.github.io/TwoSampleMR/` → TwoSampleMR 官方教程（孟德尔随机化）
- WebFetch: `https://choishingwan.github.io/PRSice/` → PRSice-2 官方教程（PRS 计算）
- WebFetch: `https://privefl.github.io/bigsnpr/articles/LDpred2.html` → LDpred2 官方教程（PRS）
- WebFetch: `https://github.com/szhan/SKAT` → SKAT 官方文档（罕见变异聚合检验）
- WebSearch 补充: `"GWAS best practices" PLINK QC <年份>` → QC 阈值和社区经验
- WebSearch 补充: `"MR-PRESSO" sensitivity analysis` → 敏感性分析细节
- WebSearch 补充: `"SKAT" rare variant gene-based test <年份>` → 版本更新

**变异注释（ANNOVAR/VEP/SnpEff/AnnotSV）：**
- WebFetch: `https://annovar.openbioinformatics.org/en/latest/user-guide/download/` → ANNOVAR 最新数据库版本列表
- WebFetch: `https://annovar.openbioinformatics.org/en/latest/user-guide/startup/` → ANNOVAR 官方使用教程
- WebFetch: `https://github.com/lgmgeo/AnnotSV/blob/master/commandLineOptions.txt` → AnnotSV 完整命令行参数
- WebFetch: `https://github.com/lgmgeo/AnnotSV` → AnnotSV 最新版本和 release notes
- WebFetch: `https://www.ensembl.org/info/docs/tools/vep/index.html` → VEP (Ensembl) 官方文档
- WebFetch: `https://pcingola.github.io/SnpEff/` → SnpEff 官方文档
- WebSearch 补充: `"ANNOVAR" database download hg38 gnomad clinvar dbnsfp` → 数据库版本搜索
- WebSearch 补充: `"ANNOVAR vs VEP vs SnpEff" comparison` → 工具对比

**通用原则**：
1. 官方文档 URL 已知的工具 → **必须先 WebFetch**，获取权威、最新的步骤、参数、版本信息
2. WebSearch 仅用于：无固定官方页面的信息（QC 阈值、社区经验、工具对比、版本更新动态）
3. WebFetch 失败时（页面变动、需要 JS 渲染等），回退到 WebSearch 关键词搜索
4. 每次搜索后，如果发现了新的官方 URL，按 Step 5 知识积累规则回写到本文件中

### Step 2b: 未覆盖流程 → 通用搜索策略
如果分析类型**不在**"快速参考表"中（如空间转录组、Hi-C、蛋白质组、代谢组、单细胞 ATAC 等），执行以下通用搜索策略：

**第 1 轮：查找权威来源**
```
web_search: "<分析类型英文> standard analysis pipeline best practices <年份>"
web_search: "<分析类型英文> nf-core pipeline"
web_search: "<分析类型英文> official workflow guidelines"
```

**第 2 轮：根据第 1 轮结果定向搜索**
- 如果找到 nf-core 流程 → `web_search: "nf-core <pipeline-name>" steps parameters`
- 如果找到 ENCODE 标准 → `web_search: "ENCODE <分析类型> data standards"`
- 如果找到核心文献 → `web_search: "<分析类型> Nature Methods/Protocols workflow <年份>"`
- 如果找到 Bioconductor workflow → `web_search: "Bioconductor <分析类型> workflow"`

**第 3 轮：补充工具和 QC 信息**
```
web_search: "<分析类型> quality control metrics thresholds"
web_search: "<核心工具名> parameters best practices <年份>"
```

**搜索后判断标准：**
- 优先级：官方文档 > nf-core > ENCODE > Bioconductor > 核心文献 > 教程博客
- 如果找不到官方标准流程，在 overview 中明确标注"暂无官方标准化流程"，提供社区最常用方案
- 至少找到 1 个权威来源才能输出 FlowSeq JSON；若全部仅来自博客/教程，在 sources[].type 中标注为 "community"

### Step 3: 提取结构化信息
从搜索结果中提取：
- 官方流程步骤顺序
- 每个步骤的推荐工具及版本
- 工具的关键参数
- 质量控制标准和阈值（如 ENCODE 的 NRF、TSS enrichment、FRiP 等）
- 官方文献和文档链接

### Step 4: 输出结果
默认输出结构化 Markdown（见"输出格式"段落），确保：
- 流程步骤用表格呈现，每行：步骤名 | 工具(版本) | 输入→输出 | 备注
- QC 阈值独立成表，不埋在步骤备注中
- 官方来源用表格列出，标注类型
- 开头一句话概述流程目标和适用场景
- 简洁原则：不展示 docker 镜像名、position 坐标等程序化字段
- 当用户明确要求 JSON 时，输出 FlowSeq JSON（见"输出格式"段落）

### Step 5: 知识积累（仅针对 Step 2b 未覆盖流程）
当通过 Step 2b 通用搜索策略成功获取到新流程信息后，将结果回写到本 Skill 文件中，使下次同类请求直接走 Step 2a 预设路径。

**判断条件：** 以下两种情况均需执行回写：
  1. **未覆盖流程**（Step 2b）：通过通用搜索策略成功找到至少 1 个 official 或 community 来源的新流程。
  2. **已覆盖流程的补充信息**（Step 2a）：即使流程已在快速参考表中，如果在检索中获取了现有知识库未收录的补充信息（如新的子流程、工具参数细节、QC 阈值、代码模板、陷阱等），也必须回写。

  **核心原则**：只要检索到了 references 文件中尚未记录的有价值信息，就应该回写，无论该流程是否已在快速参考表中。

**回写操作：**

1. **追加到快速参考表**
   - 使用文件编辑工具，在 SKILL.md 的"组学类型快速参考表"或"研究设计标准流程快速参考表"末尾追加一行
   - 字段：组学类型 | category | 推荐 nf-core 流程 | 官方金标准来源 | 关键工具
   - 示例：新增 `| Hi-C 互作组学 | epigenetics | nf-core/hic | Aiden Lab juicer | juicer, cooler, HiC-Pro |`

2. **追加预设搜索策略**（可选，当信息较丰富时）
   - 在 SKILL.md 的 Step 2a 对应分类下追加新的搜索关键词组合
   - 格式：`**<新类别名>：**` + 搜索关键词列表

3. **追加详细流程到 references**（当信息非常丰富时）
   - 在 `references/study_designs.md` 末尾追加完整的流程段落
   - 包含：流程步骤、工具版本表、代码模板、QC 阈值表、position 坐标表
   - 段落标题使用 `## <流程名>` 格式

4. **追加陷阱到 sharp_edges**（当搜索中发现特定陷阱时）
   - 在 `references/sharp_edges.md` 末尾追加新的陷阱段落
   - 格式：Id / Severity / Summary / Symptoms / Why / Gotcha / Solution

**回写规范：**
- 文件编辑时使用精确的 SEARCH/REPLACE，只追加内容，不修改已有内容
- 追加位置：快速参考表最后一行之后、references 文件末尾
- 新增条目在 notes 中标注 `[由 Step 5 知识积累自动添加, 日期: YYYY-MM-DD]`
- 每次回写后，在 SKILL.md 的"知识库参考"段落中无需额外记录（references 文件本身就是知识库）

## Agent Workflow（智能体工作流）

FlowSeq 不仅是一个知识库，更是一个可被 LLM Agent 调用的**垂直领域智能体**。其工作流遵循标准的 **Planning → Tool Calling → Execution** 范式：

### Planning（规划层）

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

### Tool Calling（工具层）

Agent 通过以下 4 个 Tool 与 FlowSeq 知识库交互。每个 Tool 有明确的 schema、输入输出类型和边界条件：

| Tool | 功能 | 输入 | 输出 |
|------|------|------|------|
| `search_pipeline` | 根据场景描述匹配最佳管线 | `scenario: str` | `PipelineDefinition` 或 `null` |
| `check_traps` | 检索管线相关的已知陷阱 | `pipeline_id: str` | `List[SharpEdge]` |
| `validate_script` | 对生成的脚本执行规则检查 | `script: str, pipeline_id: str` | `List[ValidationResult]` |
| `export_workflow` | 生成 Nextflow DSL2 可执行脚本 | `pipeline_id: str, params: dict` | `str` (Nextflow .nf 文件) |

Tool 定义和实现见 `python/agent/tools.py`。

### Execution（执行层）

Agent 按 Planning 生成的子任务序列依次调用 Tool，最终产出：

1. **管线推荐**：最匹配的 PipelineDefinition（含工具、版本、参数、QC 阈值）
2. **陷阱警告**：该管线的已知 pitfalls 列表
3. **代码审查报告**：对生成脚本的 validation 扫描结果
4. **可执行脚本**：Nextflow DSL2 `.nf` 文件（含容器声明、资源限制、`set -euo pipefail`）

### Agent 集成示例

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

### Semantic Search（语义检索层）

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

### 与 JD 的对应关系

| JD 要求 | FlowSeq Agent 实现 |
|----------|-------------------|
| 智能体（Agent）常识与探索欲 | Planning → Tool Calling → Execution 三层架构 |
| 将复杂任务拆解并向 AI 提问 | `plan()` 方法自动分解用户需求为子任务序列 |
| 设计 Prompt 与工作流构建垂直领域智能体 | 4 个 Tool 的 schema 定义 + `ResearchAgent` 工作流编排 |
| 代码调试（Debug）习惯 | `validate_script` 自动扫描 14 条 validation 规则 |

---

## 官方来源优先级

按可信度排序：

1. **GATK Best Practices** (Broad Institute) — 金标准
   - 文档：https://gatk.broadinstitute.org/hc/en-us/sections
   - GitHub：https://github.com/broadinstitute/gatk
   - 适用：germline SNPs/Indels、somatic (Mutect2)、CNV、SV

2. **nf-core pipelines** — 社区维护的标准化 Nextflow 流程
   - 主页：https://nf-co.re/pipelines（150+ 流程）
   - GitHub：https://github.com/nf-core
   - 适用：几乎所有组学类型，容器化、可复现、带测试数据

3. **ENCODE Guidelines** — 表观基因组学标准
   - ATAC-seq：https://www.encodeproject.org/atac-seq/
   - ChIP-seq：https://www.encodeproject.org/chip-seq/
   - RNA-seq：https://www.encodeproject.org/rna-seq/
   - 关键标准：生物学重复 ≥2、IDR 一致性、library complexity (NRF/PBC)、TSS enrichment

4. **Broad Institute Terra/AnVIL** — WDL 官方流程
   - 文档：https://gatk.broadinstitute.org/hc/en-us/categories/wdl-scripts
   - 适用：GATK WDL、Terra 平台、GATK4 最佳实践 WDL 实现

5. **Bioconductor workflows** — R 语言生物信息学标准
   - 主页：https://www.bioconductor.org/workflows/
   - 适用：scRNA-seq (OSCA)、差异表达、表观遗传 R 分析

6. **领域核心文献** — Nature Methods/Protocols 发表的标准化方案
   - 优先选择 3 年内的方案，注意工具版本更新

## QC 标准参考（基于 ENCODE/GATK）

### ATAC-seq / ChIP-seq
- 生物学重复 ≥ 2
- 比对率 > 95%（>80% 可接受）
- NRF > 0.9，PBC1 > 0.9，PBC2 > 3
- FRiP score > 0.3（>0.2 可接受）
- TSS enrichment（GRCh38）：> 7 理想，5-7 可接受
- IDR 一致性：rescue 和 self-consistency 比值 < 2
- ATAC-seq：需有 NFR（nucleosome free region）和单核小体峰

### RNA-seq
- 比对率 > 80%
- 重复相关性 R² > 0.8
- rRNA 比例 < 10%
- 5'/3' 偏差 < 1.5

### WGS/WES 变异检测
- 平均覆盖度：WGS ≥ 30x，WES ≥ 100x
- Q30 比例 > 85%
- 重复率 < 20%
- 变异质量：QD > 2.0、MQ > 40.0、FS < 60.0、SOR < 3.0

## 知识库参考

本 Skill 内置以下领域知识，直接运用无需搜索：

- **references/study_designs.md** — 研究设计标准流程：家系/Trio 分析、GWAS 病例对照、孟德尔随机化、多基因风险评分 (PRS)、罕见变异聚合检验，含完整代码模板和 QC 阈值
- **references/patterns.md** — Nextflow DSL2、Snakemake、WDL 的代码模式；容器策略；HPC/云扩展；测试模式
- **references/sharp_edges.md** — 常见陷阱：不可恢复失败、内存估算、容器版本、参考基因组兼容性、GATK 特有陷阱等
- **references/validations.md** — 代码审查规则

## 快速示例

用户问"WGS 种系变异标准流程"时，应搜索：
- web_search: "GATK Best Practices germline short variant discovery 2025"
- web_search: "nf-core sarek pipeline steps"
- 综合后输出包含 GATK 和 nf-core/sarek 两个 source 的完整 PipelineDefinition JSON

用户问"ATAC-seq 标准流程"时，应搜索：
- web_search: "ENCODE ATAC-seq pipeline standards"
- web_search: "nf-core atacseq pipeline"
- 综合后输出包含 ENCODE 和 nf-core 两个 source 的 PipelineDefinition JSON，notes 中包含 QC 阈值

用户问"家系/Trio 分析标准流程"时，应搜索：
- web_search: "GATK GenotypeRefinement trio de novo mutation 2025"
- web_search: "trio exome sequencing analysis best practices"
- 综合后输出包含 GATK 和 DeNovoGear 两个 source 的 PipelineDefinition JSON，notes 中包含 de novo 突变率阈值

用户问"GWAS 病例对照分析流程"时，应搜索：
- web_search: "GWAS best practices PLINK SAIGE REGENIE 2025"
- web_search: "GWAS quality control MAF HWE missingness"
- 综合后输出包含 PLINK 和 SAIGE/REGENIE 两个 source 的 PipelineDefinition JSON，notes 中包含 QC 阈值表

用户问"孟德尔随机化分析流程"时，应搜索：
- web_search: "TwoSampleMR Mendelian randomization workflow"
- web_search: "MR sensitivity analysis MR-PRESSO Steiger"
- 综合后输出包含 TwoSampleMR 标准流程的 PipelineDefinition JSON，notes 中包含 F-statistic 和多效性检验阈值

用户问"Hi-C 互作组学标准流程"（未覆盖类型）时，执行通用搜索策略：
- 第 1 轮：web_search "Hi-C standard analysis pipeline best practices 2025"、"Hi-C nf-core pipeline"、"Hi-C official workflow guidelines"
- 第 2 轮：根据第 1 轮找到的来源（如 juicer、cooler）定向搜索 "cooler Hi-C analysis workflow"、"juicer tools parameters"
- 第 3 轮：web_search "Hi-C quality control metrics thresholds"
- 综合后输出 FlowSeq JSON，overview 中标注来源可信度，sources[].type 标注为 "official" 或 "community"

用户问"Hi-C 互作组学标准流程"（未覆盖类型）且 Step 5 知识积累执行后：
- Step 2b 搜索完成 → 输出 FlowSeq JSON 给用户
- **必须生成 JSON 管线文件**：在 `src/data/pipelines/` 下生成 `{slug}.json`，按 PipelineDefinition schema 编写
- **必须注册管线**：在 `src/data/pipelines/index.ts` 添加 import 并将管线加入 pipelines 数组
- 同时自动回写：在组学快速参考表追加 `| Hi-C 互作组学 | epigenetics | nf-core/hic | Aiden Lab juicer | juicer, cooler, HiC-Pro |`
- 在 Step 2a 表观遗传分类下追加 `**Hi-C 互作组学：**` + 搜索关键词
- 在 study_designs.md 末尾追加 `## Hi-C 互作组学分析` 完整流程段落
- 标注 `[由 Step 5 知识积累自动添加, 日期: 2026-07-28]`
- 下次用户问 Hi-C 时直接走 Step 2a 预设路径，无需重新搜索

**重要**：JSON 管线文件是前端展示的唯一数据源，study_designs.md 中的 Markdown 段落仅供 AI Skill 检索参考，不会出现在 FlowSeq 前端界面中。Step 5 知识积累时必须同时产出 JSON 文件和 Markdown 段落。

**语言规则**：Step 5 生成的 JSON 只填单语言字段，与用户输入语言一致（遵循上述 Language Detection 规则）。中文输入→ 只填 `nameZH`、`overview`、`description`、`notes` 等中文字段，`nameEn`、`overviewEn`、`descriptionEn`、`notesEn` 等英文字段留空；英文输入则相反。前端语言切换时，缺失的语言侧会显示「根据输入语言生成，未翻译」提示。不要手工补全双语。
