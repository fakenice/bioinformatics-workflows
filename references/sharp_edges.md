# Bioinformatics Workflows - Sharp Edges

## Pipeline Not Resumable After Failure

### **Id**
non-resumable-pipeline
### **Severity**
critical
### **Summary**
Restart from beginning after crash wastes hours/days of compute
### **Symptoms**
  - Cluster job times out, entire pipeline restarts
  - One sample fails, all samples re-run
  - Intermediate files deleted before completion
### **Why**
  Genomics pipelines can run for days. Without checkpointing/caching:
  - A network blip at hour 47 means starting over
  - Cluster preemption restarts everything
  - Debugging requires full re-runs
  
  Most workflow managers have resume capability, but it must be configured.
  
### **Gotcha**
  # Snakemake: Deletes temp files by default
  temp("results/aligned/{sample}.unsorted.bam")
  # If job fails after this, can't resume without re-running
  
  # Nextflow: cache disabled
  process.cache = false
  # Every run starts from scratch
  
### **Solution**
  # Nextflow: Enable resume (default)
  nextflow run main.nf -resume
  
  # Snakemake: Use --keep-incomplete
  snakemake --keep-incomplete ...
  
  # Keep intermediate files until pipeline completes
  # Don't mark as temp() until you're sure
  
  # Use work directory on fast storage
  workDir = '/scratch/nextflow_work'
  

## Non-Deterministic File Processing Order

### **Id**
unstable-sort-order
### **Severity**
high
### **Summary**
Glob patterns produce different order on different runs
### **Symptoms**
  - Same inputs, different checksum on outputs
  - Merged VCFs have samples in random order
  - Hard to compare runs
### **Why**
  file() and glob patterns don't guarantee order.
  Different filesystems return files in different orders.
  This causes non-reproducible outputs even with same inputs.
  
### **Gotcha**
  # Nextflow - order not guaranteed
  Channel.fromFilePairs("*.{1,2}.fq.gz")
  
  # Snakemake - expand() order varies
  expand("data/{sample}.bam", sample=samples)
  
### **Solution**
  // Nextflow: Sort the channel
  Channel
      .fromFilePairs("*.{1,2}.fq.gz")
      .toSortedList { it[0] }  // Sort by sample name
      .flatMap()
      .set { sorted_reads }
  
  # Snakemake: Sort in rule
  sorted_samples = sorted(samples)
  expand("data/{sample}.bam", sample=sorted_samples)
  
  # Always sort before merging
  bcftools merge $(ls *.vcf.gz | sort) > merged.vcf.gz
  

## Symlinks Not Followed in Containers

### **Id**
symlink-container-failure
### **Severity**
high
### **Summary**
Files exist but container process can't read them
### **Symptoms**
  - File not found errors in container
  - Works outside container, fails inside
  - Absolute path works, relative doesn't
### **Why**
  Containers mount specific directories.
  Symlinks pointing outside mounted directories are broken.
  This is especially common with shared storage and staged inputs.
  
### **Gotcha**
  # Host filesystem:
  /data/project/sample.bam -> /shared/raw_data/sample.bam
  
  # Container only mounts /data/project
  # Symlink target /shared/raw_data is not available
  
### **Solution**
  // Nextflow: Use stageInMode 'copy' for problem files
  process ALIGN {
      stageInMode 'copy'  // or 'link' with full path mounts
      ...
  }
  
  // Mount all required directories
  docker.runOptions = '-v /data:/data -v /shared:/shared'
  singularity.runOptions = '-B /data:/data -B /shared:/shared'
  
  # Snakemake: Use shadow rules
  rule align:
      shadow: "minimal"  # Copies inputs to temp dir
      ...
  

## Memory Requests Don't Match Actual Usage

### **Id**
memory-estimation-wrong
### **Severity**
high
### **Summary**
Jobs OOM killed or waste cluster resources
### **Symptoms**
  - Jobs killed with OOM (out of memory)
  - Jobs pending because requesting too much memory
  - Cluster efficiency < 50%
