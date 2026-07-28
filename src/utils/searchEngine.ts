import Fuse from "fuse.js";
import { pipelines } from "../data/pipelines";

// ─── Doc glob imports (same pattern as DocsPage) ───

const SKILL_MD_MODULES = import.meta.glob("../../SKILL.md", {
  query: "?raw",
  import: "default",
  eager: true,
});
const REF_MD_MODULES = import.meta.glob("../../references/*.md", {
  query: "?raw",
  import: "default",
  eager: true,
});

const DOC_ENTRIES: { slug: string; title: string; source: "skill" | "ref" }[] = [
  { slug: "skill", title: "Bioinformatics Workflows — Skill 概述", source: "skill" },
  { slug: "study_designs", title: "研究设计标准流程", source: "ref" },
  { slug: "patterns", title: "代码模式 (Nextflow/Snakemake/WDL)", source: "ref" },
  { slug: "sharp_edges", title: "常见陷阱 (Sharp Edges)", source: "ref" },
  { slug: "validations", title: "代码审查规则", source: "ref" },
];

function getSkillMd(): string {
  const key = Object.keys(SKILL_MD_MODULES)[0];
  return (SKILL_MD_MODULES[key] as string) || "";
}

function getRefMd(filename: string): string {
  const key = Object.keys(REF_MD_MODULES).find((k) => k.includes(filename));
  if (!key) return "";
  return (REF_MD_MODULES[key] as string) || "";
}

// ─── Types ───

export interface SearchResult {
  type: "pipeline" | "doc";
  title: string;
  subtitle: string;
  match: string;
  route: string;
  score: number;
}

// ─── Pipeline index items ───

interface PipelineIndexItem {
  id: string;
  name: string;
  nameZH: string;
  overview: string;
  tags: string;
  stepText: string;
}

// ─── Doc index items ───

interface DocIndexItem {
  slug: string;
  title: string;
  section: string;
  text: string;
}

// ─── Build indexes (lazily) ───

let fusePipeline: Fuse<PipelineIndexItem> | null = null;
let fuseDoc: Fuse<DocIndexItem> | null = null;

function buildPipelineIndex(): PipelineIndexItem[] {
  return pipelines.map((p) => ({
    id: p.id,
    name: p.name,
    nameZH: p.nameZH,
    overview: p.overview,
    tags: p.tags.join(" "),
    stepText: p.sources
      .flatMap((s) =>
        s.steps.flatMap((step) =>
          [step.name, step.description, ...step.tools.map((t) => t.name)].join(" ")
        )
      )
      .join(" "),
  }));
}

function buildDocIndex(): DocIndexItem[] {
  const items: DocIndexItem[] = [];

  for (const entry of DOC_ENTRIES) {
    const raw =
      entry.source === "skill" ? getSkillMd() : getRefMd(`${entry.slug}.md`);
    if (!raw) continue;

    // Split by ## headings (level 2) for paragraph-level indexing
    const sections = raw.split(/^## /m);
    for (const section of sections) {
      const lines = section.split("\n");
      const heading = lines[0].trim();
      if (!heading) continue;
      const body = lines.slice(1).join("\n").trim();
      if (!body) continue;

      items.push({
        slug: entry.slug,
        title: entry.title,
        section: heading,
        text: body,
      });
    }

    // Also add as a single entry for broader matching
    items.push({
      slug: entry.slug,
      title: entry.title,
      section: "",
      text: raw,
    });
  }

  return items;
}

// ─── Public API ───

export function searchAll(query: string): SearchResult[] {
  if (!query || query.trim().length < 2) return [];

  if (!fusePipeline) {
    fusePipeline = new Fuse(buildPipelineIndex(), {
      keys: [
        { name: "name", weight: 0.3 },
        { name: "nameZH", weight: 0.3 },
        { name: "tags", weight: 0.2 },
        { name: "overview", weight: 0.1 },
        { name: "stepText", weight: 0.1 },
      ],
      threshold: 0.4,
      includeScore: true,
    });
  }

  if (!fuseDoc) {
    fuseDoc = new Fuse(buildDocIndex(), {
      keys: [
        { name: "title", weight: 0.3 },
        { name: "section", weight: 0.3 },
        { name: "text", weight: 0.4 },
      ],
      threshold: 0.4,
      includeScore: true,
    });
  }

  const results: SearchResult[] = [];

  // Pipeline hits
  const pipelineHits = fusePipeline.search(query, { limit: 10 });
  for (const hit of pipelineHits) {
    results.push({
      type: "pipeline",
      title: hit.item.nameZH,
      subtitle: hit.item.name,
      match: hit.item.overview.slice(0, 120),
      route: `/pipeline/${hit.item.id}`,
      score: hit.score ?? 0,
    });
  }

  // Doc hits
  const docHits = fuseDoc.search(query, { limit: 10 });
  for (const hit of docHits) {
    const anchor = hit.item.section
      ? `#${hit.item.section.toLowerCase().replace(/\s+/g, "-")}`
      : "";
    results.push({
      type: "doc",
      title: hit.item.title,
      subtitle: hit.item.section || "",
      match: hit.item.text.slice(0, 200),
      route: `/docs/${hit.item.slug}${anchor}`,
      score: hit.score ?? 0,
    });
  }

  // Sort by score ascending (lower is better in Fuse)
  results.sort((a, b) => a.score - b.score);

  return results;
}
