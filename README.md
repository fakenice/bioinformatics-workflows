
# bioinformatics-workflows &middot; A workflow intelligence Skill


A **bioinformatics workflow intelligence Skill repository** for AI coding assistants. Provides structured knowledge of standardized NGS analysis pipelines, guiding LLMs to generate high-quality bioinformatics scripts and pipeline code.

面向 AI 编码助手的**生物信息学工作流智能 Skill 仓库**。为 LLM 提供标准化 NGS 分析流程的结构化知识，指导 AI 生成高质量的生信分析脚本与管线代码。

This repository also hosts **FlowSeq** &mdash; both the online documentation frontend for the Skill knowledge base and an interactive analysis pipeline browser for one-stop browsing and validation of all Skill-defined content.

本仓库同时包含 **FlowSeq**&mdash;&mdash;既是 Skill 知识库的在线文档前端，也是交互式分析管线浏览器，一站式浏览和验证 Skill 定义的所有内容。

**FlowSeq Live Demo**: https://fakenice.github.io/bioinformatics-workflows

---

## Skill Capabilities &middot; 能力概览

### Knowledge Base Self-Update &middot; 知识库自更新

The Skill has an automatic knowledge accumulation mechanism (Step 5 in `SKILL.md`) that writes newly discovered pipeline information back into the repository:

1. **New workflow discovery** &mdash; when a novel analysis pipeline is found via web search, the pipeline details (steps, tools, parameters, references) are written into `references/` files and a corresponding `src/data/pipelines/*.json` file is generated, then registered in `index.ts`.
2. **Existing workflow enrichment** &mdash; even for already-covered pipelines, newly discovered supplementary information (sub-workflows, QC thresholds, parameter details, code templates, edge cases) is written back.

**Core principle**: As long as valuable information not yet in the `references/` files is found, it should be reflected — regardless of whether the pipeline is already in the quick-reference table.

Skill 具备自动知识积累机制（`SKILL.md` 中的 Step 5），可将新发现的管线信息自动回写仓库：

1. **新流程发现** &mdash; 通过网络搜索发现新分析管线时，流程详情（步骤、工具、参数、参考文献）会被写入 `references/` 文件，同时生成对应的 `src/data/pipelines/*.json` 并注册到 `index.ts`。
2. **已有流程补充** &mdash; 即使在快速参考表中已存在，新发现的补充信息（子流程、QC 阈值、参数细节、代码模板、边界情况）也会被回写。

**核心原则**：只要检索到了 `references/` 文件中尚未记录的有价值信息，就应该回写——无论该流程是否已在快速参考表中。

### Pipeline Build System &middot; 管线构建系统

The `scripts/build-pipelines.ts` script automatically generates pipeline JSON files from structured templates defined in `SKILL.md` knowledge. On each build:

- **5 study-design pipelines** (family-trio-wgs, gwas, mendelian-randomization, prs, rare-variant) are auto-generated from template definitions in the build script, producing production-ready JSON with full step details, tool parameters, and references.
- **9 standard omics pipelines** (wgs-germline, wgs-somatic, wes, rna-seq, scrna-seq, chip-seq, wgbs, metagenomics, 16s) are maintained manually as curated JSON files.
- All pipelines are unified into `index.ts` and `versions.json` for the FlowSeq frontend.

`scripts/build-pipelines.ts` 脚本在每次构建时自动从知识库模板生成管线 JSON 文件：

- **5 条研究设计管线**（家系 WGS、GWAS、孟德尔随机化、PRS、罕见变异）由构建脚本中的模板定义自动生成，产出具完整步骤、工具参数和参考文献的生产级 JSON。
- **9 条标准组学管线**（WGS 种系/体细胞、WES、RNA-seq、scRNA-seq、ChIP-seq、WGBS、宏基因组、16S）以精选 JSON 文件手工维护。
- 所有管线统一汇入 `index.ts` 和 `versions.json` 供 FlowSeq 前端使用。

---

### Core Files &middot; 核心文件

