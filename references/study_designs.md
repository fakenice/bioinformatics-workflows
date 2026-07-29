# Bioinformatics Workflows - 研究设计标准流程

本文件覆盖生物信息学一般研究设计的标准分析流程，包括家系分析、病例对照 GWAS、孟德尔随机化、多基因风险评分和罕见变异分析。

---

## 家系分析 (Family / Pedigree Analysis)

### 核心场景
- **Trio 分析**（先证者 + 父母）：检测 de novo 突变，诊断罕见遗传病
- **核心家系扩展**（含同胞）：共分离分析、单倍型推断
- **大家系/系谱分析**：连锁分析定位致病位点

### Trio De Novo 突变检测流程

```
1. 变异检测 (GATK HaplotypeCaller, 每个家庭成员单独)
   → 输入: BAM (先证者, 父, 母)
   → 输出: gVCF per sample

2. 联合基因分型 (GATK GenomicsDBImport + GenotypeGVCFs)
   → 输入: 3 个 gVCF
   → 输出: joint-genotyped VCF

3. VQSR 或硬过滤 (GATK VariantRecalibrator / VariantFiltration)
   → 输出: 高质量 VCF

4. 变异注释 (VEP / ANNOVAR / SnpEff)
   → 输出: 注释 VCF

5. De novo 突变识别 (GATK VariantFiltration 或 DeNovoGear / triodenovo)
   → 过滤条件: 孩子杂合, 父母均为参考基因型
   → 输出: de novo 候选 VCF

6. 验证与优先级排序
   → 移除区段性重复区域 (Segmental Duplication)
   → 检查 mappability (UCSC mappability track)
   → 评估致病性 (ACMG/AMP 指南, CADD, REVEL, SpliceAI)
```

### 工具与版本

| 步骤 | 推荐工具 | 版本 | Docker |
|------|---------|------|--------|
| 变异检测 | GATK HaplotypeCaller | 4.4+ | broadinstitute/gatk:4.4.0.0 |
| 联合基因分型 | GATK GenotypeGVCFs | 4.4+ | broadinstitute/gatk:4.4.0.0 |
| De novo 识别 | GATK GenotypeRefinement | 4.4+ | broadinstitute/gatk:4.4.0.0 |
| De novo (专用) | DeNovoGear / triodenovo | 0.5+ | - |
| 注释 | Ensembl VEP | 110+ | ensemblorg/ensembl-vep:110 |
| 致病性预测 | CADD, REVEL, SpliceAI | - | - |
| 单倍型推断 | SHAPEIT4 / BEAGLE 5.4 | - | - |
| IBD 检测 | KING / PLINK 2.0 | - | - |

### 关键 QC 阈值
- De novo 突变率：~1.0-1.5 × 10⁻⁸/位点/代（全基因组约 60-100 个 de novo）
- 需排除假阳性：低 mappability 区、区段性重复、低复杂度区
- 亲缘关系验证：KING kinship coefficient ≈ 0.5（一级亲属）、IBD0 < 0.01
- 先证者覆盖度 ≥ 30x（WGS）或 ≥ 100x（WES）

### GATK GenotypeRefinement 模式（推荐）
```bash
# Step 1: Calculate genotype priors
gatk CalculateGenotypePosteriors \
    -V joint.vcf.gz \
    -O joint_with_posteriors.vcf.gz \
    --pedigree trio.ped \
    --supporting-callsets gnomad.vcf.gz

# Step 2: Phase by transmission
gatk PhaseByTransmission \
    -V joint_with_posteriors.vcf.gz \
    --pedigree trio.ped \
    -O phased.vcf.gz

# Step 3: Refine de novo calls
gatk VariantAnnotator \
    -V phased.vcf.gz \
    -O annotated.vcf.gz \
    --resource gnomad.vcf.gz \
    --expression "GNOMAD_AF"

# Filter de novo: child=het, parents=hom-ref
gatk VariantFiltration \
    -V annotated.vcf.gz \
    -O denovo_candidates.vcf.gz \
    --filter-name "de_novo" \
    --filter-expression "vc.getGenotype('child').isHet() && \
        vc.getGenotype('father').isHomRef() && \
        vc.getGenotype('mother').isHomRef()"
```

