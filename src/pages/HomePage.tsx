import { useMemo } from "react";
import { useT } from "../i18n";
import { useStore } from "../store/useStore";
import CategoryTabs from "../components/CategoryTabs";
import PipelineCard from "../components/PipelineCard";
import type { PipelineDefinition } from "../types/pipeline";

function groupBySubCategory(pips: PipelineDefinition[]) {
  const groups: Record<string, PipelineDefinition[]> = {};
  for (const p of pips) {
    if (!groups[p.category]) groups[p.category] = [];
    groups[p.category].push(p);
  }
  return groups;
}

export default function HomePage() {
  const t = useT();
  const { searchQuery, selectedCategory, hiddenPipelines, pipelines, categoryTree } = useStore();

  function getAccent(cat: string): string {
    const parent = cat.split(".")[0];
    return categoryTree[parent]?.accent || "var(--color-accent)";
  }

  const filtered = useMemo(() => {
    return pipelines.filter((p) => {
      // category filter
      if (selectedCategory) {
        if (selectedCategory.includes(".")) {
          if (p.category !== selectedCategory) return false;
        } else {
          // parent-only filter
          const tree = categoryTree[selectedCategory];
          const children = tree?.children ? Object.keys(tree.children) : [];
          if (p.category !== selectedCategory && !children.includes(p.category)) return false;
        }
      }

      // hidden filter
      if (hiddenPipelines.includes(p.id)) return false;

      // search filter
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        p.name.toLowerCase().includes(q) ||
        p.nameZH.toLowerCase().includes(q) ||
        p.tags.some((t) => t.toLowerCase().includes(q)) ||
        (p.overviewEn || p.overview).toLowerCase().includes(q) ||
        p.overview.toLowerCase().includes(q) ||
        p.sources.some((s) =>
          s.steps.some(
            (st) =>
              st.name.toLowerCase().includes(q) ||
              st.tools.some((t) => t.name.toLowerCase().includes(q))
          )
        )
      );
    });
  }, [pipelines, searchQuery, selectedCategory, hiddenPipelines, categoryTree]);

  const groups = groupBySubCategory(filtered);
  const groupKeys = Object.keys(groups);

  function catLabel(cat: string): string {
    const key = `categories.${cat}`;
    const trans = t(key);
    return trans !== key ? trans : cat;
  }

  if (filtered.length === 0) {
    return (
      <div className="min-h-screen px-4 py-10" style={{ background: "var(--color-page)" }}>
        <div className="max-w-5xl mx-auto">
          <header className="mb-10">
            <h1 className="text-[28px] font-bold tracking-tight leading-tight" style={{ color: "var(--color-text-primary)" }}>
              {t("home.title")}
            </h1>
            <p className="mt-2.5 text-[15px] max-w-lg leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>
              {t("home.subtitle")}
            </p>
          </header>
          <div className="mb-8"><CategoryTabs /></div>
          <div className="text-center py-24" style={{ color: "var(--color-text-tertiary)" }}>
            <p className="text-base">{t("home.noResults")}</p>
            <p className="text-sm mt-1.5">{t("home.noResultsHint")}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-4 py-10" style={{ background: "var(--color-page)" }}>
      <div className="max-w-5xl mx-auto">
        <header className="mb-10">
          <h1 className="text-[28px] font-bold tracking-tight leading-tight" style={{ color: "var(--color-text-primary)" }}>
            {t("home.title")}
          </h1>
          <p className="mt-2.5 text-[15px] max-w-lg leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>
            {t("home.subtitle")}
          </p>
        </header>

        <div className="mb-8"><CategoryTabs /></div>

        {groupKeys.map((cat) => {
          const items = groups[cat];
          const accent = getAccent(cat);
          return (
            <div key={cat} style={{ marginBottom: 48 }}>
              <div className="flex items-center gap-2.5 mb-4">
                <div style={{ width: 20, height: 3, borderRadius: 2, background: accent }} />
                <h2 className="text-xs font-bold uppercase tracking-widest" style={{ color: "var(--color-text-tertiary)" }}>
                  {catLabel(cat)}
                  <span className="ml-2 font-normal" style={{ color: "var(--color-text-tertiary)" }}>
                    ({items.length})
                  </span>
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {items.map((p) => (
                  <PipelineCard key={p.id} pipeline={p} accent={accent} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
