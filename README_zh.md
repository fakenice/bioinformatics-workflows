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

知识库之上的轻量级检索增强层。55 个文档切片（41 个来自 references + 14 个管线 JSON）已完成嵌入和索引，支持自然语言查询如"如何处理批次效应"或"哪些管线需要 IDR"，检索延迟亚毫秒级，并带有完整溯源（`source_file:L123-L456`）。

实现：`python/vector_store/` — NumPy + sklearn，零额外依赖。

### 质量评估

5 个确定性指标对 Skill 输出做自动化评估，零 API 调用，一键运行：

| 指标 | 得分 | 方法 |
|--------|-------|--------|
| 管线选择准确率 | 100% | 预期 pipeline_id 匹配 |
| 知识落地率 | 100% | 工具/DOI/URL 知识库差集扫描 |
| 参数正确率 | 100% | 参数阈值域校验 |
| 参考文献覆盖率 | 95% | DOI/URL 正则提取 |
| Schema 有效性 | 100% | JSON 结构校验 |
| **综合** | **99%** | |

**基线对比**（纯 Prompt vs Prompt + Skill）：

| 指标 | 纯 Prompt | + Skill | 提升 |
|--------|------------|---------|---|
| 管线选择准确率 | 95% | 100% | +5% |
| 参数正确率 | 33% | 100% | +200% |
| 参考文献覆盖率 | 0% | 95% | +∞ |

```bash
cd python/evaluation
python runner.py                     # 5 项指标评估
python runner.py results/outputs.json -b results/baseline_outputs.json  # 基线对比
```

实现：`python/evaluation/` — 20 个测试用例 × 5 项确定性指标，无外部 API，无需人工标注。

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
│   └── validations.md
├── python/                       # Python 模块 (RAG + Agent)
│   ├── vector_store/             # 语义搜索（切片器 + 嵌入器 + 向量存储）
│   ├── agent/                    # Agent 工作流（工具 + 研究 agent）
│   └── evaluation/               # 评估框架（基准 + 指标）
├── scripts/
│   └── build-pipelines.ts        # 构建时管线 JSON 生成
├── app/                          # FlowSeq 前端
│   ├── src/
│   │   ├── i18n/                 # 国际化 (en / zh)
│   │   ├── components/           # PipelineMarkdown, SourceSwitcher, SearchOverlay 等
│   │   ├── pages/                # HomePage, PipelinePage, DocsPage, ComparePage
│   │   ├── data/pipelines/       # 14 个管线 JSON + index.ts + versions.json
│   │   ├── store/                # Zustand 状态管理
│   │   └── types/                # TypeScript 类型定义
│   ├── .github/workflows/
│   │   └── deploy.yml            # 自动部署到 GitHub Pages
│   └── public/
└── start.bat                     # 一键开发服务器启动器
```

---

### Agent 与 RAG 集成

当前实现通过本地 Python 工具注册表暴露生物信息学能力，支持基于智能体的工作流编排。其模块化架构与传输层无关，可无缝扩展至 MCP、REST API 或其他 Agent 协议，无需修改底层知识层。语义检索（RAG）可作为检索后端集成，同时保持仓库知识约束的工作流生成范式。

---

## 许可协议

MIT
