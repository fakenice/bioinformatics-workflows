# Decision log

本仓库关键口径与协议决定的记录。每条注明**仓内依据**（文件/代码位置）与可核对的日期
（= git 提交日期，`git log` 可逐条对上）；只收当时已留下书面或代码痕迹的决定。

## 2026-08-03（`8943875`/`bbc0308`/`fe7a0f4` 建仓期）

1. **总原则：Skill 不允许 LLM 自由发挥**——每个流程步骤、工具版本、质控阈值和
   参考文献都必须溯源到知识库；未覆盖领域走通用搜索路径并回写知识库（Step 5），
   逐步缩小未知域（`README_zh.md` §核心洞察）。
2. **中英双语 README，语言切换置顶**（`bbc0308`）。

## 2026-09-02（`4f65b88`…`1ac29a6` 检索链路）

3. **语义检索选型**：bge-small-zh-v1.5（fastembed）+ 79-chunk 索引（`4f65b88`）；
   检索质量以真实查询评测登记在 README（TOP1/TOP2 0.714/0.694；Mutect2 命中
   `wgs-somatic` 0.715），并把残余偏差归位到知识覆盖缺口而非 embedding（`21318c0`）。
4. **匹配计分从"关键词命中数量"改为"关键词长度加权"**：平局原本由 dict 插入顺序
   决定胜负（"单细胞转录组"被匹到 `rna-seq` 的事故），同时为 `scrna-seq` 补复合
   关键词（`OPTIMIZATION.md` #5；`python/agent/tools.py`）。
5. **决策规则定为"关键词优先 + 语义兜底"**：关键词有稳定命中时以其为准——规避共享
   切片上 `pipeline_ids` 的标签噪声（rare-variant 块被标成 `family-trio-wgs`）；
   仅关键词漏检时由语义推荐驱动；两路分歧在 `format_result()` 显式呈现（`9bf63a8`）。
6. **联网兜底有硬阈值且按真实查询校准**：语义最高聚合分 < `SEMANTIC_MIN_SCORE = 0.45`
   （真命中 ≥ 0.66、盲区兜底 ≥ 0.536、离题约 0.40）且关键词也落空时，才产出
   `WebFallbackPlan`（3 轮搜索计划）；**Python 层只物化计划与 grounded 契约，
   自身不发起网络请求**（`7739375`）。
7. **零结果保护**："诚实的 not-found"必须显式出现在 `WebFallbackPlan` 输出与
   SKILL.md 两侧一致（`1ac29a6`）。
8. **Python 3.11 兼容**：`export_workflow` 含反斜杠的 f-string 预绑定默认值
   （PEP 701 为 3.12+ 语法）（`9bf63a8`）。

## 2026-10-13/14（`7b3c747`/`54925ed` 评测协议）

9. **消融在无联网基线上做：Prompt+Skill vs 纯 Prompt（中性 system prompt）**，
   隔离 SKILL.md 纯文本贡献——两组差异只来自 skill 指令本身，控制变量更干净；
   评测模型固定 qwen3:14b（本地 Ollama、`think=False`、`temperature=0.3`），
   运行文件与出处表一并入库（`7b3c747`；`README_zh.md` §Evaluation）。
10. **报告只从已提交产物渲染、逐项记录分子与分母**：`render_report_from_results.py`
    无 GPU 无网络再生成；并点名表内看不出的退化项——结构有效性 0/0 按"无待检项"
    存成 100%、参数正确性仅 15 vs 3 个可抽取参数、**分母可比的只有参考文献
    覆盖率与知识落地率，引用综合分必须带这条口径**（`54925ed`）。

## 2026-11-03（`282e5f3`）

11. **只按有预期管线的用例计分并报不确定性**：管线分母 18 而非 20（TC-014/TC-017
    无预期管线，单独按"跨域题是否显式拒答"统计）；Schema 本轮 0/0 从综合分剔除；
    两组只差 1 例判**不显著**（McNemar 精确 p = 1.0，Wilson 区间重叠），修正口径与
    最小可检测差异写入 `evaluation/results/v1.1.0_report.md`。

## 2026-11-18（`1771492`）

12. **CHANGELOG 以 git 历史为准重写**：旧 changelog 带 AIGC frontmatter 且计数与
    git 历史矛盾，整体替换而非续写。
