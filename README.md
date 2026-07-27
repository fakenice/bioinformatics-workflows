# FlowSeq — 生物信息学分析流程交互导航

[![Deploy Status](https://github.com/fakenice/flowseq/actions/workflows/deploy.yml/badge.svg)](https://github.com/fakenice/flowseq/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

交互式生物信息学标准分析流程导航平台。选择分析场景，查看标准化流程图、推荐工具参数与权威文献引用。

**在线体验**: https://fakenice.github.io/flowseq

## 覆盖领域

| 分类 | 分析类型 | 参考来源 |
|------|----------|----------|
| DNA | WGS 种系变异分析 | GATK Best Practices, nf-core/sarek |
| DNA | WGS 体细胞变异分析 | GATK4 Mutect2, TCGA |
| DNA | WES 捕获测序 | GATK |
| DNA | GWAS 关联分析 | PLINK, SAIGE |
| RNA | RNA-seq 差异表达 | nf-core/rnaseq, DESeq2 |
| RNA | 单细胞 RNA-seq | Seurat, Scanpy |
| 表观 | ChIP-seq / CUT&RUN | ENCODE Guidelines |
| 表观 | 全基因组甲基化 WGBS | Bismark |
| 微生物 | 宏基因组 | QIIME2, MetaPhlAn |
| 微生物 | 16S rRNA | DADA2 + QIIME2 |

## 功能

- **交互式流程图**: 每个分析步骤可点击展开，查看推荐工具、参数、Docker 镜像
- **权威来源切换**: 同一分析类型可切换 GATK / nf-core 等不同参考来源
- **对比模式**: 并排对比不同来源的流程差异
- **反向搜索**: 输入工具名即可找到属于哪个分析流程
- **Dark 主题**: 深色界面，适合长时间查阅

## 技术栈

| 层 | 选型 |
|----|------|
| 框架 | React 18 + TypeScript 5 |
| 构建 | Vite 5 |
| 流程图 | React Flow 12 |
| 样式 | Tailwind CSS 3 |
| 状态管理 | Zustand 4 |
| 路由 | React Router 6 |
| 部署 | GitHub Pages + Actions |

## 本地运行

```bash
npm install
npm run dev
```

访问 http://localhost:5173/flowseq/

## 项目结构

```
flowseq/
├── src/
│   ├── components/        # UI 组件
│   │   ├── FlowCanvas     # React Flow 管道图
│   │   ├── DetailPanel    # 步骤详情侧边面板
│   │   ├── SourceSwitcher # 参考来源切换
│   │   ├── ReferenceAccordion  # 参考文献折叠区
│   │   ├── PipelineCard   # 分析场景卡片
│   │   ├── CategoryTabs   # 分类标签
│   │   └── Header         # 顶栏 + 搜索
│   ├── pages/             # 页面
│   │   ├── HomePage       # 首页场景选择
│   │   ├── PipelinePage   # 流程详情
│   │   └── ComparePage    # 对比模式
│   ├── data/pipelines/    # 10 个分析流程 JSON 定义
│   ├── store/             # Zustand 状态管理
│   └── types/             # TypeScript 类型定义
├── .github/workflows/     # CI/CD
│   └── deploy.yml         # 自动部署到 GitHub Pages
└── public/
```

## 贡献指南

欢迎提交新的分析流程或更新现有流程数据。

流程定义文件位于 `src/data/pipelines/`，JSON 格式，结构清晰，参考 `wgs-germline.json` 即可上手。

## License

MIT
