# bioinformatics-workflows — 生物信息学工作流 Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

面向 AI 编码助手的**生物信息学工作流智能 Skill 仓库**。为 LLM 提供标准化 NGS 分析流程的结构化知识，指导 AI 生成高质量的生信分析脚本与管线代码。

本仓库同时包含 **FlowSeq** 可视化 Demo，用于交互式浏览和验证 Skill 中定义的分析流程。

**FlowSeq 在线体验**: https://fakenice.github.io/flowseq

---

## Skill 核心

### 核心文件

| 文件 | 用途 |
|------|------|
| `SKILL.md` | Skill 主指令文件，定义触发条件、执行流程、安全规则 |
| `references/study_designs.md` | 14 种 NGS 实验设计的选型决策矩阵 |
| `references/patterns.md` | 可复用的代码模式与最佳实践 |
| `references/sharp_edges.md` | 常见陷阱、边界情况与规避策略 |
| `references/validations.md` | 输出质量校验规则与检查清单 |

### Skill 覆盖的分析管线

| 分类 | 管线 | ID |
|------|------|----|
| DNA | WGS 种系变异 | `wgs-germline` |
| DNA | WGS 体细胞变异 | `wgs-somatic` |
| DNA | 家系 WGS 种系变异 | `family-trio-wgs` |
| DNA | WES 捕获测序 | `wes` |
| DNA | GWAS 关联分析 | `gwas` |
| DNA | PRS 多基因风险评分 | `prs` |
| DNA | 罕见变异关联分析 | `rare-variant` |
| RNA | RNA-seq 差异表达 | `rna-seq` |
| RNA | 单细胞 RNA-seq | `scrna-seq` |
| 表观 | ChIP-seq / CUT&RUN | `chip-seq` |
| 表观 | 全基因组甲基化 WGBS | `wgbs` |
| 微生物 | 宏基因组 | `metagenomics` |
| 微生物 | 16S rRNA | `16s` |
| 遗传流行病 | 孟德尔随机化 | `mendelian-randomization` |

---

## FlowSeq — 可视化 Demo

交互式生物信息学标准分析流程导航平台，以 Markdown 渲染方式展示每条管线的步骤、推荐工具、关键参数与参考文献。

### 功能

- **Markdown 管线视图**: 结构化的流程步骤表格，推荐工具 + 参数一目了然
- **权威来源切换**: 同一分析类型可切换 GATK / nf-core 等不同参考来源
- **对比模式**: 并排对比不同来源的流程差异
- **反向搜索**: 输入工具名即可找到属于哪个分析流程
- **参考文献**: 每条管线附带权威文献链接

### 技术栈

| 层 | 选型 |
|----|------|
| 框架 | React 19 + TypeScript 6 |
| 构建 | Vite 8 |
| Markdown 渲染 | react-markdown 10 |
| 样式 | Tailwind CSS 4 |
| 状态管理 | Zustand 5 |
| 路由 | React Router 7 |
| 部署 | GitHub Pages + Actions |

### 本地运行

```bash
npm install
npm run dev
```

访问 http://localhost:5173/flowseq/

### 项目结构

```
├── SKILL.md                  # Skill 主指令
├── references/               # Skill 参考知识
│   ├── study_designs.md
│   ├── patterns.md
│   ├── sharp_edges.md
│   └── validations.md
├── app/                      # FlowSeq 可视化 Demo（即本目录）
│   ├── src/
│   │   ├── components/       # UI 组件
│   │   │   ├── PipelineMarkdown  # Markdown 管线渲染
│   │   │   ├── SourceSwitcher     # 参考来源切换
│   │   │   ├── ReferenceAccordion # 参考文献折叠区
│   │   │   ├── PipelineCard       # 分析场景卡片
│   │   │   ├── CategoryTabs       # 分类标签
│   │   │   └── Header             # 顶栏 + 搜索
│   │   ├── pages/            # 页面
│   │   │   ├── HomePage           # 首页场景选择
│   │   │   ├── PipelinePage       # 流程详情
│   │   │   └── ComparePage        # 对比模式
│   │   ├── data/pipelines/   # 14 个分析流程 JSON 定义
│   │   ├── store/            # Zustand 状态管理
│   │   ├── types/            # TypeScript 类型定义
│   │   └── utils/            # 工具函数
│   ├── .github/workflows/    # CI/CD
│   │   └── deploy.yml        # 自动部署到 GitHub Pages
│   └── public/
```

## 使用说明

### 作为 Skill 使用

将本仓库作为 AI 编码助手的 Skill 加载，即可在生信分析任务中自动获得：

1. **实验设计选型指导** — 根据科学问题推荐最合适的 NGS 方案
2. **标准化流程生成** — 按 GATK / nf-core 等权威来源生成分析脚本
3. **参数最佳实践** — 默认参数直接可用，减少试错
4. **质量校验清单** — 每个步骤的输出检查规则

### 作为参考浏览

直接访问 [FlowSeq Demo](https://fakenice.github.io/flowseq) 交互式浏览所有分析管线。

## License

MIT
