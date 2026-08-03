import { create } from "zustand";
import { pipelines as allPipelines, categoryTree as defaultCategoryTree } from "../data/pipelines";
import type { PipelineDefinition, PipelineStep } from "../types/pipeline";
import type { CategoryNode } from "../data/pipelines";

type Language = "en" | "zh";

// ── Hidden / Order persistence ─────────────────────────────────

function loadHidden(): string[] {
  try {
    const raw = localStorage.getItem("flowseq-hidden");
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHidden(ids: string[]) {
  localStorage.setItem("flowseq-hidden", JSON.stringify(ids));
}

// ── Pipeline deletion persistence ──────────────────────────────

function loadDeletedPipelines(): string[] {
  try {
    const raw = localStorage.getItem("flowseq-deleted");
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveDeletedPipelines(ids: string[]) {
  localStorage.setItem("flowseq-deleted", JSON.stringify(ids));
}

// ── Pipeline category override persistence ─────────────────────

function loadCategoryMap(): Record<string, string> {
  try {
    const raw = localStorage.getItem("flowseq-category-map");
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveCategoryMap(map: Record<string, string>) {
  localStorage.setItem("flowseq-category-map", JSON.stringify(map));
}

// ── Category overrides persistence ─────────────────────────────

interface CategoryOverrides {
  addedParents: Record<string, CategoryNode>;
  addedChildren: Record<string, { parentId: string; childId: string; label: string; labelZH: string }>;
  deletedChildren: string[];
  deletedParents: string[];
}

function loadCategoryOverrides(): CategoryOverrides {
  try {
    const raw = localStorage.getItem("flowseq-categories");
    const parsed = raw ? JSON.parse(raw) : {};
    return {
      addedParents: parsed.addedParents || {},
      addedChildren: parsed.addedChildren || {},
      deletedChildren: parsed.deletedChildren || [],
      deletedParents: parsed.deletedParents || [],
    };
  } catch {
    return { addedParents: {}, addedChildren: {}, deletedChildren: [], deletedParents: [] };
  }
}

function saveCategoryOverrides(overrides: CategoryOverrides) {
  localStorage.setItem("flowseq-categories", JSON.stringify(overrides));
}

function mergeCategoryTree(
  defaultTree: Record<string, CategoryNode>,
  overrides: CategoryOverrides,
): Record<string, CategoryNode> {
  const merged: Record<string, CategoryNode> = JSON.parse(JSON.stringify(defaultTree));

  // remove deleted top-level parents (built-in)
  for (const pid of overrides.deletedParents) {
    delete merged[pid];
  }

  // add user-created top-level categories
  for (const [pid, node] of Object.entries(overrides.addedParents)) {
    merged[pid] = {
      label: node.label,
      labelZH: node.labelZH,
      accent: node.accent,
      children: node.children ? { ...node.children } : {},
    };
  }

  // add user-created sub-categories to their parents
  for (const [, info] of Object.entries(overrides.addedChildren)) {
    const parent = merged[info.parentId];
    if (parent) {
      if (!parent.children) parent.children = {};
      parent.children[info.childId] = { label: info.label, labelZH: info.labelZH };
    }
  }

  // remove deleted sub-categories
  for (const childId of overrides.deletedChildren) {
    const parentId = childId.split(".")[0];
    const parent = merged[parentId];
    if (parent?.children) {
      delete parent.children[childId];
    }
  }

  return merged;
}

// ── Store interface ────────────────────────────────────────────

interface State {
  lang: Language;
  setLang: (lang: Language) => void;

  pipelines: PipelineDefinition[];
  selectedCategory: string | null;
  setSelectedCategory: (cat: string | null) => void;

  searchQuery: string;
  setSearchQuery: (q: string) => void;
  searchOverlayOpen: boolean;
  setSearchOverlayOpen: (open: boolean) => void;

  hiddenPipelines: string[];
  toggleHidden: (id: string) => void;
  movePipeline: (fromIndex: number, toIndex: number) => void;
  resetOrder: () => void;
  deletePipeline: (id: string) => void;
  changePipelineCategory: (id: string, newCategory: string) => void;

  selectedStep: PipelineStep | null;
  setSelectedStep: (step: PipelineStep | null) => void;
  selectedPipeline: PipelineDefinition | null;
  selectPipeline: (id: string) => void;
  selectedSourceId: string | null;
  setSelectedSourceId: (id: string) => void;

  // category management
  categoryTree: Record<string, CategoryNode>;
  addSubCategory: (parentId: string, childId: string, label: string, labelZH: string) => void;
  deleteSubCategory: (childId: string) => void;
  addTopLevelCategory: (id: string, label: string, labelZH: string, accent: string) => void;
  deleteTopLevelCategory: (pid: string) => void;
}

// ── Store creation ─────────────────────────────────────────────

export const useStore = create<State>()((set, get) => {
  const hidden = loadHidden();
  const deletedPipelines = loadDeletedPipelines();
  const categoryMap = loadCategoryMap();
  const categoryOverrides = loadCategoryOverrides();
  const categoryTree = mergeCategoryTree(defaultCategoryTree, categoryOverrides);

  const initialPipelines = allPipelines
    .filter((p) => !deletedPipelines.includes(p.id))
    .map((p) => (categoryMap[p.id] ? { ...p, category: categoryMap[p.id] } : p));

  return {
    lang: (localStorage.getItem("flowseq-lang") || "en") as Language,
    setLang: (lang) => {
      localStorage.setItem("flowseq-lang", lang);
      set({ lang });
    },

    pipelines: initialPipelines,
    selectedCategory: null,
    setSelectedCategory: (cat) => set({ selectedCategory: cat }),

    searchQuery: "",
    setSearchQuery: (q) => set({ searchQuery: q }),
    searchOverlayOpen: false,
    setSearchOverlayOpen: (open) => set({ searchOverlayOpen: open }),

    hiddenPipelines: hidden,
    toggleHidden: (id) => {
      const s = get();
      const idx = s.hiddenPipelines.indexOf(id);
      const next = idx >= 0
        ? s.hiddenPipelines.filter((_, i) => i !== idx)
        : [...s.hiddenPipelines, id];
      saveHidden(next);
      set({ hiddenPipelines: next });
    },

    movePipeline: (from, to) => {
      const s = get();
      const next = [...s.pipelines];
      const [removed] = next.splice(from, 1);
      next.splice(to, 0, removed);
      set({ pipelines: next });
    },

    resetOrder: () => {
      saveHidden([]);
      saveDeletedPipelines([]);
      saveCategoryMap({});
      const categoryOverrides = loadCategoryOverrides();
      categoryOverrides.deletedParents = [];
      saveCategoryOverrides(categoryOverrides);
      const categoryTree = mergeCategoryTree(defaultCategoryTree, categoryOverrides);
      set({ pipelines: allPipelines, hiddenPipelines: [], categoryTree });
    },

    deletePipeline: (id) => {
      const deleted = loadDeletedPipelines();
      if (!deleted.includes(id)) deleted.push(id);
      saveDeletedPipelines(deleted);
      set((s) => ({ pipelines: s.pipelines.filter((p) => p.id !== id) }));
    },

    changePipelineCategory: (id, newCategory) => {
      const map = loadCategoryMap();
      map[id] = newCategory;
      saveCategoryMap(map);
      set((s) => ({
        pipelines: s.pipelines.map((p) => (p.id === id ? { ...p, category: newCategory } : p)),
      }));
    },

    selectedStep: null,
    setSelectedStep: (step) => set({ selectedStep: step }),

    selectedPipeline: null,
    selectPipeline: (id) => {
      const s = get();
      const found = s.pipelines.find((p) => p.id === id);
      if (found) {
        set({ selectedPipeline: found, selectedSourceId: found.sources[0]?.id ?? null });
      }
    },

    selectedSourceId: null,
    setSelectedSourceId: (id) => set({ selectedSourceId: id }),

    // ── Category management ────────────────────────────────────
    categoryTree,

    addSubCategory: (parentId, childId, label, labelZH) => {
      const overrides = loadCategoryOverrides();
      overrides.addedChildren[childId] = { parentId, childId, label, labelZH };
      // also remove from deleted list if it was previously deleted
      overrides.deletedChildren = overrides.deletedChildren.filter((d) => d !== childId);
      saveCategoryOverrides(overrides);
      set({ categoryTree: mergeCategoryTree(defaultCategoryTree, overrides) });
    },

    deleteSubCategory: (childId) => {
      const overrides = loadCategoryOverrides();
      // remove from added children if present
      if (overrides.addedChildren[childId]) {
        delete overrides.addedChildren[childId];
      }
      // also track as deleted (handles built-in children)
      if (!overrides.deletedChildren.includes(childId)) {
        overrides.deletedChildren.push(childId);
      }
      saveCategoryOverrides(overrides);
      set({ categoryTree: mergeCategoryTree(defaultCategoryTree, overrides) });
    },

    addTopLevelCategory: (id, label, labelZH, accent) => {
      const overrides = loadCategoryOverrides();
      overrides.addedParents[id] = {
        label,
        labelZH,
        accent,
        children: {},
      };
      saveCategoryOverrides(overrides);
      set({ categoryTree: mergeCategoryTree(defaultCategoryTree, overrides) });
    },

    deleteTopLevelCategory: (pid) => {
      const overrides = loadCategoryOverrides();
      if (overrides.addedParents[pid]) {
        // user-added: remove from addedParents
        delete overrides.addedParents[pid];
      } else {
        // built-in: track as deleted
        if (!overrides.deletedParents.includes(pid)) {
          overrides.deletedParents.push(pid);
        }
      }
      saveCategoryOverrides(overrides);
      set({ categoryTree: mergeCategoryTree(defaultCategoryTree, overrides) });
    },
  };
});