| File | Purpose | 用途 |
|------|---------|------|
| `SKILL.md` | Main Skill instruction file &mdash; defines triggers, execution flow, and safety rules | Skill 主指令文件，定义触发条件、执行流程、安全规则 |
| `references/study_designs.md` | Decision matrix for 14 NGS experimental designs | 14 种 NGS 实验设计的选型决策矩阵 |
| `references/patterns.md` | Reusable code patterns and best practices | 可复用的代码模式与最佳实践 |
| `references/sharp_edges.md` | Common pitfalls, edge cases, and avoidance strategies | 常见陷阱、边界情况与规避策略 |
| `references/validations.md` | Output quality validation rules and checklists | 输出质量校验规则与检查清单 |

### Covered Analysis Pipelines &middot; 覆盖的分析管线

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

FlowSeq &mdash; Skill 知识库与管线浏览器

Browse all Skill repository documentation online (SKILL.md + 4 references), and interactively explore 14 analysis pipelines with steps, tools, parameters, and references.

既可在线浏览 Skill 仓库的全部文档（SKILL.md + 4 个 reference），也可交互式探索 14 条分析管线的步骤、工具、参数与参考文献。

### Features &middot; 功能

- **Skill Doc Browser**: Sidebar navigation with online rendering of SKILL.md and all Markdown files under `references/`.
  **Skill 文档浏览**: 侧边栏导航，在线渲染 SKILL.md 及 `references/` 下全部 Markdown 文件。

- **Markdown Pipeline View**: Structured workflow step tables with recommended tools and parameters at a glance (GFM table support).
  **Markdown 管线视图**: 结构化的流程步骤表格，推荐工具 + 参数一目了然（支持 GFM 表格）。

- **Authoritative Source Switching**: Switch between GATK, nf-core, and other reference sources for the same analysis type.
  **权威来源切换**: 同一分析类型可切换 GATK / nf-core 等不同参考来源。

- **Compare Mode**: Side-by-side comparison of workflow differences across sources.
  **对比模式**: 并排对比不同来源的流程差异。

- **Full-Text Search (Ctrl+K)**: Instant search across pipelines, docs, and tools with highlighted matches.
  **全文搜索 (Ctrl+K)**: 即时搜索管线、文档与工具，高亮匹配结果。

- **Pipeline Version Management**: Track and switch between pipeline versions for each analysis type.
  **管线版本管理**: 跟踪和切换每条分析管线的版本历史。

- **Nextflow Script Export**: Generate production-ready `.nf` scripts with one click (copy or download).
  **Nextflow 脚本导出**: 一键生成可部署的 `.nf` 脚本（支持复制或下载）。

- **Reverse Search**: Enter a tool name to discover which analysis pipeline it belongs to.
  **反向搜索**: 输入工具名即可找到属于哪个分析流程。

- **References**: Each pipeline includes links to authoritative literature.
  **参考文献**: 每条管线附带权威文献链接。

### Tech Stack &middot; 技术栈

| Layer | Choice | 选型 |
|-------|--------|------|
| Framework | React 19 + TypeScript 6 | 框架 |
| Build | Vite 8 | 构建 |
| Markdown | react-markdown 10 | Markdown 渲染 |
| Styling | Tailwind CSS 4 | 样式 |
| State | Zustand 5 | 状态管理 |
| Routing | React Router 7 | 路由 |
| Deployment | GitHub Pages + Actions | 部署 |

### Local Usage &middot; 本地使用

**Dev mode (recommended):**

```bash
npm run dev -- --host --open
```

Starts the Vite dev server with hot reload. Edits to SKILL.md, references, or pipeline JSON take effect instantly — just refresh the browser. Double-click `start.bat` for one-click launch, or tell your AI assistant to "open the frontend".

**开发模式（推荐）：**

```bash
npm run dev -- --host --open
```

启动 Vite 开发服务器并支持热更新。修改 SKILL.md、references 或管线 JSON 后刷新浏览器即时生效。双击 `start.bat` 一键启动，或直接告诉 AI 助手"打开前端"。

**Production build (for deployment):**
```bash
npm install
npm run build
npm run preview
```

### Project Structure &middot; 项目结构

