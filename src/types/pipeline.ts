export interface ToolInfo {
  name: string;
  version: string;
  params: string;
  docker: string;
  notes?: string;
  notesEn?: string;
}

export interface Reference {
  title: string;
  url: string;
  type: "official" | "community" | "paper";
}

export interface PipelineStep {
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

export interface PipelineSource {
  id: string;
  name: string;
  nameEn?: string;
  type: "official" | "community" | "paper";
  url: string;
  steps: PipelineStep[];
  references: Reference[];
}

export type Category = "dna" | "rna" | "epigenetics" | "microbiome";

export interface ChangelogEntry {
  version: string;
  date: string;
  changes: string[];
}

export interface PipelineDefinition {
  id: string;
  name: string;
  nameZH: string;
  category: Category;
  tags: string[];
  overview: string;
  overviewEn?: string;
  icon: string;
  sources: PipelineSource[];
  version?: string;
  changelog?: ChangelogEntry[];
}