### PLINK 家系 QC
```bash
# 验证亲缘关系
plink --bfile data --genome --min 0.2 --out relatedness_check

# 检查孟德尔错误
plink --bfile data --me 1 1 --set-me-missing --make-bed --out mendel_checked

# 家系关联分析 (TDT)
plink --bfile data --tdt --out tdt_results
```

---

## 病例对照 GWAS (Case-Control Genome-Wide Association Study)

### 核心场景
- 检测常见变异（MAF > 1%）与表型的关联
- 病例 vs 对照的差异等位基因频率
- 需要大样本（通常 > 1000 例）

### 标准分析流程

```
1. 基因型数据 QC
   ├─ 样本 QC: 缺失率, 性别检查, 杂合度, 亲缘关系
   ├─ 变异 QC: 缺失率, MAF, HWE, 差异缺失
   └─ 输出: 高质量 PLINK 文件集

2. 群体分层校正
   ├─ PCA (主成分分析)
   ├─ 去除异常样本
   └─ 将 PC1-PC10 作为协变量

3. 关联分析
   ├─ 二分类表型: 逻辑回归 (PLINK --logistic / SAIGE / REGENIE)
   ├─ 连续表型: 线性回归 (PLINK --linear / BOLT-LMM)
   └─ 混合模型校正 (SAIGE / REGENIE / BOLT-LMM)

4. 结果解读
   ├─ Manhattan plot, QQ plot
   ├─ 基因组膨胀因子 λ_GC (目标: 0.95-1.05)
   ├─ 显著性阈值: P < 5×10⁻⁸ (全基因组), P < 1×10⁻⁵ (提示性)
   └→ LD clumping + 注释
```

### PLINK QC 标准命令
```bash
# Step 1: 样本级 QC
plink --bfile raw_data \
    --missing \
    --het \
    --sex \
    --check-bims \
    --make-bed --out qc_step1

# 移除高缺失样本 (>3%)
plink --bfile qc_step1 --mind 0.03 --make-bed --out qc_step2

# Step 2: 变异级 QC
# 移除高缺失变异 (>2%)
plink --bfile qc_step2 --geno 0.02 --make-bed --out qc_step3

# 移除低 MAF (<1%)
plink --bfile qc_step3 --maf 0.01 --make-bed --out qc_step4

# HWE 检验 (仅对照中, P < 1×10⁻⁶ 移除)
plink --bfile qc_step4 --hwe 1e-6 --make-bed --out qc_step5

# 差异缺失检验 (病例 vs 对照, P < 1×10⁻⁵ 移除)
plink --bfile qc_step5 --test-missing --out diff_missing
plink --bfile qc_step5 --exclude diff_missing.diff.miss --make-bed --out qc_final

# 亲缘关系检测 (移除二级以上亲属)
plink --bfile qc_final --king-cutoff 0.0884 --make-bed --out qc_unrelated
# 0.0884 = 二级亲属阈值 (PI_HAT ≈ 0.0884)
```

### 群体分层校正
```bash
# PCA (GCTA 或 PLINK)
gcta --bfile qc_unrelated --autosome --make-grm --out grm
gcta --grm grm --pca 20 --out pca_results

# 或使用 PLINK 2.0
plink2 --bfile qc_unrelated --pca 20 --out pca_results

# R: 可视化 PC1 vs PC2, 标注病例/对照
# 检查是否有群体异常样本
```

### 关联分析（三种方法）

```bash
# 方法 1: PLINK 逻辑回归 (基础, 适合中小样本)
plink --bfile qc_unrelated \
    --logistic \
    --covar pca_results.eigenvec \
    --covar-name PC1,PC2,PC3,PC4,PC5 \
    --ci 0.95 \
    --pheno phenotype.txt \
    --out gwas_results

# 方法 2: SAIGE (推荐, 大样本 + 病例不平衡)
# Step 1: 空模型 (拟合均值和方差)
Rscript step1_fitNULLGLMM.R \
    --phenoFile=pheno.txt \
    --phenoCol=pheno \
    --covarColList=PC1,PC2,PC3,PC4,PC5 \
    --sampleIDCol=IID \
    --bedFile=qc_unrelated.bed \
    --bimFile=qc_unrelated.bim \
    --famFile=qc_unrelated.fam \
    --GRMFile=grm \
    --outputPrefix=saige_null

# Step 2: 关联检验
Rscript step2_SPAtests.R \
    --nullModel=saige_null.rda \
    --bedFile=qc_unrelated.bed \
    --bimFile=qc_unrelated.bim \
    --famFile=qc_unrelated.fam \
    --outputFile=saige_results.txt

# 方法 3: REGENIE (两步法, 适合 UKB 级别大数据)
# Step 1: 空模型
regenie \
    --step 1 \
    --bed qc_unrelated \
    --phenoFile pheno.txt \
    --covarFile covariates.txt \
    --covarColList PC1,PC2,PC3,PC4,PC5 \
    --bt \
    --bsize 1000 \
    --lowmem \
    --out regenie_step1

# Step 2: 关联检验
regenie \
    --step 2 \
    --bed qc_unrelated \
    --phenoFile pheno.txt \
    --covarFile covariates.txt \
    --covarColList PC1,PC2,PC3,PC4,PC5 \
    --bt \
    --pred regenie_step1_pred.list \
    --bsize 400 \
    --out regenie_results
```