```
├── SKILL.md                  # Skill main instruction · 主指令
├── references/               # Skill reference knowledge · 参考知识
│   ├── study_designs.md
│   ├── patterns.md
│   ├── sharp_edges.md
│   └── validations.md
├── scripts/
│   └── build-pipelines.ts    # Build-time pipeline JSON generation · 构建时管线JSON生成
├── app/                      # FlowSeq (Skill docs frontend + pipeline browser)
│   ├── src/
│   │   ├── i18n/             # Internationalization · 国际化
│   │   ├── components/       # UI components · UI 组件
│   │   │   ├── PipelineMarkdown  # Markdown pipeline rendering (GFM)
│   │   │   ├── SourceSwitcher     # Reference source switcher
│   │   │   ├── ReferenceAccordion # Reference collapsible section
│   │   │   ├── PipelineCard       # Analysis scenario card
│   │   │   ├── CategoryTabs       # Category filter tabs
│   │   │   ├── SearchOverlay      # Full-text search (Ctrl+K)
│   │   │   ├── ExportModal        # Nextflow script export
│   │   │   └── Header             # Top bar + search + lang switch
│   │   ├── pages/            # Pages · 页面
│   │   │   ├── HomePage           # Home scenario selection
│   │   │   ├── PipelinePage       # Pipeline detail
│   │   │   ├── DocsPage           # Skill docs browser
│   │   │   └── ComparePage        # Compare mode
│   │   ├── data/pipelines/   # Pipeline JSON · 管线数据
│   │   ├── store/            # Zustand state management
│   │   ├── types/            # TypeScript type definitions
│   │   └── utils/            # Utility functions
│   ├── .github/workflows/    # CI/CD
│   │   └── deploy.yml        # Auto deploy to GitHub Pages
│   └── public/
```

## Usage &middot; 使用说明

### As a Skill &middot; 作为 Skill 使用

Load this repository as a Skill for your AI coding assistant to automatically receive:

**Auto language detection**: Auto-detects your language from input — Chinese queries get Chinese output, English queries get English output. No manual switching needed.

**Pipeline JSON language**: Pipeline data files (`src/data/pipelines/*.json`) contain only the language matching your input. When switching the frontend language toggle, untranslated content shows a "generated from Chinese/English input" hint.

1. **Experimental design guidance** &mdash; recommends the most suitable NGS approach for your scientific question.
2. **Standardized workflow generation** &mdash; produces analysis scripts following GATK / nf-core and other authoritative sources.
3. **Parameter best practices** &mdash; sensible defaults ready to use, minimizing trial-and-error.
4. **Quality validation checklists** &mdash; output inspection rules for every step.
5. **Self-updating knowledge base** &mdash; newly discovered pipeline information and best practices are automatically written back into `references/` files and JSON pipeline definitions, keeping the Skill continuously up-to-date.

将本仓库作为 AI 编码助手的 Skill 加载，即可在生信分析任务中自动获得：

**自动语言检测**：自动检测输入语言——中文输入获得中文输出，英文输入获得英文输出，无需手动切换。

**管线 JSON 语言**：管线数据文件（`src/data/pipelines/*.json`）仅包含与输入语言匹配的单语言内容。前端切换语言时，未翻译的内容会显示「根据输入语言生成，未翻译」提示。

1. **实验设计选型指导** &mdash; 根据科学问题推荐最合适的 NGS 方案。
2. **标准化流程生成** &mdash; 按 GATK / nf-core 等权威来源生成分析脚本。
3. **参数最佳实践** &mdash; 默认参数直接可用，减少试错。
4. **质量校验清单** &mdash; 每个步骤的输出检查规则。
5. **知识库自更新** &mdash; 新发现的管线信息与最佳实践自动回写 `references/` 文件和 JSON 管线定义，Skill 持续保鲜。

### As a Reference Browser &middot; 作为参考浏览

Visit the [FlowSeq Demo](https://fakenice.github.io/bioinformatics-workflows) to browse all Skill documentation and interactively explore every analysis pipeline.

直接访问 [FlowSeq Demo](https://fakenice.github.io/bioinformatics-workflows)，既可浏览 Skill 全部文档，也可交互式探索所有分析管线。

## License

MIT