### **Why**
  Genomics tools have variable memory usage:
  - BWA: ~5GB per thread for human genome
  - STAR: 30-40GB for genome loading
  - GATK: Varies wildly by step
  
  Static memory requests don't account for sample size variation.
  
### **Gotcha**
  # Requesting flat 8GB for all samples
  process {
      memory = '8 GB'
  }
  # Small sample: wastes 6GB
  # Large sample: OOM killed
  
### **Solution**
  // Nextflow: Dynamic memory based on input
  process ALIGN {
      memory { 6.GB * task.cpus }
  
      // Or with retry
      memory { 8.GB * task.attempt }
      errorStrategy { task.exitStatus in 137..140 ? 'retry' : 'terminate' }
      maxRetries 3
  }
  
  # Snakemake: Use resources based on input
  rule align:
      resources:
          mem_mb=lambda wildcards, input: max(8000, input.size_mb * 10)
      ...
  
  # Profile tools to understand memory patterns
  # Use /usr/bin/time -v to get max RSS
  

## Ignoring Non-Zero Exit Codes

### **Id**
missing-exit-codes
### **Severity**
high
### **Summary**
Pipeline continues after tool failure, producing garbage
### **Symptoms**
  - Empty output files
  - Truncated BAMs/VCFs
  - Downstream tools fail with cryptic errors
### **Why**
  Some tools return non-zero exit codes for warnings.
  Others return 0 even on failure.
  Shell pipelines mask exit codes by default.
  
### **Gotcha**
  # Shell pipeline hides BWA failure
  bwa mem ref.fa reads.fq | samtools sort -o out.bam
  # Exit code is from samtools, not bwa
  
  # Tool returns 0 but wrote nothing
  some_tool input.fa > output.fa  # Empty file, exit 0
  
### **Solution**
  # Use pipefail in shell
  set -euo pipefail
  bwa mem ref.fa reads.fq | samtools sort -o out.bam
  
  # Nextflow: Always set in shell
  process ALIGN {
      shell:
      '''
      set -euo pipefail
      bwa mem !{ref} !{reads} | samtools sort -o !{output}
      '''
  }
  
  # Validate outputs
  if [[ ! -s output.fa ]]; then
      echo "Error: output file is empty" >&2
      exit 1
  fi
  
  # Check expected output patterns
  samtools quickcheck aligned.bam || exit 1
  

## Multiple Jobs Writing to Same Output

### **Id**
race-condition-outputs
### **Severity**
critical
### **Summary**
Parallel jobs overwrite each other's results
### **Symptoms**
  - Random missing samples in merged output
  - Different results each run
  - File corruption errors
### **Why**
  When parallelizing, multiple jobs may try to write to the same file.
  This causes race conditions and data loss.
  
