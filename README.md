
# bioinformatics-workflows &middot; 生物信息学工作流 Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A **bioinformatics workflow intelligence Skill repository** for AI coding assistants. Provides structured knowledge of standardized NGS analysis pipelines, guiding LLMs to generate high-quality bioinformatics scripts and pipeline code.

面向 AI 编码助手�?*生物信息学工作流智能 Skill 仓库**。为 LLM 提供标准�?NGS 分析流程的结构化知识，指�?AI 生成高质量的生信分析脚本与管线代码�?

This repository also hosts **FlowSeq** &mdash; both the online documentation frontend for the Skill knowledge base and an interactive analysis pipeline browser for one-stop browsing and validation of all Skill-defined content.

本仓库同时包�?**FlowSeq**&mdash;&mdash;既是 Skill 知识库的在线文档前端，也是交互式分析管线浏览器，一站式浏览和验�?Skill 定义的所有内容�?

**FlowSeq Live Demo**: https://fakenice.github.io/bioinformatics-workflows

---

## Skill Core &middot; 核心

### Core Files &middot; 核心文件

| File | Purpose | 用�?|
|------|---------|------|
| `SKILL.md` | Main Skill instruction file &mdash; defines triggers, execution flow, and safety rules | Skill 主指令文件，定义触发条件、执行流程、安全规�?|
| `references/study_designs.md` | Decision matrix for 14 NGS experimental designs | 14 �?NGS 实验设计的选型决策矩阵 |
| `references/patterns.md` | Reusable code patterns and best practices | 可复用的代码模式与最佳实�?|
| `references/sharp_edges.md` | Common pitfalls, edge cases, and avoidance strategies | 常见陷阱、边界情况与规避策略 |
| `references/validations.md` | Output quality validation rules and checklists | 输出质量校验规则与检查清�?|

### Covered Analysis Pipelines &middot; 覆盖的分析管�?

| Category | Pipeline | ID |
|----------|----------|----|
| DNA | WGS Germline Variant | `wgs-germline` |
| DNA | WGS Somatic Variant | `wgs-somatic` |
| DNA | Family Trio WGS | `family-trio-wgs` |
| DNA | WES Capture Sequencing | `wes` |
| DNA | GWAS Association Analysis | `gwas` |
| DNA | PRS Polygenic Risk Score | `prs` |
| DNA | Rare Variant Association | `rare-variant` |
| RNA | RNA-seq Differential Expression | `rna-seq` |
| RNA | Single-cell RNA-seq | `scrna-seq` |
| Epigenetics | ChIP-seq / CUT&amp;RUN | `chip-seq` |
| Epigenetics | Whole-genome Bisulfite WGBS | `wgbs` |
| Microbiome | Metagenomics | `metagenomics` |
| Microbiome | 16S rRNA | `16s` |
| Genetic Epi | Mendelian Randomization | `mendelian-randomization` |

---

## FlowSeq &mdash; Skill Knowledge Base &amp; Pipeline Browser

FlowSeq &mdash; Skill 知识库与管线浏览�?

Browse all Skill repository documentation online (SKILL.md + 4 references), and interactively explore 14 analysis pipelines with steps, tools, parameters, and references.

既可在线浏览 Skill 仓库的全部文档（SKILL.md + 4 �?reference），也可交互式探�?14 条分析管线的步骤、工具、参数与参考文献�?

### Features &middot; 功能

- **Skill Doc Browser**: Sidebar navigation with online rendering of SKILL.md and all Markdown files under `references/`.
  **Skill 文档浏览**: 侧边栏导航，在线渲染 SKILL.md �?`references/` 下全�?Markdown 文件�?

- **Markdown Pipeline View**: Structured workflow step tables with recommended tools and parameters at a glance (GFM table support).
  **Markdown 管线视图**: 结构化的流程步骤表格，推荐工�?+ 参数一目了然（支持 GFM 表格）�?

- **Authoritative Source Switching**: Switch between GATK, nf-core, and other reference sources for the same analysis type.
  **权威来源切换**: 同一分析类型可切�?GATK / nf-core 等不同参考来源�?

- **Compare Mode**: Side-by-side comparison of workflow differences across sources.
  **对比模式**: 并排对比不同来源的流程差异�?

- **Full-Text Search (Ctrl+K)**: Instant search across pipelines, docs, and tools with highlighted matches.
  **全文搜索 (Ctrl+K)**: 即时搜索管线、文档与工具，高亮匹配结果�?

- **Pipeline Version Management**: Track and switch between pipeline versions for each analysis type.
  **管线版本管理**: 跟踪和切换每条分析管线的版本历史�?

