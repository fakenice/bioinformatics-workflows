/**
 * Build-time pipeline JSON generator.
 * Parses references/study_designs.md to generate pipeline JSONs
 * for the 5 study-design pipelines (family-trio, gwas, MR, PRS, rare-variant).
 *
 * Run: npx tsx scripts/build-pipelines.ts
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");
const DATA_DIR = resolve(ROOT, "src/data/pipelines");
const STUDY_DESIGNS_PATH = resolve(ROOT, "references/study_designs.md");
const SKILL_MD_PATH = resolve(ROOT, "SKILL.md");

interface ToolInfo {
  name: string;
  version: string;
  params: string;
  docker: string;
  notes?: string;
  notesEn?: string;
}

interface PipelineStep {
  id: string;
  name: string;
  nameEn?: string;
  description: string;
  descriptionEn?: string;
  tools: ToolInfo[];
  notes: string;
  notesEn?: string;
  position: { x: number; y: number };
}

interface Reference {
  title: string;
  url: string;
  type: "official" | "community" | "paper";
}

interface PipelineSource {
  id: string;
  name: string;
  nameEn?: string;
  type: "official" | "community" | "paper";
  url: string;
  steps: PipelineStep[];
  references: Reference[];
}

interface ChangelogEntry {
  version: string;
  date: string;
  changes: string[];
}

interface PipelineDefinition {
  id: string;
  name: string;
  nameZH: string;
  category: "dna" | "rna" | "epigenetics" | "microbiome";
  tags: string[];
  overview: string;
  overviewEn?: string;
  icon: string;
  version?: string;
  changelog?: ChangelogEntry[];
  sources: PipelineSource[];
}

// ─── Pipeline definitions ────────────────────────────────────────────

interface PipelineTemplate {
  id: string;
  name: string;
  nameZH: string;
  category: "dna" | "rna" | "epigenetics" | "microbiome";
  tags: string[];
  overview: string;
  overviewEn?: string;
  icon: string;
  version: string;
  sources: {
    id: string;
    name: string;
    nameEn?: string;
    type: "official" | "community" | "paper";
    url: string;
    stepNames: string[];
    stepNamesEn?: string[];
    stepDescs: string[];
    stepDescsEn?: string[];
    toolRows: ToolRow[];
    references: Reference[];
  }[];
}

interface ToolRow {
  stepIndex: number;
  name: string;
  version: string;
  docker: string;
  params: string;
  notes: string;
  notesEn?: string;
}

const PIPELINES: PipelineTemplate[] = [
  {
    id: "family-trio-wgs",
    name: "Family Trio WGS Germline",
    nameZH: "家系WGS种系变异分析",
    category: "dna",
    tags: ["家系分析", "Trio", "GATK", "de novo", "遗传病"],
    version: "1.0.0",
    overview:
      "适用于父母-子代 Trio 家系的全基因组种系变异联合检测。基于 GATK Best Practices (v4.5) 与 nf-core/sarek (v3.9)，覆盖 FASTQ→VCF 全链路，包含联合分型、de novo 检出、遗传模式筛选。",
    icon: "dna",
    sources: [
      {
        id: "gatk",
        name: "GATK Best Practices",
        type: "official",
        url: "https://gatk.broadinstitute.org/hc/en-us/articles/360035535932",
        stepNames: [
          "比对 (BWA-MEM2)",
          "标记重复 + BQSR",
          "单样本 GVCF",
          "GVCF 整合",
          "联合基因分型",
          "VQSR 过滤 / Hard-Filtering",
          "De Novo 检测",
          "家系遗传模式筛选",
          "变异注释 + QC 报告",
        ],
        stepDescs: [
          "将 Clean Reads 比对到 hg38 参考基因组",
          "标记 PCR 重复并对碱基质量进行重校准",
          "HaplotypeCaller GVCF 模式，每个样本独立生成",
          "将 3 个 GVCF 导入 GenomicsDB 数据库",
          "基于 GenomicsDB 进行家系联合分型",
          "分别对 SNP 和 Indel 进行 VQSR 质量重校准；小样本备选硬过滤",
          "基于 PED 家系文件识别新发变异",
          "按 AD/AR/X-linked 等遗传模式 + 表型过滤候选基因",
          "功能注释 + MultiQC 汇总",
        ],
        toolRows: [
          { stepIndex: 0, name: "BWA-MEM2", version: "2.2", params: "-M -R @RG\\tID:sample\\tSM:sample\\tPL:ILLUMINA", docker: "biocontainers/bwa-mem2:2.2.1", notes: "BWA-MEM2 比 BWA-MEM 快约 2×。也可选 DragMap 提速 3-5×。" },
          { stepIndex: 1, name: "GATK MarkDuplicates", version: "4.5", params: "", docker: "broadinstitute/gatk:4.5.0.0", notes: "BQSR 基于 dbSNP/1000G/Mills 等已知位点集。家系分析中不推荐完全移除重复，仅标记即可。" },
          { stepIndex: 1, name: "GATK BaseRecalibrator", version: "4.5", params: "--known-sites dbsnp.vcf", docker: "broadinstitute/gatk:4.5.0.0", notes: "" },
          { stepIndex: 1, name: "GATK ApplyBQSR", version: "4.5", params: "", docker: "broadinstitute/gatk:4.5.0.0", notes: "" },
          { stepIndex: 2, name: "GATK HaplotypeCaller", version: "4.5", params: "-ERC GVCF --native-pair-hmm-threads 8", docker: "broadinstitute/gatk:4.5.0.0", notes: "GVCF 模式便于后续增量联合 calling。Trio 中 3 个样本完全并行。" },
          { stepIndex: 3, name: "GATK GenomicsDBImport", version: "4.5", params: "--genomicsdb-workspace-path gendb --intervals chr.list", docker: "broadinstitute/gatk:4.5.0.0", notes: "按染色体区间并行导入。3 个样本的 Trio 直接全基因组导入即可。" },
          { stepIndex: 4, name: "GATK GenotypeGVCFs", version: "4.5", params: "--include-non-variant-sites", docker: "broadinstitute/gatk:4.5.0.0", notes: "联合分型可利用群体信息提高稀有变异敏感性，并输出一致的基因型矩阵。对 Trio 设计增益明显。" },
          { stepIndex: 5, name: "GATK VariantRecalibrator", version: "4.5", params: "-mode SNP --max-gaussians 4", docker: "broadinstitute/gatk:4.5.0.0", notes: "⚠ VQSR 至少需要 30 样本才稳健。Trio 小样本建议 Hard-Filtering：QD<2.0, FS>60, MQ<40, SOR>3.0。" },
          { stepIndex: 5, name: "GATK ApplyVQSR", version: "4.5", params: "--truth-sensitivity-filter-level 99.7", docker: "broadinstitute/gatk:4.5.0.0", notes: "" },
          { stepIndex: 5, name: "GATK VariantFiltration", version: "4.5", params: "--filter-expression \"QD<2.0||FS>60||MQ<40\"", docker: "broadinstitute/gatk:4.5.0.0", notes: "" },
          { stepIndex: 6, name: "GATK PossibleDeNovo", version: "4.5", params: "--ped family.ped --max-parent-af 0.001", docker: "broadinstitute/gatk:4.5.0.0", notes: "筛选仅先证者存在、父母为参考纯合的变异。结合 gnomAD MAF<0.01 及功能注释进一步缩窄候选。" },
          { stepIndex: 7, name: "slivar", version: "0.3", params: "--ped family.ped --trio --gnomad-max-af 0.01 --impactful", docker: "brentp/slivar:0.3", notes: "slivar 一站式支持 de novo、compound het、AR homozygous、AD inherited 等模式。结合表型 HPO 词条效果更佳。" },
          { stepIndex: 7, name: "GATK SelectVariants", version: "4.5", params: "--select-type-to-include SNP", docker: "broadinstitute/gatk:4.5.0.0", notes: "" },
          { stepIndex: 8, name: "Ensembl VEP", version: "112", params: "--everything --fork 8 --pick", docker: "ensemblorg/ensembl-vep:112", notes: "VEP 输出含 gnomAD AF、ClinVar 临床意义、CADD/SIFT/PolyPhen 预测分数。MultiQC 汇总覆盖度、Ti/Tv、比对率等。" },
          { stepIndex: 8, name: "MultiQC", version: "1.21", params: "", docker: "multiqc/multiqc:1.21", notes: "" },
        ],
        references: [
          { title: "GATK Best Practices - Germline short variant discovery (2024)", url: "https://gatk.broadinstitute.org/hc/en-us/articles/360035535932", type: "official" },
          { title: "GATK - The logic of joint calling for germline short variants (2024)", url: "https://gatk.broadinstitute.org/hc/en-us/articles/360035890431", type: "official" },
          { title: "BWA-MEM2: faster alignment (Vasimuddin et al., 2019)", url: "https://doi.org/10.1109/IPDPS.2019.00041", type: "paper" },
          { title: "slivar: rapid population-scale trio analysis (Pedersen et al.)", url: "https://github.com/brentp/slivar", type: "community" },
        ],
      },
      {
        id: "nfcore",
        name: "nf-core/sarek",
        type: "community",
        url: "https://nf-co.re/sarek/3.9",
        stepNames: [
          "质控 + 修剪",
          "比对 + 去重",
          "BQSR (可选)",
          "变异检测",
          "注释 + MultiQC 报告",
        ],
        stepDescs: [
          "FastQC + fastp 一体化 QC",
          "BWA-MEM2 / DragMap 比对并 MarkDuplicates",
          "碱基质量重校准，可通过 --no_bqsr 跳过",
          "HaplotypeCaller / DeepVariant / Strelka2 多工具可选",
          "snpEff/VEP 注释 + 全流程 QC 汇总",
        ],
        toolRows: [
          { stepIndex: 0, name: "FastQC", version: "0.12.1", params: "", docker: "nfcore/sarek:3.9", notes: "fastp 一步完成质控、接头去除、质量裁剪，效率高于 Trim Galore。" },
          { stepIndex: 0, name: "fastp", version: "0.23.4", params: "--qualified_quality_phred 20", docker: "nfcore/sarek:3.9", notes: "" },
          { stepIndex: 1, name: "BWA-MEM2 / DragMap / Sentieon", version: "—", params: "", docker: "nfcore/sarek:3.9", notes: "三选一。DragMap 速度最快（DRAGEN 算法），Sentieon 商用精度最高。" },
          { stepIndex: 1, name: "GATK MarkDuplicates", version: "4.5", params: "", docker: "nfcore/sarek:3.9", notes: "" },
          { stepIndex: 2, name: "GATK BaseRecalibrator + ApplyBQSR", version: "4.5", params: "", docker: "nfcore/sarek:3.9", notes: "现代测序平台此步收益递减，但临床级分析仍推荐保留。" },
          { stepIndex: 3, name: "GATK HaplotypeCaller", version: "4.5", params: "", docker: "nfcore/sarek:3.9", notes: "DeepVariant 基于 CNN，对 Indel 灵敏度最高。可多工具并行取交集提升准确性。" },
          { stepIndex: 3, name: "DeepVariant", version: "1.6", params: "", docker: "nfcore/sarek:3.9", notes: "" },
          { stepIndex: 3, name: "Strelka2", version: "2.9", params: "", docker: "nfcore/sarek:3.9", notes: "" },
          { stepIndex: 4, name: "snpEff / VEP", version: "5.1 / 112", params: "", docker: "nfcore/sarek:3.9", notes: "snpEff 比 VEP 轻量。自动产出 MultiQC HTML 报告，含覆盖度、GC bias、insert size 等。" },
          { stepIndex: 4, name: "MultiQC", version: "1.21", params: "", docker: "nfcore/sarek:3.9", notes: "" },
        ],
        references: [
          { title: "nf-core/sarek v3.9 Documentation", url: "https://nf-co.re/sarek/latest", type: "official" },
          { title: "Hanssen et al. (2024) NAR Genomics and Bioinformatics 6(2):lqae031", url: "https://doi.org/10.1093/nargab/lqae031", type: "paper" },
          { title: "nf-core: community curated bioinformatics pipelines (Ewels et al., 2020)", url: "https://doi.org/10.1038/s41587-020-0439-x", type: "paper" },
          { title: "DeepVariant: A Universal SNP and Indel Variant Caller (Poplin et al., 2018)", url: "https://doi.org/10.1038/nbt.4235", type: "paper" },
        ],
      },
    ],
  },
  {
    id: "gwas",
    name: "GWAS Case-Control",
    nameZH: "病例对照 GWAS 分析",
    category: "dna",
    tags: ["GWAS", "病例对照", "SAIGE", "REGENIE", "PLINK", "群体遗传"],
    version: "1.0.0",
    overview:
      "全基因组关联分析标准流程，覆盖基因型 QC、群体分层校正、关联分析（PLINK/SAIGE/REGENIE）和结果解读。适用于常见变异（MAF > 1%）与二分类/连续表型的关联检测。",
    overviewEn:
      "Standard GWAS pipeline covering genotype QC, population stratification correction, association testing (PLINK/SAIGE/REGENIE), and result interpretation. Suitable for common variants (MAF > 1%) with binary or continuous traits.",
    icon: "dna",
    sources: [
      {
        id: "plink",
        name: "PLINK GWAS",
        nameEn: "PLINK GWAS",
        type: "official",
        url: "https://www.cog-genomics.org/plink/",
        stepNames: [
          "基因型数据 QC",
          "群体分层校正",
          "关联分析",
          "结果解读",
        ],
        stepNamesEn: [
          "Genotype QC",
          "Population Stratification",
          "Association Testing",
          "Result Interpretation",
        ],
        stepDescs: [
          "样本 QC（缺失率、性别检查、杂合度、亲缘关系）+ 变异 QC（缺失率、MAF、HWE、差异缺失）",
          "PCA 主成分分析，去除异常样本，PC1-PC10 作为协变量",
          "二分类表型用逻辑回归（PLINK --logistic / SAIGE / REGENIE），连续表型用线性回归（PLINK --linear / BOLT-LMM）",
          "Manhattan plot, QQ plot, 基因组膨胀因子 λ_GC, LD clumping + 注释",
        ],
        stepDescsEn: [
          "Sample QC (missingness, sex check, heterozygosity, relatedness) + Variant QC (missingness, MAF, HWE, differential missingness)",
          "PCA principal component analysis, remove outliers, use PC1-PC10 as covariates",
          "Binary traits: logistic regression (PLINK --logistic / SAIGE / REGENIE); Continuous traits: linear regression (PLINK --linear / BOLT-LMM)",
          "Manhattan plot, QQ plot, genomic inflation λ_GC, LD clumping + annotation",
        ],
        toolRows: [
          { stepIndex: 0, name: "PLINK", version: "1.9 / 2.0", params: "--mind 0.03 --geno 0.02 --maf 0.01 --hwe 1e-6", docker: "", notes: "样本缺失率 < 3%，变异缺失率 < 2%，MAF > 1%，HWE P > 1e-6。", notesEn: "Sample missingness < 3%, variant missingness < 2%, MAF > 1%, HWE P > 1e-6." },
          { stepIndex: 0, name: "PLINK --king", version: "2.0", params: "--king-cutoff 0.0884", docker: "", notes: "移除二级以上亲属（PI_HAT < 0.0884）。", notesEn: "Remove 2nd-degree or closer relatives (PI_HAT < 0.0884)." },
          { stepIndex: 1, name: "GCTA / PLINK 2.0", version: "1.94 / 2.0", params: "--pca 20", docker: "", notes: "PCA 计算前 20 个主成分。检查 PC1 vs PC2 是否有群体异常样本。", notesEn: "Compute top 20 PCs. Inspect PC1 vs PC2 for population outliers." },
          { stepIndex: 2, name: "PLINK --logistic", version: "1.9", params: "--covar PC1-PC5 --ci 0.95", docker: "", notes: "基础逻辑回归，适合中小样本。", notesEn: "Basic logistic regression, suitable for small-to-medium samples." },
          { stepIndex: 2, name: "SAIGE", version: "1.3+", params: "step1: fitNULLGLMM, step2: SPAtests", docker: "", notes: "推荐用于大样本 + 病例不平衡。使用 SPA 校正。", notesEn: "Recommended for large samples + case imbalance. Uses SPA correction." },
          { stepIndex: 2, name: "REGENIE", version: "3.4+", params: "--step 1 --step 2 --bt", docker: "", notes: "两步法，适合 UKB 级别大数据。低内存模式。", notesEn: "Two-step method, suitable for UKB-scale data. Low-memory mode." },
          { stepIndex: 3, name: "LDSC / GCTA", version: "1.0.1 / 1.94", params: "", docker: "", notes: "计算 λ_GC（目标 0.95-1.05）。Manhattan/QQ 图用 R qqman 包。", notesEn: "Compute λ_GC (target 0.95-1.05). Manhattan/QQ plots via R qqman package." },
        ],
        references: [
          { title: "PLINK 1.9 / 2.0 Documentation", url: "https://www.cog-genomics.org/plink/", type: "official" },
          { title: "SAIGE: Scalable and accurate generalized mixed model (Zhou et al., 2018)", url: "https://doi.org/10.1038/s41588-018-0184-6", type: "paper" },
          { title: "REGENIE: whole-genome regression (Mbatchou et al., 2021)", url: "https://doi.org/10.1038/s41588-021-00870-7", type: "paper" },
          { title: "BOLT-LMM: Bayesian mixed model (Loh et al., 2015)", url: "https://doi.org/10.1038/ng.3190", type: "paper" },
        ],
      },
    ],
  },
  {
    id: "mendelian-randomization",
    name: "Mendelian Randomization",
    nameZH: "孟德尔随机化分析",
    category: "dna",
    tags: ["孟德尔随机化", "MR", "TwoSampleMR", "工具变量", "因果推断"],
    version: "1.0.0",
    overview:
      "利用遗传变异作为工具变量评估暴露与结局的因果关系。支持双样本 MR（使用 GWAS summary statistics），覆盖 IV 选择、harmonization、多方法 MR 估计和敏感性分析。",
    overviewEn:
      "Uses genetic variants as instrumental variables to assess causal relationships between exposures and outcomes. Supports two-sample MR (using GWAS summary statistics), covering IV selection, harmonization, multi-method MR estimation, and sensitivity analysis.",
    icon: "dna",
    sources: [
      {
        id: "twosamplemr",
        name: "TwoSampleMR (MRC IEU)",
        nameEn: "TwoSampleMR (MRC IEU)",
        type: "official",
        url: "https://mrcieu.github.io/TwoSampleMR/",
        stepNames: [
          "选择工具变量",
          "提取结局 SNP + Harmonization",
          "MR 估计",
          "敏感性分析",
          "多变量 MR (可选)",
        ],
        stepNamesEn: [
          "Select Instrumental Variables",
          "Extract Outcome SNPs + Harmonization",
          "MR Estimation",
          "Sensitivity Analysis",
          "Multivariable MR (optional)",
        ],
        stepDescs: [
          "从暴露 GWAS 选 IV（P < 5e-8），Clumping（r² < 0.001, 10Mb），检查 F-statistic > 10",
          "提取结局 GWAS 对应 SNP，正链对齐，去除回文 SNP（MAF > 0.4）",
          "IVW（主方法）、MR-Egger、加权中位数、加权模式、最多似然法",
          "Cochran's Q 异质性、MR-Egger 截距多效性、Leave-one-out、MR-PRESSO 离群值、Steiger 因果方向",
          "控制混杂暴露，评估独立因果效应",
        ],
        stepDescsEn: [
          "Select IVs from exposure GWAS (P < 5e-8), clumping (r² < 0.001, 10Mb), check F-statistic > 10",
          "Extract corresponding SNPs from outcome GWAS, align to forward strand, remove palindromic SNPs (MAF > 0.4)",
          "IVW (primary), MR-Egger, weighted median, weighted mode, maximum likelihood",
          "Cochran's Q heterogeneity, MR-Egger intercept pleiotropy, leave-one-out, MR-PRESSO outliers, Steiger directionality",
          "Control for confounding exposures, assess independent causal effects",
        ],
        toolRows: [
          { stepIndex: 0, name: "TwoSampleMR R 包", version: "0.6+", params: "extract_instruments(p1=5e-8, clump=T, r2=0.001, kb=10000)", docker: "", notes: "F-statistic = beta²/se²，要求 F > 10。", notesEn: "F-statistic = beta²/se²; threshold F > 10." },
          { stepIndex: 1, name: "TwoSampleMR harmonise_data()", version: "0.6+", params: "action=2", docker: "", notes: "action=2 去除回文 SNP（MAF > 0.4）。", notesEn: "action=2 removes palindromic SNPs (MAF > 0.4)." },
          { stepIndex: 2, name: "TwoSampleMR mr()", version: "0.6+", params: "method_list=c('mr_ivw','mr_egger_regression','mr_weighted_median')", docker: "", notes: "IVW 为主方法。MR-Egger 检验水平多效性。", notesEn: "IVW is the primary method. MR-Egger tests for horizontal pleiotropy." },
          { stepIndex: 3, name: "TwoSampleMR mr_heterogeneity()", version: "0.6+", params: "", docker: "", notes: "Cochran's Q P < 0.05 表示异质性。", notesEn: "Cochran's Q P < 0.05 indicates heterogeneity." },
          { stepIndex: 3, name: "TwoSampleMR mr_pleiotropy_test()", version: "0.6+", params: "", docker: "", notes: "MR-Egger 截距 P < 0.05 表示水平多效性。", notesEn: "MR-Egger intercept P < 0.05 indicates horizontal pleiotropy." },
          { stepIndex: 3, name: "MR-PRESSO", version: "1.0", params: "NbDistribution=1000, SignifThreshold=0.05", docker: "", notes: "离群值检测 + 失真检验。", notesEn: "Outlier detection + distortion test." },
          { stepIndex: 3, name: "TwoSampleMR mr_leaveoneout()", version: "0.6+", params: "", docker: "", notes: "逐个 SNP 剔除，检查是否有单一 SNP 驱动结果。", notesEn: "Leave-one-out analysis to check if a single SNP drives the result." },
          { stepIndex: 4, name: "TwoSampleMR mv_multivariable_mr()", version: "0.6+", params: "", docker: "", notes: "多变量 MR 控制混杂暴露。", notesEn: "Multivariable MR controls for confounding exposures." },
        ],
        references: [
          { title: "TwoSampleMR R package documentation", url: "https://mrcieu.github.io/TwoSampleMR/", type: "official" },
          { title: "MR-PRESSO: detection of horizontal pleiotropy (Verbanck et al., 2018)", url: "https://doi.org/10.1038/s41588-018-0099-2", type: "paper" },
          { title: "Davey Smith & Hemani (2014) Mendelian randomization", url: "https://doi.org/10.1093/hmg/ddu328", type: "paper" },
          { title: "Hemani et al. (2018) The MR-Base platform", url: "https://doi.org/10.7554/eLife.34408", type: "paper" },
        ],
      },
    ],
  },
  {
    id: "prs",
    name: "Polygenic Risk Score",
    nameZH: "多基因风险评分分析",
    category: "dna",
    tags: ["PRS", "多基因风险评分", "PRSice", "LDpred2", "PRS-CS", "风险预测"],
    version: "1.0.0",
    overview:
      "利用 GWAS summary statistics 预测个体遗传风险。支持 Clumping+Thresholding（PRSice-2）、Bayesian 连续收缩（LDpred2、PRS-CS）三种方法，覆盖数据准备、QC、PRS 计算和模型评估。",
    overviewEn:
      "Uses GWAS summary statistics to predict individual genetic risk. Supports Clumping+Thresholding (PRSice-2) and Bayesian continuous shrinkage (LDpred2, PRS-CS) methods, covering data preparation, QC, PRS calculation, and model evaluation.",
    icon: "dna",
    sources: [
      {
        id: "prsice",
        name: "PRSice-2",
        nameEn: "PRSice-2",
        type: "official",
        url: "https://www.prsice.info/",
        stepNames: [
          "准备数据",
          "质量控制",
          "PRS 计算",
          "模型评估",
        ],
        stepNamesEn: [
          "Prepare Data",
          "Quality Control",
          "PRS Calculation",
          "Model Evaluation",
        ],
        stepDescs: [
          "Base data: GWAS summary statistics（β, SE, P, SNP, EA, OA）；Target data: 个体基因型（PLINK format）",
          "Base: 移除低质量 SNP（MAF < 0.01, INFO < 0.8）；Target: 标准 GWAS QC；正链对齐",
          "C+T（PRSice-2）/ Bayesian 连续收缩（LDpred2, PRS-CS）",
          "R² / AUC / OR per SD / 十折交叉验证 / 分层分析",
        ],
        stepDescsEn: [
          "Base data: GWAS summary statistics (β, SE, P, SNP, EA, OA); Target data: individual genotypes (PLINK format)",
          "Base: remove low-quality SNPs (MAF < 0.01, INFO < 0.8); Target: standard GWAS QC; forward-strand alignment",
          "C+T (PRSice-2) / Bayesian continuous shrinkage (LDpred2, PRS-CS)",
          "R² / AUC / OR per SD / 10-fold cross-validation / stratified analysis",
        ],
        toolRows: [
          { stepIndex: 0, name: "PLINK", version: "1.9 / 2.0", params: "--bfile", docker: "", notes: "Target data 需为 PLINK 格式（bed/bim/fam）。", notesEn: "Target data must be in PLINK format (bed/bim/fam)." },
          { stepIndex: 1, name: "PLINK / QCTOOL", version: "2.0 / 2", params: "--maf 0.01 --info 0.8", docker: "", notes: "Base data 过滤：MAF > 0.01, INFO > 0.8。", notesEn: "Base data filtering: MAF > 0.01, INFO > 0.8." },
          { stepIndex: 2, name: "PRSice-2", version: "2.3+", params: "--bar-levels 5e-8,1e-6,...,1 --fastscore", docker: "", notes: "C+T 方法。--fastscore 只计算指定阈值。", notesEn: "C+T method. --fastscore computes only specified thresholds." },
          { stepIndex: 2, name: "LDpred2 (bigsnpr)", version: "1.12+", params: "snp_ldpred2_auto()", docker: "", notes: "Bayesian 自动调参，推荐。需要 LD 参考面板。", notesEn: "Bayesian auto-tuning, recommended. Requires LD reference panel." },
          { stepIndex: 2, name: "PRS-CS", version: "1.0", params: "--n_gwas=<N>", docker: "", notes: "Bayesian 连续收缩，大样本推荐。PRS-CS-auto 自动调参。", notesEn: "Bayesian continuous shrinkage, recommended for large samples. PRS-CS-auto for auto-tuning." },
          { stepIndex: 3, name: "R / PLINK", version: "4.3+ / 2.0", params: "--score", docker: "", notes: "评估指标：R²（连续）、AUC（二分类）、OR per SD。", notesEn: "Evaluation metrics: R² (continuous), AUC (binary), OR per SD." },
        ],
        references: [
          { title: "PRSice-2: Polygenic Risk Score software (Choi & O'Reilly, 2019)", url: "https://doi.org/10.1093/gigascience/giz082", type: "paper" },
          { title: "LDpred2: better, faster, stronger (Privé et al., 2021)", url: "https://doi.org/10.1093/bioinformatics/btaa1029", type: "paper" },
          { title: "PRS-CS: polygenic prediction via Bayesian regression (Ge et al., 2019)", url: "https://doi.org/10.1038/s41467-019-09718-5", type: "paper" },
          { title: "PRSice-2 Documentation", url: "https://www.prsice.info/", type: "official" },
        ],
      },
    ],
  },
  {
    id: "rare-variant",
    name: "Rare Variant Aggregation",
    nameZH: "罕见变异聚合分析",
    category: "dna",
    tags: ["罕见变异", "SKAT", "SKAT-O", "Burden test", "ACAT", "基因聚合检验"],
    version: "1.0.0",
    overview:
      "针对罕见变异（MAF < 1%）统计效力不足的问题，通过基因级聚合检验提高检测效力。支持 Burden test（方向一致）、SKAT（方差分量）、SKAT-O（自适应混合）和 ACAT（超大样本）。",
    overviewEn:
      "Addresses the statistical power limitation of rare variants (MAF < 1%) through gene-level aggregation tests. Supports Burden test (same-direction effects), SKAT (variance component), SKAT-O (adaptive hybrid), and ACAT (ultra-large samples).",
    icon: "dna",
    sources: [
      {
        id: "skat",
        name: "SKAT/SKAT-O",
        nameEn: "SKAT/SKAT-O",
        type: "official",
        url: "https://www.hsph.harvard.edu/skat/",
        stepNames: [
          "变异 QC",
          "功能注释",
          "拟合空模型",
          "Burden test",
          "SKAT 检验",
          "SKAT-O（推荐）",
          "多重检验校正",
        ],
        stepNamesEn: [
          "Variant QC",
          "Functional Annotation",
          "Fit Null Model",
          "Burden Test",
          "SKAT Test",
          "SKAT-O (recommended)",
          "Multiple Testing Correction",
        ],
        stepDescs: [
          "测序数据变异级质控",
          "基因级注释，确定变异-基因映射",
          "仅协变量的 null model",
          "基因内罕见变异计数求和",
          "方差分量检验",
          "Burden + SKAT 自适应混合",
          "全基因组 per-gene 检验 + FDR 校正",
        ],
        stepDescsEn: [
          "Variant-level QC for sequencing data",
          "Gene-level annotation, determine variant-gene mapping",
          "Covariate-only null model",
          "Per-gene rare variant count summation",
          "Variance component test",
          "Adaptive hybrid of Burden + SKAT",
          "Genome-wide per-gene testing + FDR correction",
        ],
        toolRows: [
          { stepIndex: 0, name: "GATK / BCFtools", version: "4.5 / 1.17", params: "QUAL>30, DP>10, MAF<0.01", docker: "", notes: "QUAL > 30, DP > 10, MAF < 1%。仅保留功能性变异（missense/nonsense/splice-site）。CADD > 20 进一步过滤。", notesEn: "QUAL > 30, DP > 10, MAF < 1%. Retain only functional variants (missense/nonsense/splice-site). CADD > 20 for further filtering." },
          { stepIndex: 1, name: "VEP / ANNOVAR", version: "112 / 2023", params: "--everything", docker: "ensemblorg/ensembl-vep:112", notes: "按基因分组变异。通常排除 synonymous。可选按功能域分层（如 LOFTEE、REVEL > 0.5）。", notesEn: "Group variants by gene. Usually exclude synonymous. Optional functional domain stratification (e.g., LOFTEE, REVEL > 0.5)." },
          { stepIndex: 2, name: "SKAT R 包", version: "2.2+", params: "out_type='D' or 'C'", docker: "", notes: "SKAT_Null_Model(y ~ PC1+PC2+Age+Sex, out_type='D')。out_type='D' 二分类，'C' 连续。", notesEn: "SKAT_Null_Model(y ~ PC1+PC2+Age+Sex, out_type='D'). out_type='D' for binary, 'C' for continuous." },
          { stepIndex: 3, name: "SKAT Burden()", version: "2.2+", params: "r.corr=1", docker: "", notes: "假设基因内所有罕见变异方向一致（同向效应时效力最高）。方向不一致时效力显著下降。", notesEn: "Assumes all rare variants within a gene have the same direction (highest power when true). Power drops significantly with mixed directions." },
          { stepIndex: 4, name: "SKAT SKAT()", version: "2.2+", params: "r.corr=0", docker: "", notes: "不假设变异方向一致，对双向效应（既有保护性又有致病性变异）效力更高。", notesEn: "No direction assumption; higher power for bi-directional effects (both protective and pathogenic variants)." },
          { stepIndex: 5, name: "SKAT SKAT()", version: "2.2+", params: "r.corr=NA", docker: "", notes: "SKAT-O 自动选择最优 r.corr 参数，推荐作为默认方法。", notesEn: "SKAT-O automatically selects optimal r.corr parameter; recommended as default method." },
          { stepIndex: 6, name: "R p.adjust()", version: "4.3+", params: "method='BH'", docker: "", notes: "FDR 校正，显著性阈值 q < 0.05。", notesEn: "FDR correction, significance threshold q < 0.05." },
        ],
        references: [
          { title: "SKAT: SNP-set Kernel Association Test (Wu et al., 2011)", url: "https://doi.org/10.1016/j.ajhg.2011.05.029", type: "paper" },
          { title: "SKAT-O: Optimal unified test (Lee et al., 2012)", url: "https://doi.org/10.1016/j.ajhg.2012.06.004", type: "paper" },
          { title: "ACAT: Aggregated Cauchy Association Test (Liu et al., 2019)", url: "https://doi.org/10.1016/j.ajhg.2019.02.009", type: "paper" },
          { title: "SKAT R package documentation", url: "https://www.hsph.harvard.edu/skat/", type: "official" },
        ],
      },
    ],
  },
];

// ─── Generator ───────────────────────────────────────────────────────

function buildPipeline(template: PipelineTemplate): PipelineDefinition {
  const sources: PipelineSource[] = template.sources.map((src) => {
    const steps: PipelineStep[] = src.stepNames.map((name, i) => {
      const tools: ToolInfo[] = src.toolRows
        .filter((t) => t.stepIndex === i)
        .map((t) => ({
          name: t.name,
          version: t.version,
          params: t.params,
          docker: t.docker,
          notes: t.notes || undefined,
          notesEn: t.notesEn || undefined,
        }));

      const notes = src.toolRows
        .filter((t) => t.stepIndex === i && t.notes)
        .map((t) => t.notes)
        .join(" ");
      const notesEn = src.toolRows
        .filter((t) => t.stepIndex === i && t.notesEn)
        .map((t) => t.notesEn)
        .join(" ") || undefined;

      return {
        id: `step-${i + 1}`,
        name,
        nameEn: src.stepNamesEn ? src.stepNamesEn[i] : undefined,
        description: src.stepDescs[i] || "",
        descriptionEn: src.stepDescsEn ? src.stepDescsEn[i] : undefined,
        tools,
        notes,
        notesEn,
        position: { x: 0, y: i * 120 },
      };
    });

    return {
      id: src.id,
      name: src.name,
      nameEn: src.nameEn,
      type: src.type,
      url: src.url,
      steps,
      references: src.references,
    };
  });

  return {
    id: template.id,
    name: template.name,
    nameZH: template.nameZH,
    category: template.category,
    tags: template.tags,
    overview: template.overview,
    overviewEn: template.overviewEn,
    icon: template.icon,
    version: template.version,
    sources,
  };
}

// ─── Main ────────────────────────────────────────────────────────────

function varName(id: string): string {
  // Identifier can't start with a digit; prefix such cases.
  if (/^\d/.test(id)) return `pipe_${id}`;
  return id.replace(/-/g, "");
}

function main() {
  if (!existsSync(DATA_DIR)) {
    mkdirSync(DATA_DIR, { recursive: true });
  }

  for (const template of PIPELINES) {
    const pipeline = buildPipeline(template);
    const filePath = resolve(DATA_DIR, `${template.id}.json`);
    writeFileSync(filePath, JSON.stringify(pipeline, null, 2) + "\n", "utf-8");
    console.log(`  ✓ ${template.id}.json (${pipeline.sources.length} sources, ${pipeline.sources.reduce((a, s) => a + s.steps.length, 0)} steps)`);
  }

  // Omics pipeline IDs (manually maintained)
  const omicsIds = [
    "wgs-germline", "wgs-somatic", "wes", "rna-seq", "scrna-seq",
    "chip-seq", "wgbs", "metagenomics", "16s",
  ];

  // Generate versions.json
  const versions: Record<string, string> = {};
  for (const template of PIPELINES) {
    versions[template.id] = template.version;
  }
  // Add omics pipelines (manually maintained, assumed v1.0.0)
  for (const id of omicsIds) {
    versions[id] = "1.0.0";
  }
  const versionsPayload = {
    generated: new Date().toISOString(),
    pipelines: versions,
  };
  writeFileSync(resolve(DATA_DIR, "versions.json"), JSON.stringify(versionsPayload, null, 2) + "\n", "utf-8");
  console.log("  ✓ versions.json");
  const studyIds = PIPELINES.map((p) => p.id);

  const studyImports = PIPELINES.map(
    (p) => `import ${varName(p.id)} from "./${p.id}.json";`
  );
  const omicsImports = omicsIds.map(
    (id) => `import ${varName(id)} from "./${id}.json";`
  );

  const studyExports = PIPELINES.map((p) => `  ${varName(p.id)},`);
  const omicsExports = omicsIds.map((id) => `  ${varName(id)},`);

  const indexContent = `import type { PipelineDefinition } from "../../types/pipeline";
${studyImports.join("\n")}
${omicsImports.join("\n")}

export const pipelines: PipelineDefinition[] = [
${studyExports.join("\n")}
${omicsExports.join("\n")}
] as PipelineDefinition[];

export const categoryLabels: Record<string, string> = {
  dna: "DNA",
  rna: "RNA",
  epigenetics: "表观遗传",
  microbiome: "微生物",
};

export const categoryIcons: Record<string, string> = {
  dna: "dna",
  rna: "microscope",
  epigenetics: "layers",
  microbiome: "bacteria",
};
`;

  writeFileSync(resolve(DATA_DIR, "index.ts"), indexContent, "utf-8");
  console.log("  ✓ index.ts");
}

main();
