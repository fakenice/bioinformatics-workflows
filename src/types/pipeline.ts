export interface ToolInfo {
  name: string;
  version: string;
  params: string;
  docker: string;
}

export interface Reference {
  title: string;
  url: string;
  type: "official" | "community" | "paper";
}

export interface PipelineStep {
  id: string;
  name: string;
  description: string;
  tools: ToolInfo[];
  notes: string;
  position: { x: number; y: number };
}

export interface PipelineSource {
  id: string;
  name: string;
  type: "official" | "community" | "paper";
  url: string;
  steps: PipelineStep[];
  references: Reference[];
}

export type Category = "dna" | "rna" | "epigenetics" | "microbiome";

export interface PipelineDefinition {
  id: string;
  name: string;
  nameZH: string;
  category: Category;
  tags: string[];
  overview: string;
  icon: string;
  sources: PipelineSource[];
}