### GWAS QC 阈值汇总

| QC 步骤 | 指标 | 阈值 | 工具 |
|---------|------|------|------|
| 样本缺失率 | --mind | < 0.03 (3%) | PLINK |
| 变异缺失率 | --geno | < 0.02 (2%) | PLINK |
| 最小等位基因频率 | --maf | > 0.01 (1%) | PLINK |
| HWE (仅对照) | --hwe | P > 1×10⁻⁶ | PLINK |
| 差异缺失 | --test-missing | P > 1×10⁻⁵ | PLINK |
| 杂合度异常 | ±3 SD | - | PLINK --het |
| 亲缘关系 | PI_HAT | < 0.0884 (移除二级以上) | PLINK --king |
| 性别一致性 | F coefficient | 男 0.8-1.0, 女 < 0.2 | PLINK --check-sex |
| 基因组膨胀因子 | λ_GC | 0.95-1.05 | LDSC / GCTA |
| 显著性阈值 | P value | < 5×10⁻⁸ | - |

---

## 孟德尔随机化 (Mendelian Randomization, MR)

### 核心场景
- 利用遗传变异作为工具变量评估暴露与结局的因果关系
- 双样本 MR（使用 GWAS summary statistics）
- 不需要个体基因型数据

### 标准分析流程

```
1. 选择工具变量
   ├─ 从暴露 GWAS 中选 IV (P < 5×10⁻⁸)
   ├─ Clumping (r² < 0.001, window 10Mb)
   ├─ 去除与结局连锁不平衡的 IV
   └→ 检查 IV 强度 (F-statistic > 10)

2. 提取结局 GWAS 中的对应 SNP
   ├─ 正链对齐 (harmonization)
   ├─ 去除回文 SNP (中间等位基因, MAF > 0.4 去除)
   └→ 输出: 暴露 β + SE, 结局 β + SE

3. MR 估计
   ├─ IVW (逆方差加权) - 主分析方法
   ├─ MR-Egger - 检验水平多效性
   ├─ 加权中位数 (Weighted Median)
   ├─ 加权模式 (Weighted Mode)
   └→ 最多似然法 (Maximum Likelihood)

4. 敏感性分析
   ├─ Cochran's Q (异质性检验)
   ├─ MR-Egger 截距 (水平多效性)
   ├─ Leave-one-out (逐个 SNP 剔除)
   ├─ MR-PRESSO (离群值检测)
   └→ Steiger filtering (因果方向检验)

5. 多变量 MR (可选)
   ├─ 控制混杂暴露
   └→ 评估独立因果效应
```

### TwoSampleMR R 包标准代码

