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

详见 `references/schema.md`（Markdown 模板 + FlowSeq JSON Schema）。

## 工作流程

## Language Detection

根据用户输入语言自动判断，生成相应语言的管线代码与文档。中文输入 → 中文输出；English → English。无需显式询问语言偏好。

### Step 1: 理解用户需求
确定分析类型 → 分类（DNA/RNA/表观遗传/微生物组/研究设计）→ 查阅上方"快速参考表"判断是否属于内置覆盖范围

### Step 2a: 已覆盖流程 → 使用预设搜索策略

如果分析类型在"快速参考表"中，使用预设搜索策略。URL 清单及通用原则详见 `references/search_strategies.md`。

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

**⚠️ 零结果保护（最高优先级）**：若三轮搜索均未获取到权威有效信息（无官方文档、无 nf-core 流程、无核心文献、无 Bioconductor workflow），**禁止**编造工具、参数或步骤进入 Step 3。改为告知用户未找到官方标准流程，同时列出搜索到的博客/教程/论坛等非权威来源链接，供用户自行判断：「当前未检索到关于 [分析类型] 的官方或标准主流分析流程信息，以下是搜索到的社区讨论和教程，请自行甄别参考：」

- 优先级：官方文档 > nf-core > ENCODE > Bioconductor > 核心文献 > 教程博客
- 如果找不到官方标准流程，在 overview 中明确标注「暂无官方标准化流程」，提供社区最常用方案
- 至少找到 1 个权威来源（官方文档/nf-core/ENCODE/Bioconductor/核心文献）才能输出 FlowSeq JSON；若全部仅来自博客/教程，在 sources[].type 中标注为 "community"

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

> **⚠️ 前端同步（最高优先级）**：新增或修改管线时，除回写 SKILL.md 外，必须同时完成：
> 1. 生成 `src/data/pipelines/{slug}.json`（按 PipelineDefinition schema）
> 2. 在 `src/data/pipelines/index.ts` 中 import 并加入 pipelines 数组
> 3. 语言规则：JSON 只填单语言字段（中文输入→只填 ZH 字段，English→只填 En 字段），不手工补全双语
>
> **缺失任一步骤 → 前端无法显示 → 视为未完成**

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

详见 `references/architecture.md`。

## QC 标准参考（基于 ENCODE/GATK）

详见 `references/qc_standards.md`。

## 知识库参考

本 Skill 内置以下领域知识，直接运用无需搜索：

- **references/study_designs.md** — 研究设计标准流程：家系/Trio 分析、GWAS 病例对照、孟德尔随机化、多基因风险评分 (PRS)、罕见变异聚合检验，含完整代码模板和 QC 阈值
- **references/patterns.md** — Nextflow DSL2、Snakemake、WDL 的代码模式；容器策略；HPC/云扩展；测试模式
- **references/sharp_edges.md** — 常见陷阱：不可恢复失败、内存估算、容器版本、参考基因组兼容性、GATK 特有陷阱等
- **references/validations.md** — 代码审查规则
- **references/schema.md** — 输出格式规范：Markdown 模板 + FlowSeq JSON Schema
- **references/search_strategies.md** — Step 2a 预设搜索策略：各分类官方文档 URL 及通用原则

## 快速示例

用户问"WGS 种系变异标准流程"时 → 走 Step 2a DNA 变异检测预设策略，综合 GATK + nf-core/sarek 输出。

用户问"Hi-C 互作组学标准流程"等未覆盖类型时 → 走 Step 2b 三轮通用搜索，执行完整 Step 5 知识积累（含前端 JSON 管线文件生成 + index.ts 注册 + Markdown 回写）。
