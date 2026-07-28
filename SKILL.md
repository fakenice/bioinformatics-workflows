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
| 结构变异 (SV/CNV) | dna | nf-core/sarek (--tools) | GATK-gCNV, Manta, Lumpy | Manta, Lumpy, GATK gCNV |
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
如果分析类型在"快速参考表"中，使用下方预设的搜索关键词组合（根据组学类型选择）：

**DNA 变异检测：**
- `"GATK Best Practices" <germline|somatic|Mutect2> <年份>`
- `"nf-core sarek" pipeline steps`
- `"Broad Institute" <分析类型> workflow WDL`

**RNA 分析：**
- `"nf-core rnaseq" pipeline steps <年份>`
- `"ENCODE RNA-seq pipeline" guidelines`
- `"Bioconductor" <scRNA-seq|OSCA> workflow`

**表观遗传：**
- `"ENCODE" <ATAC-seq|ChIP-seq> pipeline standards`
- `"nf-core" <chipseq|ataacseq|methylseq> pipeline`
- `"<分析类型> data standards" library complexity IDR`

**微生物组：**
- `"QIIME2" <16S|shotgun> workflow official`
- `"nf-core" <ampliseq|mag> pipeline`
- `"HUMAnN" metagenome workflow`

**研究设计（家系/GWAS/MR/PRS）：**
- `"GATK GenotypeRefinement" trio de novo mutation <年份>`
- `"GWAS best practices" PLINK QC <年份>`
- `"SAIGE" <analysis method> pipeline <年份>`
- `"REGENIE" GWAS two-step method`
- `"TwoSampleMR" Mendelian randomization workflow`
- `"MR-PRESSO" sensitivity analysis`
- `"PRSice" <version> polygenic risk score tutorial`
- `"LDpred2" PRS calculation R bigsnpr`
- `"SKAT" rare variant gene-based test <年份>`

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

**判断条件：** 仅当该流程通过 Step 2b 搜索且成功找到至少 1 个 official 或 community 来源时执行。已在快速参考表中的流程跳过此步。

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
- 同时自动回写：在组学快速参考表追加 `| Hi-C 互作组学 | epigenetics | nf-core/hic | Aiden Lab juicer | juicer, cooler, HiC-Pro |`
- 在 Step 2a 表观遗传分类下追加 `**Hi-C 互作组学：**` + 搜索关键词
- 在 study_designs.md 末尾追加 `## Hi-C 互作组学分析` 完整流程段落
- 标注 `[由 Step 5 知识积累自动添加, 日期: 2026-07-28]`
- 下次用户问 Hi-C 时直接走 Step 2a 预设路径，无需重新搜索