```r
# 安装
install.packages("TwoSampleMR", repos = c("https://mrcieu.r-universe.dev", "https://cloud.r-project.org"))

library(TwoSampleMR)

# Step 1: 提取暴露 GWAS 工具变量
exposure_dat <- extract_instruments(
    outcomes = "ieu-a-2",  # BMI GWAS ID
    p1 = 5e-8,              # 全基因组显著性阈值
    clump = TRUE,           # LD clumping
    r2 = 0.001,             # r² 阈值
    kb = 10000              # clumping window
)

# 检查工具变量强度 (F-statistic)
# F = beta² / se², 要求 F > 10
exposure_dat$F_stat <- (exposure_dat$beta.exposure / exposure_dat$se.exposure)^2
mean(exposure_dat$F_stat)  # 应 > 10

# Step 2: 提取结局 GWAS 中对应 SNP
outcome_dat <- extract_outcome_data(
    snps = exposure_dat$SNP,
    outcomes = "ieu-a-7"  # 冠心病 GWAS ID
)

# Step 3: 正链对齐 (harmonization)
dat <- harmonise_data(
    exposure_dat = exposure_dat,
    outcome_dat = outcome_dat,
    action = 2  # 去除回文 SNP (MAF > 0.4)
)

# Step 4: MR 分析
res <- mr(dat)

# res 包含:
# - mr_ivw (逆方差加权, 主方法)
# - mr_egger_regression (MR-Egger)
# - mr_weighted_median (加权中位数)
# - mr_weighted_mode (加权模式)

# Step 5: 敏感性分析
# 异质性检验
het <- mr_heterogeneity(dat)
# Cochran's Q: P < 0.05 表示存在异质性

# 水平多效性
pleio <- mr_pleiotropy_test(dat)
# MR-Egger 截距 P < 0.05 表示存在水平多效性

# Leave-one-out
loo <- mr_leaveoneout(dat)

# 单个 SNP 分析
single <- mr_singlesnp(dat)

# Step 6: 可视化
mr_scatter_plot(res, dat)       # 散点图
mr_forest_plot(single)          # 森林图
mr_funnel_plot(single)         # 漏斗图
mr_leaveoneout_plot(loo)       # Leave-one-out 图
```

### MR-PRESSO 离群值检测
```r
library(MRPRESSO)
presso <- mr_presso(
    BetaOutcome = "beta.outcome",
    BetaExposure = "beta.exposure",
    SdOutcome = "se.outcome",
    SdExposure = "se.exposure",
    data = dat,
    OUTLIERtest = TRUE,
    DISTORTIONtest = TRUE,
    NbDistribution = 1000,
    SignifThreshold = 0.05
)
```

### 关键 QC 阈值

| 步骤 | 指标 | 阈值 | 说明 |
|------|------|------|------|
| 工具变量选择 | P value | < 5×10⁻⁸ | 全基因组显著性 |
| LD clumping | r² | < 0.001 | 独立 SNP |
| Clumping window | kb | 10,000 | 10 Mb 窗口 |
| F-statistic | F | > 10 | 强工具变量 |
| 回文 SNP | MAF | > 0.4 去除 | 避免链方向不确定 |
| 异质性 | Cochran's Q | P > 0.05 | 同质 |
| 水平多效性 | MR-Egger 截距 | P > 0.05 | 无显著多效性 |
| 因果方向 | Steiger | - | 暴露→结局方向正确 |

---

## 多基因风险评分 (Polygenic Risk Score, PRS)

### 核心场景
- 利用 GWAS summary statistics 预测个体遗传风险
- 适用于疾病风险分层、预后评估
- 需要 base data (GWAS) + target data (个体基因型)

### 标准分析流程

```
1. 准备数据
   ├─ Base data: GWAS summary statistics (β, SE, P, SNP, EA, OA)
   ├─ Target data: 个体基因型 (PLINK format)
   └→ 确保 base 和 target 使用相同参考基因组

2. 质量控制
   ├─ Base: 移除低质量 SNP (MAF < 0.01, INFO < 0.8)
   ├─ Target: 标准 GWAS QC (见上方 GWAS 部分)
   └→ 正链对齐 (base 和 target 的效应等位基因一致)

3. PRS 计算 (三种方法)
   ├─ Clumping + Thresholding (C+T) - PRSice-2
   ├─ Bayesian (连续收缩) - LDpred2, PRS-CS
   └→ LDpred2-autom / PRS-CS-auto (自动调参)

4. 模型评估
   ├─ R² (变异解释率)
   ├<arg_value> AUC / C-index (分类性能)
   └→ 十折交叉验证
```

### PRSice-2 标准命令
```bash
# PRSice-2 (C+T 方法)
Rscript PRSice.R \
    --prsice PRSice_linux \
    --base base_gwas.txt \
    --target target_data \
    --base-maf MAF \
    --base-info INFO \
    --base-A1 A1 \
    --base-A2 A2 \
    --base-bp BP \
    --base-chr CHR \
    --base-pvalue P \
    --base-effect BETA \
    --target-A1 A1 \
    --target-A2 A2 \
    --stat OR \
    --binary-target T \
    --pheno-file phenotype.txt \
    --pheno-col Phenotype \
    --cov-file covariates.txt \
    --cov-col PC1,PC2,PC3,PC4,PC5,Sex \
    --bar-levels 5e-8,1e-6,1e-4,1e-3,0.01,0.05,0.1,0.5,1 \
    --fastscore \
    --all-score \
    --out prs_results

# --bar-levels: 多个 P 阈值
# --fastscore: 只计算指定阈值 (不做全范围扫描)
# --all-score: 输出所有阈值的 PRS
```

