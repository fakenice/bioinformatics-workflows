# Evaluation Framework

完全自动化的 Skill 质量评估框架。**零外部依赖、零 API 调用、零人工参与**。

## 快速开始

```bash
cd python/
python evaluation/runner.py
```

首次运行若无 `outputs.json`，自动使用 dummy 数据跑通全流程。

## 5 个指标

| 指标 | 测量内容 | 类型 | 满分含义 |
|------|----------|------|----------|
| `workflow_accuracy` | 管线匹配是否选对 | 规则匹配 | 18 道有预期管线的题全部一致；2 道跨域题单独统计拒答 |
| `hallucination_rate` | 引用的工具/DOI/URL 是否在 KB 中 | KB 对照 | 所有引用均存在于知识库 |
| `parameter_correctness` | 参数值是否在合理范围内 | 值域校验 | 所有参数均通过阈值检查 |
| `reference_coverage` | 每个步骤是否有引用来源 | 正则扫描 | 所有步骤均附带参考文献 |
| `schema_validity` | 输出的 JSON 是否符合 PipelineDefinition schema | 结构校验 | 所有 JSON 输出合规 |

## 目录结构

```
evaluation/
├── benchmarks/
│   └── test_cases.json       # 20 个测试用例（14 管线 + 6 跨域/边界）
├── metrics/
│   ├── workflow_accuracy.py   # 管线匹配准确率
│   ├── hallucination.py       # 幻觉检测
│   ├── parameter_correctness.py # 参数合理性
│   ├── reference_coverage.py  # 引用覆盖率
│   └── schema_validity.py     # Schema 合规性
├── runner.py                  # 一键运行
├── results/
│   ├── outputs.json           # Skill 输出（需填入真实数据）
│   └── report.json            # 自动生成的评估报告
└── README.md
```

## 如何真实评估（填入 data）

1. 让 Skill 对 `test_cases.json` 中每个 case 的 query 生成回答
2. 将结果整理为 `results/outputs.json`：

```json
{
  "TC-001": "GATK HaplotypeCaller + GenotypeGVCFs... pipeline_id: 'family-trio-wgs' ...",
  "TC-002": "...",
  ...
}
```

3. 运行 `python evaluation/runner.py` 生成 `report.json`

## 口径（v1.1.0）

- 只有 `expected_pipeline_id` 非空的用例进入管线准确率分母；
- 缺少预测 = `unparsed`，显式 `__uncovered__` = `abstained`，两者都不算对；
- 预期为空的跨域题单独统计拒答，不混入管线分母；
- 0 分母指标 `score=None`，由 runner 从 overall 剔除，不再按 100% 计入；
- Wilson 区间、McNemar 精确检验与最小可检测差异直接写在报告里。

## 测试

```bash
cd python
python -m unittest discover -s evaluation/tests -v
```

## 设计原则

- **易执行**：一行命令，零配置
- **零成本**：不需要 API Key、不需要 GPU、不需要人工专家
- **确定性**：所有指标都是确定性规则检查，可复现
- **不夸大**：20 例只能测大效应，报告区间与 MDE，不把 1 例差异写成能力提升
