# 预设搜索策略

本文档列出 Step 2a 中已覆盖流程的官方文档 URL 及搜索策略。

## 核心原则

已知官方文档 URL 的工具，优先使用 WebFetch 直接抓取官方页面，WebSearch 仅作为补充手段（用于工具对比、版本搜索、QC 阈值等无固定官方页面的信息）。

## DNA 变异检测

- WebFetch: `https://gatk.broadinstitute.org/hc/en-us/articles/360035531212` → GATK Germline SNPs/Indels 最佳实践
- WebFetch: `https://gatk.broadinstitute.org/hc/en-us/articles/360035894711` → GATK Somatic (Mutect2) 最佳实践
- WebFetch: `https://nf-co.re/sarek/latest` → nf-core/sarek 流程文档（步骤、参数、输出）
- WebFetch: `https://github.com/broadinstitute/gatk` → GATK GitHub（最新版本、release notes）

## RNA 分析

- WebFetch: `https://nf-co.re/rnaseq/latest` → nf-core/rnaseq 流程文档
- WebFetch: `https://nf-co.re/scrnaseq/latest` → nf-core/scrnaseq 流程文档
- WebFetch: `https://www.encodeproject.org/rna-seq/` → ENCODE RNA-seq 标准
- WebFetch: `https://bioconductor.org/books/release/OSCA/` → Bioconductor OSCA 单细胞分析教程

## 表观遗传

- WebFetch: `https://www.encodeproject.org/atac-seq/` → ENCODE ATAC-seq 标准
- WebFetch: `https://www.encodeproject.org/chip-seq/` → ENCODE ChIP-seq 标准
- WebFetch: `https://nf-co.re/chipseq/latest` → nf-core/chipseq 流程文档
- WebFetch: `https://nf-co.re/atacseq/latest` → nf-core/atacseq 流程文档
- WebFetch: `https://nf-co.re/methylseq/latest` → nf-core/methylseq 流程文档

## 微生物组

- WebFetch: `https://docs.qiime2.org/` → QIIME2 官方文档（16S/宏基因组）
- WebFetch: `https://nf-co.re/ampliseq/latest` → nf-core/ampliseq 流程文档
- WebFetch: `https://nf-co.re/mag/latest` → nf-core/mag 流程文档
- WebFetch: `https://huttenhower.sph.harvard.edu/humann` → HUMAnN 官方文档

## 研究设计（家系/GWAS/MR/PRS）

- WebFetch: `https://gatk.broadinstitute.org/hc/en-us/articles/360035531212` → GATK GenotypeRefinement（家系/Trio）
- WebFetch: `https://www.cog-genomics.org/plink/2.0/` → PLINK 2.0 官方文档（GWAS QC、关联分析）
- WebFetch: `https://github.com/weizhouUMN/SAIGE` → SAIGE 官方文档（大样本 GWAS）
- WebFetch: `https://rgcgithub.github.io/regenie/` → REGENIE 官方文档（两步法 GWAS）
- WebFetch: `https://mrcieu.github.io/TwoSampleMR/` → TwoSampleMR 官方教程（孟德尔随机化）
- WebFetch: `https://choishingwan.github.io/PRSice/` → PRSice-2 官方教程（PRS 计算）
- WebFetch: `https://privefl.github.io/bigsnpr/articles/LDpred2.html` → LDpred2 官方教程（PRS）
- WebFetch: `https://github.com/szhan/SKAT` → SKAT 官方文档（罕见变异聚合检验）

## 变异注释（ANNOVAR/VEP/SnpEff/AnnotSV）

- WebFetch: `https://annovar.openbioinformatics.org/en/latest/user-guide/download/` → ANNOVAR 最新数据库版本列表
- WebFetch: `https://annovar.openbioinformatics.org/en/latest/user-guide/startup/` → ANNOVAR 官方使用教程
- WebFetch: `https://raw.githubusercontent.com/lgmgeo/AnnotSV/master/commandLineOptions.txt` → AnnotSV 完整命令行参数（raw URL，可直取）
- WebFetch: `https://github.com/lgmgeo/AnnotSV` → AnnotSV 版本信息（README 摘要，非完整文档）
- WebFetch: `https://www.ensembl.org/info/docs/tools/vep/index.html` → VEP (Ensembl) 官方文档
- WebFetch: `https://pcingola.github.io/SnpEff/` → SnpEff 官方文档
- WebSearch 补充: `"AnnotSV manual" OR "README.AnnotSV" PDF` → AnnotSV 完整手册（PDF 无法 WebFetch 直取）
- WebSearch 补充: `"ANNOVAR" database download hg38 gnomad clinvar dbnsfp` → 数据库版本搜索
- WebSearch 补充: `"ANNOVAR vs VEP vs SnpEff" comparison` → 工具对比

## 通用原则

1. 官方文档 URL 已知 → **必须先 WebFetch**
2. WebSearch 仅在以下场景使用：无固定官方页面（QC 阈值、社区经验、版本更新动态）、工具对比、WebFetch 失败后的回退补充
3. WebFetch 失败时（404 / Cloudflare / JS 渲染），不重试，直接切换关键词走 WebSearch
4. 每次搜索后，如果发现了新的官方 URL，按 Step 5 知识积累规则回写到本文件中
5. GitHub README 作为路由跳板：先 WebFetch 获取文档站链接（Read the Docs、GitHub Pages、项目官网等），再按链接二次 WebFetch 真正的文档；若 README 中无文档链接，回退到 WebSearch