- **Nextflow Script Export**: Generate production-ready `.nf` scripts with one click (copy or download).
  **Nextflow 脚本导出**: 一键生成可部署�?`.nf` 脚本（支持复制或下载）�?

- **Reverse Search**: Enter a tool name to discover which analysis pipeline it belongs to.
  **反向搜索**: 输入工具名即可找到属于哪个分析流程�?

- **References**: Each pipeline includes links to authoritative literature.
  **参考文�?*: 每条管线附带权威文献链接�?

### Tech Stack &middot; 技术栈

| Layer | Choice | 选型 |
|-------|--------|------|
| Framework | React 19 + TypeScript 6 | 框架 |
| Build | Vite 8 | 构建 |
| Markdown | react-markdown 10 | Markdown 渲染 |
| Styling | Tailwind CSS 4 | 样式 |
| State | Zustand 5 | 状态管�?|
| Routing | React Router 7 | 路由 |
| Deployment | GitHub Pages + Actions | 部署 |

### Local Development &middot; 本地运行

```bash
npm install
npm run dev
```

Visit http://localhost:5173/flowseq/

### Project Structure &middot; 项目结构

```
├── SKILL.md                  # Skill main instruction · 主指�?
├── references/               # Skill reference knowledge · 参考知�?
�?  ├── study_designs.md
�?  ├── patterns.md
�?  ├── sharp_edges.md
�?  └── validations.md
├── scripts/
�?  └── build-pipelines.ts    # Build-time pipeline JSON generation · 构建时管线JSON生成
├── app/                      # FlowSeq (Skill docs frontend + pipeline browser)
�?  ├── src/
�?  �?  ├── i18n/             # Internationalization · 国际�?
�?  �?  ├── components/       # UI components · UI 组件
�?  �?  �?  ├── PipelineMarkdown  # Markdown pipeline rendering (GFM)
�?  �?  �?  ├── SourceSwitcher     # Reference source switcher
�?  �?  �?  ├── ReferenceAccordion # Reference collapsible section
�?  �?  �?  ├── PipelineCard       # Analysis scenario card
�?  �?  �?  ├── CategoryTabs       # Category filter tabs
�?  �?  �?  ├── SearchOverlay      # Full-text search (Ctrl+K)
�?  �?  �?  ├── ExportModal        # Nextflow script export
�?  �?  �?  └── Header             # Top bar + search + lang switch
�?  �?  ├── pages/            # Pages · 页面
�?  �?  �?  ├── HomePage           # Home scenario selection
�?  �?  �?  ├── PipelinePage       # Pipeline detail
�?  �?  �?  ├── DocsPage           # Skill docs browser
�?  �?  �?  └── ComparePage        # Compare mode
�?  �?  ├── data/pipelines/   # Pipeline JSON · 管线数据
�?  �?  ├── store/            # Zustand state management
�?  �?  ├── types/            # TypeScript type definitions
�?  �?  └── utils/            # Utility functions
�?  ├── .github/workflows/    # CI/CD
�?  �?  └── deploy.yml        # Auto deploy to GitHub Pages
�?  └── public/
```

## Usage &middot; 使用说明

### As a Skill &middot; 作为 Skill 使用

Load this repository as a Skill for your AI coding assistant to automatically receive:

1. **Experimental design guidance** &mdash; recommends the most suitable NGS approach for your scientific question.
2. **Standardized workflow generation** &mdash; produces analysis scripts following GATK / nf-core and other authoritative sources.
3. **Parameter best practices** &mdash; sensible defaults ready to use, minimizing trial-and-error.
4. **Quality validation checklists** &mdash; output inspection rules for every step.

将本仓库作为 AI 编码助手�?Skill 加载，即可在生信分析任务中自动获得：

1. **实验设计选型指导** &mdash; 根据科学问题推荐最合适的 NGS 方案�?
2. **标准化流程生�?* &mdash; �?GATK / nf-core 等权威来源生成分析脚本�?
3. **参数最佳实�?* &mdash; 默认参数直接可用，减少试错�?
4. **质量校验清单** &mdash; 每个步骤的输出检查规则�?

### As a Reference Browser &middot; 作为参考浏�?

Visit the [FlowSeq Demo](https://fakenice.github.io/bioinformatics-workflows) to browse all Skill documentation and interactively explore every analysis pipeline.

直接访问 [FlowSeq Demo](https://fakenice.github.io/bioinformatics-workflows)，既可浏�?Skill 全部文档，也可交互式探索所有分析管线�?

## License

MIT
*（内容由AI生成，仅供参考）*