### LDpred2 (Bayesian 方法, 推荐)
```r
library(bigsnpr)
library(data.table)

# Step 1: 读取 GWAS summary statistics
sumstats <- fread("base_gwas.txt")
sumstats <- sumstats[, .(chr, pos, rsid, ea, nea, beta, p)]

# Step 2: 与目标基因型对齐
snp_info <- snp_match(sumstats, map = bigsnpr::snp_attach("target_data.rds")$map)

# Step 3: LD 参考面板 (使用目标数据自身或参考面板)
LD <- snp_cor(G, ind.col = ind_chr, ncores = nb_cores())

# Step 4: LDpred2-auto (自动调参, 推荐)
beta_inf <- snp_ldpred2_inf(
    corr = LD,
    fbeta = snp_info$beta,
    fbeta_se = snp_info$beta_se
)

beta_auto <- snp_ldpred2_auto(
    corr = LD,
    fbeta = snp_info$beta,
    fbeta_se = snp_info$beta_se
)

# Step 5: 计算 PRS
prs <- big_prodVec(G, beta_auto[[1]]$beta_estim, ind.col = ind_chr)
```

### PRS-CS (Bayesian 连续收缩, 大样本推荐)
```bash
# PRS-CS (Python)
python PRS_cs.py \
    --ref_dir=/path/to/ld_reference \
    --bim_prefix=target_data \
    --sst_file=base_gwas.txt \
    --n_gwas=sample_size \
    --out_dir=output \
    --chrom=22

# PRS-CS-auto (自动调参)
python PRS_cs_auto.py \
    --ref_dir=/path/to/ld_reference \
    --bim_prefix=target_data \
    --sst_file=base_gwas.txt \
    --n_gwas=sample_size \
    --out_dir=output
```

### PRS 评估指标

| 指标 | 计算方法 | 解读 |
|------|---------|------|
| R² (连续表型) | 线性回归 PRS ~ 表型 | 解释方差比例 |
| Pseudo-R² (二分类) | Nagelkerke R² | 模型解释力 |
| AUC (二分类) | ROC 曲线下面积 | 分类性能 |
| OR per SD | PRS 每升高 1 SD 的 OR | 风险倍数 |
| 分层分析 | 最高 5%/10% vs 最低 | 风险分层效果 |

---

## 罕见变异分析 (Rare Variant Analysis)

### 核心场景
- 单个罕见变异（MAF < 1%）统计效力不足
- 基因聚合检验提高检测效力
- 适用于外显子组/全基因组测序数据

### 分析方法

| 方法 | 原理 | 适用场景 |
|------|------|---------|
| Burden test | 基因内所有罕见变异计数求和 | 变异方向一致 |
| SKAT | 平方和检验 (variance-component) | 变异方向不一致 |
| SKAT-O | Burden + SKAT 自适应混合 | 方向未知 |
| CMC | 混合模型组合 | 多频率分层 |
| ACAT | 从每个变异 P 值组合 | 超大样本 |

### SKAT 标准流程 (R)
```r
library(SKAT)

# 准备数据
# Z: 基因型矩阵 (n × m, 个体 × 变异)
# y: 表型向量
# X: 协变量矩阵
# obj: NULL model (仅协变量)

# Step 1: 拟合空模型
obj <- SKAT_Null_Model(
    y ~ PC1 + PC2 + PC3 + Age + Sex,
    out_type = "D"  # "D" 二分类, "C" 连续
)

# Step 2: Burden test
p_burden <- Burden(Z, obj, r.corr = 1)$p.value

# Step 3: SKAT (variance-component)
p_skat <- SKAT(Z, obj, r.corr = 0)$p.value

# Step 4: SKAT-O (自适应混合, 推荐)
p_skato <- SKAT(Z, obj, r.corr = NA)$p.value

# Step 5: 全基因组 (per-gene)
# 遍历所有基因, 输出 per-gene P value
for (gene in gene_list) {
    Z_gene <- extract_gene_genotypes(gene)
    p <- SKAT(Z_gene, obj, r.corr = NA)$p.value
    results <- rbind(results, data.frame(gene, p))
}

# 多重检验校正
results$q <- p.adjust(results$p, method = "BH")  # FDR
# 显著性: FDR q < 0.05
```

