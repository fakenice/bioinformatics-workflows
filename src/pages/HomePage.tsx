import { useMemo } from "react";
import { useStore } from "../store/useStore";
import CategoryTabs from "../components/CategoryTabs";
import PipelineCard from "../components/PipelineCard";
import type { PipelineDefinition } from "../types/pipeline";

const CATEGORY_META: Record<string, { label: string; accent: string }> = {
  dna: { label: "DNA 分析", accent: "var(--color-node-dna)" },
  rna: { label: "RNA 分析", accent: "var(--color-node-rna)" },
  epigenetics: { label: "表观遗传", accent: "var(--color-node-epi)" },
  microbiome: { label: "微生物组", accent: "var(--color-node-micro)" },
};

function Section({
  title,
  items,
  accent,
}: {
  title: string;
  items: PipelineDefinition[];
  accent: string;
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
          {title}
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
            生物信息学分析流程导航
          </h1>
          <p
            className="mt-2.5 text-[15px] max-w-lg leading-relaxed"
            style={{ color: "var(--color-text-secondary)" }}
          >
            选择分析场景，查看标准化流程、推荐工具与权威文献。覆盖 DNA、RNA、表观遗传和微生物四大领域。
          </p>
        </header>

        <div className="mb-8">
          <CategoryTabs />
        </div>

        {dnaPipeline.length > 0 && (
          <Section title="DNA 分析" items={dnaPipeline} accent={CATEGORY_META.dna.accent} />
        )}
        {rnaPipeline.length > 0 && (
          <Section title="RNA 分析" items={rnaPipeline} accent={CATEGORY_META.rna.accent} />
        )}
        {epiPipeline.length > 0 && (
          <Section title="表观遗传" items={epiPipeline} accent={CATEGORY_META.epigenetics.accent} />
        )}
        {microPipeline.length > 0 && (
          <Section title="微生物组" items={microPipeline} accent={CATEGORY_META.microbiome.accent} />
        )}

        {filtered.length === 0 && (
          <div className="text-center py-24" style={{ color: "var(--color-text-tertiary)" }}>
            <p className="text-base">没有找到匹配的分析流程</p>
            <p className="text-sm mt-1.5">尝试使用其他关键词或切换分类筛选</p>
          </div>
        )}
      </div>
    </div>
  );
}
