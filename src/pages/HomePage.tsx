import { useMemo } from "react";
import { useT } from "../i18n";
import { useStore } from "../store/useStore";
import CategoryTabs from "../components/CategoryTabs";
import PipelineCard from "../components/PipelineCard";
import type { PipelineDefinition } from "../types/pipeline";

const CATEGORY_META: Record<string, { label: string; accent: string }> = {
  dna: { label: "categories.dna", accent: "var(--color-node-dna)" },
  rna: { label: "categories.rna", accent: "var(--color-node-rna)" },
  epigenetics: { label: "categories.epigenetics", accent: "var(--color-node-epi)" },
  microbiome: { label: "categories.microbiome", accent: "var(--color-node-micro)" },
};

function Section({
  title,
  items,
  accent,
  t,
}: {
  title: string;
  items: PipelineDefinition[];
  accent: string;
  t: (key: string) => string;
}) {
  return (
    <div style={{ marginBottom: 48 }}>
      <div className="flex items-center gap-2.5 mb-4">
        <div
          style={{
            width: 20,
            height: 3,
            borderRadius: 2,
            background: accent,
          }}
        />
        <h2
          className="text-xs font-bold uppercase tracking-widest"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {t(title)}
        </h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map((p) => (
          <PipelineCard key={p.id} pipeline={p} accent={accent} />
        ))}
      </div>
    </div>
  );
}

export default function HomePage() {
  const t = useT();
  const { searchQuery, selectedCategory, pipelines } = useStore();

  const filtered = useMemo(() => {
    return pipelines.filter((p) => {
      if (selectedCategory && p.category !== selectedCategory) return false;
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        p.name.toLowerCase().includes(q) ||
        p.nameZH.toLowerCase().includes(q) ||
        p.tags.some((t) => t.toLowerCase().includes(q)) ||
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
  }, [pipelines, searchQuery, selectedCategory]);

  const dnaPipeline = filtered.filter((p) => p.category === "dna");
  const rnaPipeline = filtered.filter((p) => p.category === "rna");
  const epiPipeline = filtered.filter((p) => p.category === "epigenetics");
  const microPipeline = filtered.filter((p) => p.category === "microbiome");

  return (
    <div className="min-h-screen px-4 py-10" style={{ background: "var(--color-page)" }}>
      <div className="max-w-5xl mx-auto">
        <header className="mb-10">
          <h1
            className="text-[28px] font-bold tracking-tight leading-tight"
            style={{ color: "var(--color-text-primary)" }}
          >
            {t("home.title")}
          </h1>
          <p
            className="mt-2.5 text-[15px] max-w-lg leading-relaxed"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {t("home.subtitle")}
          </p>
        </header>

        <div className="mb-8">
          <CategoryTabs />
        </div>

        {dnaPipeline.length > 0 && (
          <Section title="categories.dna" items={dnaPipeline} t={t} accent={CATEGORY_META.dna.accent} />
        )}
        {rnaPipeline.length > 0 && (
          <Section title="categories.rna" items={rnaPipeline} t={t} accent={CATEGORY_META.rna.accent} />
        )}
        {epiPipeline.length > 0 && (
          <Section title="categories.epigenetics" items={epiPipeline} t={t} accent={CATEGORY_META.epigenetics.accent} />
        )}
        {microPipeline.length > 0 && (
          <Section title="categories.microbiome" items={microPipeline} t={t} accent={CATEGORY_META.microbiome.accent} />
        )}

        {filtered.length === 0 && (
          <div className="text-center py-24" style={{ color: "var(--color-text-tertiary)" }}>
            <p className="text-base">{t("home.noResults")}</p>
            <p className="text-sm mt-1.5">{t("home.noResultsHint")}</p>
          </div>
        )}
      </div>
    </div>
  );
}