### 罕见变异 QC 阈值

| QC 步骤 | 指标 | 阈值 |
|---------|------|------|
| 变异质量 | QUAL | > 30 |
| 变异深度 | DP | > 10 |
| MAF 上限 | MAF | < 0.01 (1%) |
| 基因注释 | 功能影响 | missense, nonsense, splice-site |
| synonymous | 通常排除 | - |
| CADD | 预测有害性 | > 20 (推荐) |
| 多重检验 | FDR | q < 0.05 |

---

### GenotypeRefinement 在完整家系 WGS 流程中的精确位置

[由 Step 5 知识积累自动添加, 日期: 2026-07-29]

GenotypeRefinement 应插入在 **VQSR 过滤完成之后、队列 QC 之前**，是家系数据区别于普通队列分析的关键专属步骤。

`完整家系 WGS 流程:`
  FASTQ -> BWA -> MarkDuplicates -> BQSR -> HaplotypeCaller(-ERC GVCF)
  -> GenomicsDBImport -> GenotypeGVCFs
  -> bcftools norm (左对齐+拆分多等位)
  -> VariantRecalibrator (VQSR 训练)
  -> ApplyVQSR (链式: SNP 99.5% -> INDEL 99.0%)
  -> [此处插入 GenotypeRefinement]  <- 家系专属
  -> 队列 QC (基因型/位点/样本/家系孟德尔)
  -> 下游分析 (de novo / 共分离 / 注释)

**GenotypeRefinement 三步详细说明：**

| 步骤 | 工具 | 作用 | 输入 | 输出 |
|------|------|------|------|------|
| 1. 基因型后验优化 | CalculateGenotypePosteriors | 结合家系 pedigree + 人群 AF（gnomAD）优化低质量基因型 | VQSR 过滤后 VCF + .ped + gnomAD | 加了 PP/GP 字段的 VCF |
| 2. 传递相位 | PhaseByTransmission | 利用 pedigree 推断父母->子传递的等位基因，修正相位 | 上一步输出 + .ped | 加了 PQ 字段的 phased VCF |
| 3. de novo 标注 | VariantAnnotator + VariantFiltration | 标注 de novo 候选（子杂合+父母均参考型） | phased VCF + gnomAD | de novo 候选 VCF |

**关键注意事项：**
- `CalculateGenotypePosteriors` 的 `--supporting-callsets` 推荐使用 gnomAD（需与参考基因组版本匹配）
- `.ped` 文件格式：FamilyID IndividualID FatherID MotherID Sex Phenotype（0=未知）
- 该步骤能显著提高低覆盖度区域（<20x）的基因型准确率
- 如果队列中家系成员不完整（单亲），PhaseByTransmission 仍可工作但效力降低

### VQSR 链式应用 vs 并行应用

[由 Step 5 知识积累自动添加, 日期: 2026-07-29]

GATK ApplyVQSR 有两种应用策略，对家系 WGS 队列有重要影响：

| 策略 | 方法 | SNP 模型输入 | INDEL 模型输入 | GATK 推荐 | 适用场景 |
|------|------|------------|--------------|----------|---------|
| 链式（顺序） | 先 SNP 过滤，再用过滤后 VCF 过滤 INDEL | 原始 VCF | SNP 过滤后 VCF | YES 官方推荐 | 标准分析 |
| 并行（独立） | SNP 和 INDEL 各自从原始 VCF 独立过滤 | 原始 VCF | 原始 VCF | 非推荐 | 需要分离输出时 |

**链式应用（推荐）代码模式：**
```bash
# Step 1: 先对原始 VCF 应用 SNP VQSR
gatk ApplyVQSR \
    -V input_norm.vcf.gz \
    -O tmp_snp_recal.vcf.gz \
    --recal-file global_snps.recal \
    --tranches-file global_snps.tranches \
    -mode SNP \
    --truth-sensitivity-filter-level 99.5

# Step 2: 对 SNP 过滤后的 VCF 继续应用 INDEL VQSR
gatk ApplyVQSR \
    -V tmp_snp_recal.vcf.gz \
    -O final_PASS.vcf.gz \
    --recal-file global_indels.recal \
    --tranches-file global_indels.tranches \
    -mode INDEL \
    --truth-sensitivity-filter-level 99.0
```

