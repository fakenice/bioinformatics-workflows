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

// ── Category Tree ──────────────────────────────────────────────

export interface CategoryNode {
  label: string;
  labelZH: string;
  children?: Record<string, { label: string; labelZH: string }>;
  accent?: string;
}

/** Built-in default category tree (before project-level overrides). */
export const defaultCategoryTree: Record<string, CategoryNode> = {
  dna: {
    label: "DNA",
    labelZH: "DNA",
    accent: "var(--color-node-dna)",
    children: {
      "dna.germline": { label: "Germline Variant", labelZH: "种系变异" },
      "dna.somatic": { label: "Somatic Variant", labelZH: "体细胞变异" },
      "dna.structural": { label: "Structural Variant", labelZH: "结构变异" },
      "dna.association": { label: "Association & PRS", labelZH: "关联分析与 PRS" }
    },
  },
  rna: {
    label: "RNA",
    labelZH: "RNA",
    accent: "var(--color-node-rna)",
    children: {
      "rna.bulk": { label: "Bulk RNA-seq", labelZH: "常规转录组" },
      "rna.singlecell": { label: "Single-cell", labelZH: "单细胞" }
    },
  },
  epigenetics: {
    label: "Epigenetics",
    labelZH: "表观遗传",
    accent: "var(--color-node-epi)",
    children: {
      "epigenetics.chip": { label: "ChIP-seq / CUT&RUN", labelZH: "ChIP-seq" },
      "epigenetics.methyl": { label: "Methylation", labelZH: "甲基化" }
    },
  },
  microbiome: {
    label: "Microbiome",
    labelZH: "微生物组",
    accent: "var(--color-node-micro)",
    children: {
      "microbiome.meta": { label: "Metagenomics", labelZH: "宏基因组" },
      "microbiome.amplicon": { label: "16S / Amplicon", labelZH: "扩增子" }
    },
  }
};

/** Merged category tree (default + project-level overrides from category-overrides.json). */
export const categoryTree: Record<string, CategoryNode> = {
  dna: {
    label: "DNA",
    labelZH: "DNA",
    accent: "var(--color-node-dna)",
    children: {
      "dna.germline": { label: "Germline Variant", labelZH: "种系变异" },
      "dna.somatic": { label: "Somatic Variant", labelZH: "体细胞变异" },
      "dna.structural": { label: "Structural Variant", labelZH: "结构变异" },
      "dna.association": { label: "Association & PRS", labelZH: "关联分析与 PRS" }
    },
  },
  rna: {
    label: "RNA",
    labelZH: "RNA",
    accent: "var(--color-node-rna)",
    children: {
      "rna.bulk": { label: "Bulk RNA-seq", labelZH: "常规转录组" },
      "rna.singlecell": { label: "Single-cell", labelZH: "单细胞" }
    },
  },
  epigenetics: {
    label: "Epigenetics",
    labelZH: "表观遗传",
    accent: "var(--color-node-epi)",
    children: {
      "epigenetics.chip": { label: "ChIP-seq / CUT&RUN", labelZH: "ChIP-seq" },
      "epigenetics.methyl": { label: "Methylation", labelZH: "甲基化" }
    },
  },
  microbiome: {
    label: "Microbiome",
    labelZH: "微生物组",
    accent: "var(--color-node-micro)",
    children: {
      "microbiome.meta": { label: "Metagenomics", labelZH: "宏基因组" },
      "microbiome.amplicon": { label: "16S / Amplicon", labelZH: "扩增子" }
    },
  }
};

export const categoryLabels: Record<string, string> = {};
for (const [parentId, parent] of Object.entries(categoryTree)) {
  categoryLabels[parentId] = parent.labelZH;
  if (parent.children) {
    for (const [childId, child] of Object.entries(parent.children)) {
      categoryLabels[childId] = child.labelZH;
    }
  }
}

export const categoryIcons: Record<string, string> = {
  dna: "dna",
  rna: "microscope",
  epigenetics: "layers",
  microbiome: "bacteria",
};
