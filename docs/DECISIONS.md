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

## 2026-11-19/20（30 例扩展运行）

13. **扩样本后结论一律改用配对口径重算，不沿用 runner 的百分比相减**：两臂各自的分母
    会被抽取器左右（+ Skill 有 4 个在域用例没解析出管线 id、纯 Prompt 只有 2 个），
    `runner.py --baseline` 因此报出 −9.5 pt；`analyze_ext30.py` 在两臂共同解析的 22 例上
    给 19/22 vs 19/22，另附"未解析算错"与"正文出现预期 id"两种口径
    （`python/evaluation/analyze_ext30.py`、`results/report_ext30_stats.json`）。
14. **用配对灵敏度替代非配对 MDE 作为能否下结论的判据**：n = 26 时非配对下限是 38.9 pt，
    只作量级参考；真正决定能不能说话的是不一致用例数——管线选择的三种口径分别是 2、4、3
    例，全部偏向同一边也只有 p = 0.5、0.125、0.25，够不到 α = 0.05；参考文献覆盖率有 9 例
    不一致，理论上判得出 8:1（p = 0.039），但实测 4:5 给 p = 1.0。所以对外口径是
    "两个方向都测不出 skill 效应"，不是"skill 拖后腿"
    （`python/evaluation/metrics/statistics.py` 的 `mcnemar_exact`；`test_ext30_stats.py`
    逐条锁住这些数）。
15. **未覆盖题的拒答分支仍未被真实输出验证，如实登记**：4 道无预期管线的题里 + Skill 答
    1 道、纯 Prompt 答 3 道，两边拒答加分都是 0/4，`workflow_accuracy.py` 的
    `__uncovered__` 路径不能声称已检验。
16. **用例声明但没人评的字段不算成绩**：`must_flag_traps`、`must_apply_validations` 在 30
    例上都有、被 0 个指标模块引用；`must_include_params` 声明 37 条约束，参数指标只对 13
    个硬编码参数名做区间检查（本轮检出 12 与 17 处），其 `PIPELINES_DIR` 常量指向不存在
    的目录。README 里的 100% 必须写成"抽出来的数都没越界"，并由
    `test_unscored_case_fields_are_documented_as_gaps` 强制文档点名这些缺口。
17. **可引用的运行产物用 `.gitignore` 例外入库，延续 v1.1.0 先例**：ext30 的
    outputs/meta/report/comparison/stats 全部加 `!` 行；文档镜像
    `evaluation/benchmarks/test_cases.json` 仍由 `sync_doc_cases.py` 生成、不手改，其
    `generated` 保持常量，以便再生成逐字节可复现。