**为什么推荐链式：** INDEL 模型的训练和过滤基于 SNP 质量已优化的 VCF，避免低质量 SNP 干扰 INDEL 判定。GATK 官方文档明确推荐链式应用。

**如果下游需要分离的 SNP/INDEL 文件：** 在链式 ApplyVQSR 完成后，用 bcftools 拆分即可，无需用并行策略：
```bash
bcftools view -v snps -f PASS final_PASS.vcf.gz -Oz -o pure_snps.vcf.gz
bcftools view -v indels -f PASS final_PASS.vcf.gz -Oz -o pure_indels.vcf.gz
```

---
## 研究设计流程图坐标参考

家系分析 (Trio) 步骤坐标（position.y 递增 120）：

| 步骤 | y 坐标 |
|------|--------|
| 变异检测 | 0 |
| 联合基因分型 | 120 |
| VQSR/硬过滤 | 240 |
| GenotypeRefinement | 360 |
| 变异注释 | 480 |
| De novo 识别 | 600 |
| 验证排序 | 720 |

GWAS 步骤坐标：

| 步骤 | y 坐标 |
|------|--------|
| 基因型 QC | 0 |
| 群体分层校正 | 120 |
| 关联分析 | 240 |
| 结果解读 | 360 |

MR 步骤坐标：

| 步骤 | y 坐标 |
|------|--------|
| 选择工具变量 | 0 |
| 提取结局 SNP | 120 |
| MR 估计 | 240 |
| 敏感性分析 | 360 |
| 多变量 MR (可选) | 480 |

PRS 步骤坐标：

| 步骤 | y 坐标 |
|------|--------|
| 准备数据 | 0 |
| 质量控制 | 120 |
| PRS 计算 | 240 |
| 模型评估 | 360 |

---

## 结构变异检测 (Structural Variant Calling - Manta)

[由 Step 5 知识积累自动添加, 日期: 2026-07-29]

### 核心场景
- 种系 SV 检测：缺失、插入、倒位、串联重复、染色体间易位
- 家系规模的小群体联合分析（<=10 样本）
- 兼顾体细胞 SV（Tumor/Normal 对）

### Manta 官方流程

