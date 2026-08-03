# 输出格式规范

本文件定义 bioinformatics-workflows Skill 的输出格式：Markdown 模板与 FlowSeq JSON Schema。

## 默认格式：结构化 Markdown

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

## 可选格式：FlowSeq JSON（程序消费）

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
