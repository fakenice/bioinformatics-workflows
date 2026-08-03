# QC 标准参考（基于 ENCODE/GATK）

## ATAC-seq / ChIP-seq
- 生物学重复 ≥ 2
- 比对率 > 95%（>80% 可接受）
- NRF > 0.9，PBC1 > 0.9，PBC2 > 3
- FRiP score > 0.3（>0.2 可接受）
- TSS enrichment（GRCh38）：> 7 理想，5-7 可接受
- IDR 一致性：rescue 和 self-consistency 比值 < 2
- ATAC-seq：需有 NFR（nucleosome free region）和单核小体峰

## RNA-seq
- 比对率 > 80%
- 重复相关性 R² > 0.8
- rRNA 比例 < 10%
- 5'/3' 偏差 < 1.5

## WGS/WES 变异检测
- 平均覆盖度：WGS ≥ 30x，WES ≥ 100x
- Q30 比例 > 85%
- 重复率 < 20%
- 变异质量：QD > 2.0、MQ > 40.0、FS < 60.0、SOR < 3.0
