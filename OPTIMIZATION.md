# 优化记录 (Optimization Log)

> 产品：FlowSeq — 知识约束型生信工作流 AI Skill + 交互式管线浏览器
> 记录日期：2026-08-31
> 验证环境：Windows / Python 3 / Node (tsc -b exit 0)

---

## 一、本次已修复问题

| # | 问题 | 严重度 | 修复方式 | 涉及文件 |
|---|------|:---:|----------|----------|
| 1 | **评估框架在 Windows 控制台崩溃**：`runner.py` 打印进度条字符 `█░─` 时触发 `UnicodeEncodeError: 'gbk' codec can't encode` | 高 | 模块启动时 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` 强制 UTF-8 输出（带兼容性保护） | `python/evaluation/runner.py` |
| 2 | **Agent 无法作为包导入**：`research_agent.py` 使用裸 `from tools import ...`，`from python.agent.research_agent import ResearchAgent` 直接 `ModuleNotFoundError` | 高 | 改为 `try: from .tools import ... except ImportError: from tools import ...` 双模式导入，脚本直跑与包导入均可用 | `python/agent/research_agent.py` |
| 3 | **`check_traps` 是硬编码桩实现**：代码注释自述 "Minimal stub"，只返回 2 条写死的陷阱，而 `references/sharp_edges.md` 实际有 16 条结构化条目 | 高 | 实现 `_load_sharp_edges()` 真实 Markdown 解析器（解析 Id/Severity/Summary/Symptoms/Solution 段落，带缓存），`check_traps` 返回「通用陷阱 + 管线专属陷阱」 | `python/agent/tools.py` |
| 4 | **陷阱映射表引用 13 个幽灵 ID**：`PIPELINE_TRAP_MAP` 中的 `vqsr-trap`、`mutect2-pon`、`population-stratification`、`"rna-seq strand-specificity"`（含空格）等在 `sharp_edges.md` 中均不存在，被静默丢弃 → 多数管线最多只能拿到 2 条通用陷阱 | 高 | 全部替换为真实存在的 edge ID（如 `vqsr-trap` → `vqsr-chain-vs-parallel`）；通用陷阱改由 `UNIVERSAL_EDGE_IDS` 自动注入，映射表不再重复列举 | `python/agent/tools.py` |
| 5 | **管线匹配错误**：「单细胞转录组分析」被匹配到 `rna-seq` 而非 `scrna-seq`。根因：按关键词命中**数量**计分，两边各命中 1 个平局时由 dict 插入顺序决定胜负 | 中 | 计分改为**关键词长度加权**（特异性高的长词权重更大）；并为 `scrna-seq` 补充复合关键词（`单细胞转录组`/`单细胞测序`/`single-cell`） | `python/agent/tools.py` |
| 6 | **`workflow_completeness.py` 无 CLI 入口**：README 指引「单独运行 `metrics/workflow_completeness.py`」，但直接运行静默退出、零输出 | 中 | 新增 `__main__` CLI：自动合并 `test_cases.json` 的 `expected_pipeline_id` 与 `outputs.json`，输出分数摘要并写报告（同样带 UTF-8 保护） | `python/evaluation/metrics/workflow_completeness.py` |
| 7 | **README 项目结构与实际不符**（中英文版均有）：写了不存在的 `app/` 前缀目录；`start.bat` 实为 `start_flowseq.bat`；`references/` 只列 4/9 个文件 | 低 | 结构树改为真实的根级 `src/` 布局，修正启动脚本名，补全 9 个 references 文件 | `README.md`、`README_zh.md` |
| 8 | **7 个 `.bak_*` 备份文件入库**（`workflow_completeness.py.bak_fix2` 等 6 个 + `test_cases.json.bak_queryfix`） | 低 | 全部删除（git 历史已保留内容） | `python/evaluation/metrics/`、`python/evaluation/benchmarks/` |

### 验证结果

| 验证项 | 结果 |
|--------|------|
| `search_pipeline` 匹配矩阵（16 条代表性查询，覆盖全部 14 条管线） | **16/16 通过** |
| `check_traps("wgs-germline")` | 从 2 条 → **10 条**真实陷阱 |
| `python python/evaluation/runner.py`（Windows GBK 环境） | 跑通，Overall **98.23%** |
| `python python/evaluation/metrics/workflow_completeness.py` | **79.27%**（65/82 标准步骤，18 cases） |
| Agent 脚本直跑模式 + 包导入模式 | 均正常 |
| `npx tsc -b` 前端类型检查 | exit 0 |

---

## 二、已知问题（未修复，需决策或改动较大）

| # | 问题 | 建议处理方式 |
|---|------|-------------|
| 1 | 根目录存在**两套评估框架**：`evaluation/`（旧版，指标命名不一致，如 `hallucination.py`）与 `python/evaluation/`（现役）。用户易混淆 | 确认后删除根目录 `evaluation/`，或在其中放置指向说明 |
| 2 | `FlowSeq.lnk`（Windows 快捷方式）被提交入库，对非 Windows 用户无意义 | `git rm --cached FlowSeq.lnk` 并加入 `.gitignore` |
| 3 | `__pycache__/`、`*.pyc` 被跟踪提交，`.gitignore` 未覆盖 | `.gitignore` 增加 `__pycache__/`、`*.pyc`、`*.bak*`，并 `git rm --cached` 已跟踪文件 |
| 4 | `package.json` version 仍为 `0.0.0`，与已有 `CHANGELOG.md` 脱节 | 升为 `0.1.0` 并打 GitHub Release |
| 5 | 依赖 `reactflow@11` 是已停更的旧包名，官方已迁移至 `@xyflow/react` | 评估迁移（API 基本兼容） |
| 6 | `research_agent.plan()` 为硬编码关键词匹配 + 固定五步子任务序列，"Planning" 阶段名不副实 | 用 `vector_store` 语义检索驱动规划 |
| 7 | 语义检索仅 55 chunks、sklearn TF-IDF 级实现，与 "semantic search" 定位有差距 | 引入真实 embedding 或扩充索引覆盖 |
| 8 | **覆盖缺口**：SKILL.md 快速参考表中的 ATAC-seq、长读长、免疫组库、结构变异**没有对应管线 JSON**；空间转录组、Hi-C 等热门方向未覆盖 | 按 Step 5 回写流程补齐 |
| 9 | 工具版本（FastQC 0.12.1 等）手工维护，无上游版本跟踪机制，会静默过期 | GitHub Action 定期抓取 Bioconda / nf-core 容器 tag |
| 10 | 评估仅 20 cases × 单模型（qwen3:14b），消融对照样本偏小；生成的 `.nf` 无 `nextflow lint` 端到端验证 | 扩充用例与模型矩阵；CI 加 lint |
| 11 | 前端无单元测试；`PipelineManager.tsx` 26KB 单文件 | 引入 vitest；拆分组件 |
| 12 | 关键词子串匹配存在误报风险（`mr`/`tf`/`go`/`chip` 等短词易误命中普通词汇） | 改为词边界/分词匹配，或由语义检索替代 |
| 13 | **命名冲突双重撞名**：① 仓库名与 `GoekeLab/bioinformatics-workflows`（工作流管理器 PoC，教程文章多）撞名，搜索被淹没；② 产品名 "FlowSeq" 与 NLP 论文（Flow Matching 文本生成，arXiv 1909.02480）撞名，SEO 被稀释 | 见「P1 → 命名与可发现性」专项方案（短期零成本弥补，改名作为后备选项） |
| 14 | **陈旧硬编码路径**：`start_flowseq.bat`/`update.bat` 写死 `E:\skills\bioinformatics-workflows`（当前工作区在 F 盘，脚本已失效）；`python/vector_data/documents.json` 中 15 处 `source_file` 指向 `E:\skills\...` | bat 改用 `%~dp0` 相对定位；documents.json 改存仓库相对路径 |

---

## 三、可优化方向（按优先级）

### P0 — 仓库卫生（半天内可完成）

- [ ] `.gitignore` 增加 `__pycache__/`、`*.pyc`、`*.bak*`、`*.lnk`；`git rm --cached` 已跟踪的对应文件
- [ ] 决定根目录 `evaluation/` 旧目录的去留
- [ ] `package.json` 升版本 `0.1.0` + GitHub Release + CHANGELOG 同步

### P1 — 分发与可信度（竞争价值最高）

- [ ] **安装脚本**：按 Agent Skills 开放标准提供 `install.sh` / `npx skills add`，支持一键装入 Claude Code / Codex / Gemini CLI（直接竞品 bioSkills、K-Dense 均以此获客，这是当前最大短板）
- [ ] **端到端验证**：CI 中对 `export_workflow` 产物执行 `nextflow lint` / `-dry-run`，把「生成的脚本真的能跑」做成可验证卖点
- [ ] 向 `GoekeLab/awesome-genomic-skills` 提交收录 PR（最便宜的曝光渠道）

#### 命名与可发现性（专项方案）

**现状**：双重撞名 —— 仓库名撞 `GoekeLab/bioinformatics-workflows`，产品名 "FlowSeq" 撞 NLP 论文。仓库名硬编码于 `vite.config.ts` base、`App.tsx` basename、`Header.tsx`、`SKILL.md` frontmatter、i18n localStorage key。

**推荐策略：短期不改名，用零成本手段抢回可发现性；改名留作后备**

第一阶段（零成本，≈ 30 分钟，建议立即做）：
- [ ] 重写 GitHub About 描述，突出差异点：*"Knowledge-grounded bioinformatics workflow Skill with quantitative evaluation — 14 curated NGS pipelines, traceable references, Nextflow export"*
- [ ] 补充 topics：`bioinformatics` `ngs` `nf-core` `nextflow` `agent-skills` `claude-code` `llm` `pipeline` `genomics` `reproducibility`
- [ ] 全站统一使用完整品牌形式 **"FlowSeq — Bioinformatics Pipeline Navigator"**（README 标题、站点 title 已是此形式，保持不简写）
- [ ] `index.html` 增加 Open Graph / Twitter Card meta（分享卡片影响点击率）
- [ ] 提交 `awesome-genomic-skills`；中文圈可在知乎/生信公众号发一篇「带量化评估的生信 Skill」介绍文引流
- [ ] 修复上表 #14 的陈旧路径（坏脚本会直接劝退新用户）

第二阶段（决策点，观察 1–2 个月后）：
- [ ] 若搜索流量仍被撞名淹没 → 执行仓库改名。候选名：`flowseq-bio`（推荐，保留品牌 + 领域后缀）/ `biopipeline-navigator` / `grounded-bio-skills`
- [ ] 改名影响清单（成本可控，共 5 处）：`vite.config.ts` base、`App.tsx` basename、`Header.tsx` GitHub 链接、`SKILL.md` name、Pages 部署路径；GitHub 对旧仓库 URL 自动重定向，但 **Pages 站点 URL 会变**，需同步更新所有外链与部署配置；i18n localStorage key 建议不动（避免丢用户语言设置）
- [ ] **不建议**改产品品牌名："FlowSeq" 已贯穿前端/JSON/bat/localStorage，改名成本高；且论文撞名只影响搜索引擎，生信目标受众内实际混淆很小

### P2 — 技术深度

- [ ] Agent Planning 阶段改用 `vector_store` 语义匹配，替代硬编码关键词
- [ ] 引入真实语义 embedding，扩充 chunk 覆盖至全部 references
- [ ] 补齐管线：ATAC-seq、空间转录组、Hi-C、长读长（先补 SKILL.md 表中已承诺的 4 条）
- [ ] 工具版本自动跟踪（Bioconda / nf-core 定时同步 + 自动 PR）
- [ ] 消除短关键词误报（词边界匹配或语义化）

### P3 — 工程质量

- [ ] `reactflow` → `@xyflow/react` 迁移；拆分 `PipelineManager.tsx`
- [ ] 测试体系：pytest（Python 侧）+ vitest（前端）；把本次 16 条匹配矩阵固化为回归测试
- [ ] 评估扩充：50+ test cases × 3 个模型，公开 82 标准步骤映射
- [ ] MCP / REST 封装 `python/agent` 四工具（README 已声明 transport-agnostic，尚缺实际接入）

---

## 附：竞品参照（2026-08 调研）

| 项目 | 定位 | 对本项目的启示 |
|------|------|---------------|
| `GPTomics/bioSkills` | 438 skills / 63 子领域，直接竞品 | 广度拼不过；学其安装脚本与分类安装体验 |
| `K-Dense-AI/scientific-agent-skills` | ~24k ⭐，CI 质量门禁 + 版本感知 | 学其质量工程（每技能带测试 + CI） |
| `GoekeLab/awesome-genomic-skills` | 生信 agent skill 目录 | 提交收录；关注其收录标准 |
| `openai/plugins` ngs-analysis | Codex 官方 NGS skill | 借鉴 preflight（环境检查→安装计划→启动）模式 |
| `OLAF` (arXiv 2504.03976) | 对话式端到端生信分析 | 走「真执行」路线，缺本项目的接地可信度层 |
| `BioCoder` / `BioDSBench` | 生信代码生成基准 | 可对标接入以增强评估公信力 |

**战略结论**：不与竞品拼技能数量，主打三个独有资产 —— ① 结构化知识库 + 可视化浏览器；② 确定性评估框架 + 消融数据；③ 自我回写闭环。
