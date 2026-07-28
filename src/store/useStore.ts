import { create } from "zustand";
import type { PipelineDefinition, PipelineStep } from "../types/pipeline";
import { pipelines, categoryLabels as catLabels } from "../data/pipelines";

export const categoryLabels = catLabels;

interface FlowSeqState {
  searchQuery: string;
  selectedCategory: string | null;
  selectedPipeline: PipelineDefinition | null;
  selectedSourceId: string;
  selectedStep: PipelineStep | null;
  pipelines: PipelineDefinition[];
  searchOverlayOpen: boolean;

  setSearchQuery: (q: string) => void;
  setSelectedCategory: (c: string | null) => void;
  selectPipeline: (id: string) => void;
  setSelectedSourceId: (id: string) => void;
  setSelectedStep: (step: PipelineStep | null) => void;
  toggleSearchOverlay: () => void;
  setSearchOverlayOpen: (open: boolean) => void;
}

export const useStore = create<FlowSeqState>((set) => ({
  searchQuery: "",
  selectedCategory: null,
  selectedPipeline: null,
  selectedSourceId: "",
  selectedStep: null,
  pipelines,
  searchOverlayOpen: false,

  setSearchQuery: (q) => set({ searchQuery: q }),
  setSelectedCategory: (c) => set({ selectedCategory: c }),

  selectPipeline: (id) => {
    const p = pipelines.find((p) => p.id === id) || null;
    const sourceId = p?.sources[0]?.id || "";
    set({ selectedPipeline: p, selectedSourceId: sourceId, selectedStep: null });
  },

  setSelectedSourceId: (id) => set({ selectedSourceId: id, selectedStep: null }),
  setSelectedStep: (step) => set({ selectedStep: step }),
  toggleSearchOverlay: () => set((s) => ({ searchOverlayOpen: !s.searchOverlayOpen })),
  setSearchOverlayOpen: (open) => set({ searchOverlayOpen: open }),
}));
