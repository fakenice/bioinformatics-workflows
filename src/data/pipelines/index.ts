import type { PipelineDefinition } from "../../types/pipeline";
import wgsGermline from "./wgs-germline.json";
import wgsSomatic from "./wgs-somatic.json";
import wes from "./wes.json";
import gwas from "./gwas.json";
import rnaSeq from "./rna-seq.json";
import scrnaSeq from "./scrna-seq.json";
import chipSeq from "./chip-seq.json";
import wgbs from "./wgbs.json";
import metagenomics from "./metagenomics.json";
import rrna16s from "./16s.json";

export const pipelines: PipelineDefinition[] = [
  wgsGermline,
  wgsSomatic,
  wes,
  gwas,
  rnaSeq,
  scrnaSeq,
  chipSeq,
  wgbs,
  metagenomics,
  rrna16s,
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
