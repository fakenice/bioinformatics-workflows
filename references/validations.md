# Bioinformatics Workflows - Validations

## Using Latest Container Tag

### **Id**
latest-container-tag
### **Severity**
warning
### **Type**
regex
### **Pattern**
  - container.*['"].*:latest['"]
  - docker.*:latest
  - singularity.*:latest
### **Message**
Pin container version instead of 'latest' for reproducibility.
### **Fix Action**
Use specific version tag (e.g., :0.7.17--h5bf99c6_8)
### **Applies To**
  - **/*.nf
  - **/nextflow.config
  - **/*.smk
  - **/Snakefile

## Shell Without Pipefail

### **Id**
no-pipefail
### **Severity**
warning
### **Type**
regex
### **Pattern**
  - shell:\s*['"]\s*[^'"]*\|[^'"]*['"](?![\s\S]{0,50}pipefail)
  - shell:\s*'''[^']*\|[^']*'''(?![\s\S]{0,50}pipefail)
### **Message**
Use 'set -euo pipefail' in shell blocks with pipes.
### **Applies To**
  - **/*.nf

## Hardcoded Thread Count

### **Id**
hardcoded-thread-count
### **Severity**
info
### **Type**
regex
### **Pattern**
  - -t\s+[0-9]+(?![\s\S]{0,20}\$\{?task\.cpus)
  - --threads\s+[0-9]+(?![\s\S]{0,20}\$\{?task\.cpus)
  - -p\s+[0-9]+(?![\s\S]{0,20}threads)
### **Message**
Use dynamic thread allocation (task.cpus or {threads}).
### **Applies To**
  - **/*.nf
  - **/*.smk

## Process Without Version Tracking

### **Id**
no-version-output
### **Severity**
info
### **Type**
regex
### **Pattern**
  - process\s+\w+\s*\{[^}]*output:[^}]*(?!versions)[^}]*\}
### **Message**
Include versions.yml output for tool version tracking.
### **Applies To**
  - **/*.nf

## Temp Files Without Backup Strategy

### **Id**
temp-without-protected
### **Severity**
info
### **Type**
regex
### **Pattern**
  - temp\([^)]+\.bam[^)]*\)
  - temp\([^)]+\.vcf[^)]*\)
### **Message**
Consider keeping intermediate BAM/VCF until pipeline completes.
### **Applies To**
  - **/*.smk

## Snakemake Rule Without Log

### **Id**
missing-log-directive
### **Severity**
info
### **Type**
regex
### **Pattern**
  - rule\s+\w+:[^}]*(?!log:)[^}]*shell:
### **Message**
Add log directive to capture stderr for debugging.
### **Applies To**
  - **/*.smk
  - **/Snakefile

## Process Without Resource Limits

### **Id**
no-resource-specification
### **Severity**
warning
### **Type**
regex
### **Pattern**
  - process\s+\w+\s*\{[^}]*(?!memory|cpus|label)[^}]*\}
### **Message**
Specify memory and CPU requirements for cluster execution.
### **Applies To**
  - **/*.nf

## Merging Files Without Sorting

### **Id**
unsorted-merge-input
### **Severity**
info
### **Type**
regex
### **Pattern**
  - collect\(\)(?![\s\S]{0,50}sort)
  - bcftools\s+merge(?![\s\S]{0,50}sort)
### **Message**
Sort input files before merging for reproducible order.
### **Applies To**
  - **/*.nf
  - **/*.smk

## Process Without Error Handling

### **Id**
no-error-strategy
### **Severity**
info
### **Type**
regex
### **Pattern**
  - process\s+\w+\s*\{[^}]*(?!errorStrategy)[^}]*\}
### **Message**
Consider adding errorStrategy for retry on transient failures.
### **Applies To**
  - **/*.nf

## Absolute Path in Workflow Definition

### **Id**
absolute-path-in-workflow
### **Severity**
warning
### **Type**
regex
### **Pattern**
  - ['"]/home/[a-z]+/.*['"]
  - ['"]/data/.*['"]
  - ['"]C:\\.*['"]
### **Message**
Use relative paths or params for portability.
### **Applies To**
  - **/*.nf
  - **/*.smk
  - **/Snakefile

## Mixing Reference Genome Builds

### **Id**
reference-build-mismatch
### **Severity**
critical
### **Type**
regex
### **Pattern**
  - hg19.*GRCh38
  - b37.*hg38
  - GRCh37.*assembly38
  - dbsnp_138\.b37.*assembly38
### **Message**
Reference genome builds are mixed. All files must use the same build.
### **Fix Action**
Use a consistent reference bundle (e.g., GRCh38 for all: FASTA, index, known sites, annotation).
### **Applies To**
  - **/*.nf
  - **/*.smk
  - **/*.wdl
  - **/nextflow.config
  - **/config/*.yaml

## GATK GVCF Without Joint Genotyping

### **Id**
gvcf-without-genotyping
### **Severity**
warning
### **Type**
regex
### **Pattern**
  - emit-ref-confidence\s+GVCF(?!.*GenotypeGVCFs)(?!.*GenomicsDBImport)
### **Message**
GVCF was emitted but no joint genotyping (GenotypeGVCFs/GenomicsDBImport) follows.
### **Fix Action**
Add GenomicsDBImport + GenotypeGVCFs steps, or use regular VCF if single-sample.
### **Applies To**
  - **/*.nf
  - **/*.smk
  - **/*.wdl

## Missing Read Group In Alignment

### **Id**
missing-read-group
### **Severity**
warning
### **Type**
regex
### **Pattern**
  - bwa\s+mem(?![\s\S]{0,200}-R)
  - bwa-mem2(?![\s\S]{0,200}-R)
### **Message**
BWA alignment without -R read group. GATK requires read groups.
### **Fix Action**
Add -R '@RG\tID:sample\tSM:sample\tPL:ILLUMINA\tLB:lib1' to bwa mem command.
### **Applies To**
  - **/*.nf
  - **/*.smk
  - **/*.sh

## Hardcoded Memory For Genomics Tools

### **Id**
hardcoded-memory-genomics
### **Severity**
warning
### **Type**
regex
### **Pattern**
  - memory\s*=\s*['"]\d+\s*GB['"](?![\s\S]{0,100}attempt|input|cpus)
### **Message**
Static memory for genomics tools causes OOM or waste. Use dynamic allocation.
### **Fix Action**
Use memory { 8.GB * task.attempt } with errorStrategy retry for variable-size inputs.
### **Applies To**
  - **/*.nf

## Peak Calling Without IDR

### **Id**
peak-calling-without-idr
### **Severity**
warning
### **Type**
regex
### **Pattern**
  - macs2(?![\s\S]{0,500}idr|IDR)
### **Message**
Peak calling without IDR analysis. ENCODE requires IDR for reproducibility.
### **Fix Action**
Add idr step after MACS2 peak calling for replicate concordance analysis.
### **Applies To**
  - **/*.nf
  - **/*.smk
  - **/*.sh

## Unsorted BAM Output

### **Id**
unsorted-bam-output
### **Severity**
warning
### **Type**
regex
### **Pattern**
  - bwa\s+mem(?![\s\S]{0,300}sort|samtools\s+sort)
  - bowtie2(?![\s\S]{0,300}sort|samtools\s+sort)
### **Message**
Alignment output is not sorted. Downstream tools require coordinate-sorted BAM.
### **Fix Action**
Pipe alignment output through samtools sort: bwa mem ref reads | samtools sort -o out.bam.
### **Applies To**
  - **/*.nf
  - **/*.smk
  - **/*.sh