### **Gotcha**
  # Multiple parallel jobs appending to same file
  parallel 'process {} >> combined_results.txt' ::: samples/*
  # Order is random, may have interleaved lines
  
  # GATK GenomicsDBImport with multiple writers
  gatk GenomicsDBImport ... --batch-size 50
  # Can fail with too many concurrent writers
  
### **Solution**
  # Write to separate files, merge at end
  parallel 'process {} > results/{/.}.txt' ::: samples/*
  cat results/*.txt > combined_results.txt
  
  # Use atomic writes
  process {} > temp_$$.txt && mv temp_$$.txt final.txt
  
  # Let workflow manager handle parallelism
  # Don't manually parallelize within rules/processes
  

## Using 'latest' Container Tags

### **Id**
version-drift-containers
### **Severity**
high
### **Summary**
Pipeline behavior changes without code changes
### **Symptoms**
  - Pipeline worked yesterday, fails today
  - Different results on different machines
  - Can't reproduce old analysis
### **Why**
  'latest' tags get updated. Your pipeline pulls a new version
  with different behavior, bugs, or broken dependencies.
  
### **Gotcha**
  container = 'biocontainers/bwa:latest'
  # Today: bwa 0.7.17
  # Next week: bwa 0.7.18 with different defaults
  
### **Solution**
  # Always use specific version tags
  container = 'biocontainers/bwa:0.7.17--h5bf99c6_8'
  
  # Use SHA256 digest for maximum reproducibility
  container = 'biocontainers/bwa@sha256:abc123...'
  
  # Lock all tool versions in environment
  # Export conda-lock or requirements.txt

## Reference Genome Version Mismatch

### **Id**
reference-genome-mismatch
### **Severity**
critical
### **Summary**
Mixing reference genome versions produces wrong variants and broken annotations
### **Symptoms**
  - Variants at wrong positions or on wrong contigs
  - VEP/SnpEff annotation produces empty or wrong results
  - LiftOver fails or produces low-quality results
  - Cross-sample analysis has zero overlap
### **Why**
  Reference assemblies (hg19/GRCh37 vs hg38/GRCh38) have different
  coordinate systems, contig names (1 vs chr1), and sequences.
  Mixing them silently corrupts analysis:
  - BAM aligned to hg38 but GATK uses hg37 reference
  - dbSNP from hg37 applied to hg38-aligned BAM
  - Annotation databases (VEP, SnpEff) built for wrong assembly
  
### **Gotcha**
  # Contig name mismatch: GRCh38 uses 'chr1', some tools expect '1'
  samtools view -h aligned.bam | head
  # @SQ SN:chr1 LN:248956422  (hg38)
  # But reference FASTA has:
  # >1  (ensembl style, no 'chr' prefix)
  
  # dbSNP from wrong build
  gatk HaplotypeCaller --variant dbsnp_138.b37.vcf  # b37 build!
  # Applied to GRCh38 BAM -> wrong positions
  
### **Solution**
  # Verify ALL reference files use the same build:
  # - Reference FASTA (.fa/.fa.gz)
  # - Index files (.bwt, .fai, .dict)
  # - Known sites (dbSNP, Mills indels, gnomAD)
  # - Annotation databases (VEP cache, SnpEff database)
  
  # Check contig names and lengths match
  samtools view -H aligned.bam | grep "^@SQ" | head
  grep "^>" reference.fa | head
  # Both must have identical SN and LN values
  
  # Use consistent naming convention (recommend 'chr' prefix for GRCh38)
  # Build a single reference bundle and use it consistently:
  # GRCh38_bundle/
  # ├── Homo_sapiens_assembly38.fasta
  # ├── Homo_sapiens_assembly38.fasta.fai
  # ├── Homo_sapiens_assembly38.dict
  # ├── Homo_sapiens_assembly38.fasta.bwt
  # ├── known_sites/
  # │   ├── dbsnp_146.hg38.vcf.gz
  # │   ├── Mills_and_1000G_gold_standard.indels.hg38.vcf.gz
  # │   └── gnomad.v4.1.sites.vcf.gz
  # └── annotation/
  #     └── vep_cache/
  
  # For liftOver, verify mapping rate > 95%
  # Discard variants that failed liftOver

## GATK BQSR With Wrong Known Sites

### **Id**
gatk-bqsr-wrong-sites
### **Severity**
high
### **Summary**
Base Quality Score Recalibration uses wrong known variants database
### **Symptoms**
  - Over-filtering of good bases (quality scores too low)
  - Under-filtering of bad bases (false positive variants)
  - Different variant calls on re-run with updated dbSNP
### **Why**
  BQSR adjusts base quality scores based on known variant sites.
  If known sites are from wrong genome build or too old,
  it systematically mislabels real variants as sequencing errors.
  
### **Gotcha**
  # Using b37 known sites on GRCh38
  gatk BaseRecalibrator \
      -I input.bam \
      -R GRCh38.fa \
      --known-sites dbsnp_138.b37.vcf.gz  # WRONG BUILD
  
  # Using very old dbSNP (138) when 156 is available
  # Missing thousands of known variants -> recalibration over-corrects
  
### **Solution**
  # Use GATK resource bundle matching your reference:
  # GRCh38:
  gatk BaseRecalibrator \
      -R Homo_sapiens_assembly38.fasta \
      -I input.bam \
      --known-sites Homo_sapiens_assembly38.dbsnp138.vcf \
      --known-sites Mills_and_1000G_gold_standard.indels.hg38.vcf.gz \
      --known-sites Homo_sapiens_assembly38.known_indels.vcf.gz
  
  # Always check known sites version matches reference build
  # Update known sites when new dbSNP/gnomAD releases available
  # Document exact known sites versions in pipeline config

## Sample Cross-Contamination

### **Id**
sample-contamination
### **Severity**
critical
### **Summary**
Sample mix-up or contamination produces wrong variant calls
### **Symptoms**
  - Tumor-normal pairs have swapped samples
  - Unusually high heterozygosity in "pure" samples
  - Sex chromosome mismatch (XX sample called as XY)
  - Identity check fails against genotyping array
### **Why**
  Sample swaps can happen at collection, library prep, or sequencing.
  Cross-contamination (index hopping) on multiplexed runs is common.
  Without verification, downstream analysis is meaningless.
  
### **Gotcha**
  # Index hopping on patterned flowcells (NovaSeq)
  # ~1% of reads have wrong index
  # For pooled normal/tumor, this means tumor reads in normal
  # -> Mutect2 filters out real somatic variants
  
  # Sample swap in tumor-normal pair
  # Normal is actually tumor, tumor is actually normal
  # -> All "somatic" variants are germline
  
### **Solution**
  # Run VerifyBamID or Somalier on every BAM
  # Check against expected sex and population
  
  # VerifyBamID2
  verifybamid2 --reference GRCh38.fa \
      --bam sample.bam \
      --vcf reference_panel.vcf.gz
  
  # Somalier (fast, works on BAM/CRAM)
  somalier extract -f reference.fa sample.bam
  somalier relate sample1.somalier sample2.somalier
  
  # Check sex: count X/Y chromosome reads
  # Female: X ~2x autosomes, Y ~0
  # Male: X ~1x autosomes, Y ~1x autosomes
  
  # For tumor-normal: verify relatedness (should be same person)
  # FREM (FREquency-based contamination Estimation for Mutect2)
  # is built into GATK Mutect2
  
  # Use unique dual indexes (UDI) to prevent index hopping
  # Not combinatorial dual indexes

## GATK HaplotypeCaller Emitting Wrong Confidence

### **Id**
gatk-gvcf-mode-misuse
### **Severity**
high
### **Summary**
Wrong GVCF mode causes missing variants or bloated files
### **Symptoms**
  - Joint genotyping fails or takes excessive memory
  - Non-variant blocks have wrong confidence
  - Missing calls in regions that should have variants
### **Why**
  HaplotypeCaller has two GVCF modes:
  - --emit-ref-confidence GVCF (for joint genotyping later)
  - --emit-ref-confidence BP_RESOLUTION (every position)
  
  Using BP_RESOLUTION creates huge files but is sometimes needed.
  Using GVCF is standard but requires GenomicsDBImport + GenotypeGVCFs.
  
### **Gotcha**
  # Emitting GVCF but then running HaplotypeCaller in normal mode
  # instead of GenotypeGVCFs for joint calling
  gatk HaplotypeCaller --emit-ref-confidence GVCF -O sample.g.vcf.gz
  # Then wrongly:
  gatk HaplotypeCaller -V sample.g.vcf.gz  # WRONG - can't genotype a GVCF
  # Correct:
  gatk GenomicsDBImport --genomicsdb-workspace-path db \
      --variant sample.g.vcf.gz
  gatk GenotypeGVCFs -G db -R ref.fa -O joint.vcf.gz
  
  # Using BP_RESOLUTION for large cohorts -> TB-sized files
  gatk HaplotypeCaller --emit-ref-confidence BP_RESOLUTION
  # 30x WGS human: ~50GB per sample in BP_RESOLUTION vs ~5GB in GVCF
  
### **Solution**
  # For single-sample: emit regular VCF (no GVCF)
  gatk HaplotypeCaller -I input.bam -R ref.fa -O output.vcf.gz
  
  # For joint genotyping (recommended for cohorts >3):
  # Step 1: Per-sample GVCF
  gatk HaplotypeCaller --emit-ref-confidence GVCF \
      -I sample.bam -R ref.fa -O sample.g.vcf.gz
  
  # Step 2: GenomicsDBImport (batch samples)
  gatk GenomicsDBImport \
      --genomicsdb-workspace-path genomicsdb \
      --variant samples_list.txt \
      --batch-size 50
  
  # Step 3: Joint genotyping
  gatk GenotypeGVCFs \
      -G genomicsdb -R ref.fa \
      --only-output-callable-regions \
      -O joint.vcf.gz
  
  # Only use BP_RESOLUTION if you need every-position reference calls
  # (e.g., specific QC applications)


## VQSR Apply: Chain vs Parallel Strategy

### **Id**
vqsr-chain-vs-parallel
### **Severity**
high
### **Summary**
Using parallel ApplyVQSR (SNP and INDEL independently from raw VCF) instead of chain (SNP first, then INDEL on filtered VCF) produces lower quality INDEL calls
### **Symptoms**
  - Higher false positive rate in INDEL calls
  - INDEL tranches model trained on unfiltered SNP noise
  - Inconsistent variant quality between runs using different strategies
  - Downstream analysis gets noisier INDEL set
### **Why**
GATK VQSR has two application strategies:
- Chain (recommended): Apply SNP VQSR first, then apply INDEL VQSR on the SNP-filtered VCF
- Parallel (non-recommended): Apply SNP and INDEL VQSR independently from the same raw VCF

The chain approach is recommended because INDEL model training and filtering benefits
from SNP quality already being optimized. Low-quality SNPs can interfere with INDEL
variant quality assessment in the raw VCF.

### **Gotcha**
``bash
# WRONG: Parallel - both read from raw VCF independently
gatk ApplyVQSR -V raw.vcf.gz -O snps_pass.vcf.gz -mode SNP --truth-sensitivity-filter-level 99.5 ...
gatk ApplyVQSR -V raw.vcf.gz -O indels_pass.vcf.gz -mode INDEL --truth-sensitivity-filter-level 99.0 ...
# INDEL model sees unfiltered SNP noise

# CORRECT: Chain - INDEL reads from SNP-filtered VCF
gatk ApplyVQSR -V raw.vcf.gz -O tmp_snp.vcf.gz -mode SNP --truth-sensitivity-filter-level 99.5 ...
gatk ApplyVQSR -V tmp_snp.vcf.gz -O final.vcf.gz -mode INDEL --truth-sensitivity-filter-level 99.0 ...
``

### **Solution**
``bash
# Always use chain strategy (GATK official recommendation)
# Step 1: Apply SNP model to raw VCF
gatk ApplyVQSR \
    -V input_norm.vcf.gz \
    -O tmp_snp_recal.vcf.gz \
    --recal-file global_snps.recal \
    --tranches-file global_snps.tranches \
    -mode SNP \
    --truth-sensitivity-filter-level 99.5

# Step 2: Apply INDEL model to SNP-filtered VCF
gatk ApplyVQSR \
    -V tmp_snp_recal.vcf.gz \
    -O final_PASS.vcf.gz \
    --recal-file global_indels.recal \
    --tranches-file global_indels.tranches \
    -mode INDEL \
    --truth-sensitivity-filter-level 99.0

# If downstream needs separated SNP/INDEL files:
# Split AFTER chain ApplyVQSR, not during
bcftools view -v snps -f PASS final_PASS.vcf.gz -Oz -o pure_snps.vcf.gz
bcftools view -v indels -f PASS final_PASS.vcf.gz -Oz -o pure_indels.vcf.gz
``

[由 Step 5 知识积累自动添加, 日期: 2026-07-29]


## BQSR With Incomplete Known Sites

### **Id**
bqsr-incomplete-known-sites
### **Severity**
medium
### **Summary**
BaseRecalibrator only uses dbSNP as known sites, missing Mills indels and other resources, causing suboptimal base quality recalibration
### **Symptoms**
  - Over-correction of bases at real indel sites (treated as errors)
  - Slightly lower variant quality at indel flanking regions
  - Recalibration table shows higher error rate near indels
### **Why**
BQSR models systematic errors in base quality scores.
It needs known variant sites to distinguish real variants from sequencing errors.
If only dbSNP is provided, indel regions are not masked, and real indel
flanking bases are incorrectly treated as sequencing errors.

GATK recommends providing ALL available known sites databases:
- dbSNP (SNP sites)
- Mills indels (known indel sites)
- Known indels (additional indel sites)

### **Gotcha**
``bash
# Suboptimal: only dbSNP
gatk BaseRecalibrator \
    -I sample.bam \
    -R ref.fa \
    --known-sites dbsnp_138.vcf.gz
# Real indel bases treated as errors -> over-correction

# Correct: all known sites
gatk BaseRecalibrator \
    -I sample.bam \
    -R ref.fa \
    --known-sites dbsnp_138.vcf.gz \
    --known-sites Mills_and_1000G_gold_standard.indels.hg38.vcf.gz \
    --known-sites Homo_sapiens_assembly38.known_indels.vcf.gz
``

### **Solution**
``bash
# Always provide all available known sites matching your reference build
gatk BaseRecalibrator \
    -R Homo_sapiens_assembly38.fasta \
    -I sample.markdup.bam \
    --known-sites Homo_sapiens_assembly38.dbsnp138.vcf.gz \
    --known-sites Mills_and_1000G_gold_standard.indels.hg38.vcf.gz \
    --known-sites Homo_sapiens_assembly38.known_indels.vcf.gz \
    -O sample.recal.table

# Verify known sites match reference build (GRCh38/hg38)
# Do NOT use b37 known sites on GRCh38 reference
``

[由 Step 5 知识积累自动添加, 日期: 2026-07-29]

## Manta SV: Not Filtering PASS Variants

### **Id**
manta-missing-pass-filter
### **Severity**
medium
### **Summary**
Using raw Manta diploidSV.vcf.gz without filtering PASS variants introduces low-quality SV calls
### **Symptoms**
  - High false positive rate in downstream SV analysis
  - Low-quality SV candidates with MinQUALLow or LowQual filters
  - Inflated SV count in annotation reports
### **Why**
Manta outputs all SV candidates in candidateSV.vcf.gz, and scored variants in diploidSV.vcf.gz.
Not all variants in diploidSV.vcf.gz pass quality filters. Variants without PASS filter
have insufficient evidence or low quality scores.

### **Gotcha**
```bash
# WRONG: using raw output directly
cp results/variants/diploidSV.vcf.gz final.vcf.gz
# Includes LowQual, MinQUALLow filtered variants

# CORRECT: filter PASS only
bcftools view -f PASS diploidSV.vcf.gz -O z -o filteredSV.vcf.gz
tabix -p vcf filteredSV.vcf.gz
```

### **Solution**
```bash
# Always filter PASS variants from Manta output
bcftools view -f PASS -O z -o sample.filteredSV.vcf.gz sample.manta.diploidSV.vcf.gz
tabix -p vcf sample.filteredSV.vcf.gz

# Verify: compare raw vs filtered counts
raw_count=$(bcftools view -H diploidSV.vcf.gz | wc -l)
filtered_count=$(bcftools view -H filteredSV.vcf.gz | wc -l)
echo "Raw: $raw_count | PASS: $filtered_count"
```

[由 Step 5 知识积累自动添加, 日期: 2026-07-29]


## GATK gCNV: Inconsistent Counts File Row Count

### **Id**
gcnv-inconsistent-counts
### **Severity**
high
### **Summary**
Different samples have different row counts in counts.tsv files, causing GermlineCNVCaller to fail
### **Symptoms**
  - GermlineCNVCaller crashes with interval mismatch error
  - Some samples have fewer/more rows than expected
  - FilterIntervals produces inconsistent interval lists
### **Why**
CollectReadCounts uses interval lists to count reads per bin.
If samples use different interval files, or if the reference has different contigs,
the output TSV files will have different row counts.
All samples in a cohort MUST use the same RAW_INTERVALS and NOISE_BED.

### **Gotcha**
```bash
# WRONG: different interval files for different batches
# Batch 1: --interval-list wgs_1000bp_v1.interval_list
# Batch 2: --interval-list wgs_1000bp_v2.interval_list
# -> Different row counts, GermlineCNVCaller fails

# CORRECT: same interval file for ALL samples
INTERVALS="Homo_sapiens_assembly38.wgs.1000bp.interval_list"
gatk CollectReadCounts -L "$INTERVALS" --XL "$NOISE_BED" ...
```

### **Solution**
```bash
# Verify all counts files have identical row count BEFORE running gCNV
EXPECTED_ROW=2954698  # WGS 1000bp, GRCh38, main chromosomes
for f in counts_dir/*.counts.tsv; do
    rows=$(wc -l < "$f")
    if [ "$rows" -ne "$EXPECTED_ROW" ]; then
        echo "ERROR: $f has $rows rows (expected $EXPECTED_ROW)" >&2
        exit 1
    fi
done
echo "All counts files consistent"

# Always use the same RAW_INTERVALS and NOISE_BED for all samples
# Re-run CollectReadCounts for inconsistent samples with correct intervals
```

[由 Step 5 知识积累自动添加, 日期: 2026-07-29]


## GATK gCNV: Main Chromosome Filtering Required

### **Id**
gcnv-scaffold-contamination
### **Severity**
medium
### **Summary**
Including unplaced scaffolds and alt contigs causes gCNV model instability and excessive runtime
### **Symptoms**
  - GermlineCNVCaller takes excessively long to converge
  - PostprocessGermlineCNVCalls fails with contig not in dictionary error
  - Many low-quality CNV calls on scaffold regions
### **Why**
GRCh38 contains many unplaced scaffolds and alt contigs.
These regions have abnormal read depth patterns that destabilize the gCNV model.
Filtering to main chromosomes (chr1-22, X, Y) before modeling is recommended.

### **Gotcha**
```bash
# WRONG: using all intervals including scaffolds
gatk GermlineCNVCaller -L "$FILTERED_INTERVALS" ...
# Includes chrUn_*, chr*_random, chr*_alt -> model instability

# CORRECT: filter to main chromosomes only
grep '^@' "$FILTERED_INTERVALS" > "$MAIN_FILTERED_INTERVALS"
awk '!/^@/ && $1 ~ /^chr([1-9]|1[0-9]|2[0-2]|[XY])$/' "$FILTERED_INTERVALS" >> "$MAIN_FILTERED_INTERVALS"
gatk GermlineCNVCaller -L "$MAIN_FILTERED_INTERVALS" ...
```

### **Solution**
```bash
# After FilterIntervals, extract only main chromosomes
MAIN_INTERVALS="${GCNV_RESOURCES}/wgs_1000bp.main_chrs.gc_filtered.interval_list"
grep '^@' "$FILTERED_INTERVALS" > "$MAIN_INTERVALS"
awk '!/^@/ && $1 ~ /^chr([1-9]|1[0-9]|2[0-2]|[XY])$/' "$FILTERED_INTERVALS" >> "$MAIN_INTERVALS"

# Use MAIN_INTERVALS for all downstream gCNV steps
# Also verify reference .dict matches main chromosome names
```

[由 Step 5 知识积累自动添加, 日期: 2026-07-29]
