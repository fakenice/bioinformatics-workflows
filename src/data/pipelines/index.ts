import type { PipelineDefinition } from "../../types/pipeline";
import familytriowgs from "./family-trio-wgs.json";
import gwas from "./gwas.json";
import mendelianrandomization from "./mendelian-randomization.json";
import prs from "./prs.json";
import rarevariant from "./rare-variant.json";
import wgsgermline from "./wgs-germline.json";
import wgssomatic from "./wgs-somatic.json";
import wes from "./wes.json";
import rnaseq from "./rna-seq.json";
import scrnaseq from "./scrna-seq.json";
import chipseq from "./chip-seq.json";
import wgbs from "./wgbs.json";
import metagenomics from "./metagenomics.json";
import pipe_16s from "./16s.json";
export const pipelines: PipelineDefinition[] = [
  familytriowgs,
  gwas,
  mendelianrandomization,
  prs,
  rarevariant,
  wgsgermline,
  wgssomatic,
  wes,
  rnaseq,
  scrnaseq,
  chipseq,
  wgbs,
  metagenomics,
  pipe_16s,
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
