const en = {
  header: {
    searchPlaceholder: "Search pipelines, tools… (Ctrl+K)",
    docs: "Skill Docs",
  },
  home: {
    title: "Bioinformatics Pipeline Navigator",
    subtitle:
      "Choose an analysis scenario to explore standardized workflows, recommended tools, and authoritative references. Covers DNA, RNA, epigenetics, and microbiome domains.",
    searchPlaceholder: "Search pipelines, tools… (Ctrl+K)",
    noResults: "No matching pipelines found",
    noResultsHint: "Try different keywords or switch category filters",
  },
  categories: {
    all: "All",
    dna: "DNA Analysis",
    rna: "RNA Analysis",
    epigenetics: "Epigenetics",
    microbiome: "Microbiome",
  },
  pipeline: {
    back: "Back",
    export: "Export .nf",
    compare: "Compare",
    version: "v",
    loading: "Loading pipeline...",
    compareMode: "Compare",
  },
  export: {
    title: "Export Nextflow Script",
    copy: "Copy Script",
    copied: "Copied!",
    download: "Download .nf",
    close: "Close",
  },
  search: {
    title: "Search",
    placeholder: "Search pipelines, docs…",
    pipelines: "Pipelines",
    docs: "Docs",
    noResults: "No results found",
    close: "Close",
  },
  compare: {
    title: "Workflow Comparison",
    singleSourceNotice: "This pipeline has only one reference source, unable to compare.",
    backToPipeline: "Back to Pipeline",
    noCorrespondingStep: "(No corresponding step)",
  },
  docs: {
    sidebarTitle: "Skill Docs",
    footerNote:
      "This page renders SKILL.md + references/ from the Skill repository, sharing the same data source as FlowSeq pipelines.",
  },
};

export default en;
export type I18nStrings = typeof en;