Manta 由 Illumina 开发，是种系 SV 检测的主流工具之一 [](https://github.com/Illumina/manta)。最新版本 v1.6.0，仓库状态为 Public Archive（功能稳定，不再活跃开发）。

Manta 将 SV 检测分为两步：(1) 扫描基因组发现 SV 关联区域，构建 breakend 关联图；(2) 分析图边发现、组装、评分和过滤 SV [](https://github.com/Illumina/manta/blob/master/docs/userGuide/README.md)。

### 流程步骤

| # | 步骤 | 工具 (版本) | 输入 -> 输出 | 备注 |
|---|------|------------|------------|------|
| 1 | 配置 | configManta.py (1.6.0) | BAM + REF -> workflow.py | 生成运行脚本 |
| 2 | SV 检测 | run workflow.py (1.6.0) | workflow.py -> diploidSV.vcf.gz | 含 paired+split-read 证据 |
| 3 | PASS 过滤 | bcftools view -f PASS (1.16+) | diploidSV.vcf.gz -> filteredSV.vcf.gz | 提取高置信变异 |
| 4 | 索引 | tabix -p vcf (1.16+) | filteredSV.vcf.gz -> .tbi | 下游查询必备 |

### Manta 输出文件说明

| 文件 | 内容 | 适用场景 |
|------|------|---------|
| diploidSV.vcf.gz | 二倍体模型评分的 SV 和 indel | 种系分析（主要输出） |
| candidateSV.vcf.gz | 未评分的 SV 候选（最低证据阈值） | 高灵敏度筛选 |
| candidateSmallIndels.vcf.gz | <50bp 的小 indel 候选 | 传递给小变异检测器 |
| somaticSV.vcf.gz | 体细胞模型评分的 SV | 仅 Tumor/Normal 分析 |

### 可检测的 SV 类型

- 缺失 (Deletions)
- 插入 (Insertions) - 含完全组装和部分组装
- 倒位 (Inversions)
- 串联重复 (Tandem Duplications)
- 染色体间易位 (Interchromosomal Translocations)

### 已知局限
- 无法检测分散重复 (Dispersed duplications)
- 无法检测大多数串联重复的扩张/收缩
- 小倒位检测能力有限（<200bp 衰减）
- 完全组装的大插入受片段大小限制

### 关键参数
- 最小 SV 评分大小：默认 50bp（<50bp 传递给小变异检测器）
- 最小 indel 报告大小：默认 8bp
- 输入要求：坐标排序 + 索引的 BAM/CRAM，配对端测序
- GRCh38 参考：建议排除短 contig 加速运行

### 运行时间
- NA12878 50x WGS：<20 分钟（20 核服务器）
- Tumor/Normal 分析：<2 小时

### 参考文献
- Chen, X. et al. (2016) Manta: rapid detection of structural variants and indels for germline and cancer sequencing applications. Bioinformatics, 32, 1220-1222. doi:10.1093/bioinformatics/btv710

---

## 种系 CNV 检测 (GATK gCNV)

[由 Step 5 知识积累自动添加, 日期: 2026-07-29]

### 核心场景
- 全基因组种系 CNV 检测（WGS 1000bp 窗口）
- 队列联合建模（cohort 模式）
- 基于 read depth 的拷贝数变异分析

### GATK gCNV 官方流程

GATK gCNV (GermlineCNVCaller) 是 Broad Institute 开发的种系 CNV 检测工具，使用贝叶斯模型从 read depth 推断拷贝数变异。

### 流程步骤

| # | 步骤 | 工具 | 输入 -> 输出 | 备注 |
|---|------|------|------------|------|
| 1 | CRAM 解码+过滤 | samtools view -F 2308 -q 20 | CRAM -> clean BAM | 去除低质量 reads |
| 2 | Read 深度计数 | CollectReadCounts | BAM -> counts.tsv | 1000bp 窗口，TSV 格式 |
| 3 | 区间 GC 注释 | AnnotateIntervals | interval_list -> annotated.tsv | GC 含量注释 |
| 4 | 区间质控过滤 | FilterIntervals | annotated.tsv + counts -> filtered.interval_list | 过滤低质量和极端区间 |
| 5 | 染色体倍性建模 | DetermineGermlineContigPloidy | counts + priors -> ploidy-calls | 推断每条染色体倍性 |
| 6 | CNV 变异分析 | GermlineCNVCaller (COHORT) | counts + ploidy -> cohort-calls/model | 贝叶斯模型，可分片并行 |
| 7 | 后处理聚合 | PostprocessGermlineCNVCalls | model + calls -> segments.vcf + intervals.vcf + ratios.tsv | 跨分片聚合，输出单样本 VCF |
| 8 | 质量硬过滤 | bcftools filter | segments.vcf -> filtered.vcf | QS>=30, NP>=3, CN!=2 |
| 9 | 队列合并 | bcftools merge | filtered.vcf x N -> cohort.vcf | 合并多样本矩阵 |
| 10 | 注释 | AnnotSV | cohort.vcf -> annotated.tsv | SV 功能注释 |

### 关键参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 窗口大小 | 1000bp (WGS) | PreprocessIntervals --bin-length |
| 最低 mapping quality | 20 | CollectReadCounts --minimum-mapping-quality |
| low-count 过滤 | 90% 样本 | FilterIntervals --low-count-filter-percentage-of-samples |
| extreme-count 过滤 | 90% 样本 | FilterIntervals --extreme-count-filter-percentage-of-samples |
| coherence length | 1000.0 | GermlineCNVCaller --cnv-coherence-length |
| 分片大小 | 40000 区间/片 | IntervalListTools --SCATTER_CONTENT |
| QS 阈值 | >= 30 | bcftools filter FMT/QS |
| NP 阈值 | >= 3 | bcftools filter FMT/NP |

### QC 验收
- counts.tsv 行数应一致（全基因组 1000bp 约 295 万行）
- 所有样本的 segments.vcf.gz 均需生成
- 过滤后 CN!=2 的区间为候选 CNV
- AnnotSV 注释后可按 ACMG 指南评估致病性

### 分片策略
- 使用 IntervalListTools 将主染色体（chr1-22, X, Y）区间分为约 69 个分片
- 每个分片独立运行 GermlineCNVCaller
- PostprocessGermlineCNVCalls 一次性传入所有分片模型进行跨分片聚合
