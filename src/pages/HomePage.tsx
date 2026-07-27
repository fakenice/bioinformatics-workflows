import { useMemo } from "react";
import { useStore } from "../store/useStore";
import CategoryTabs from "../components/CategoryTabs";
import PipelineCard from "../components/PipelineCard";
import type { PipelineDefinition } from "../types/pipeline";

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
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-white mb-3">
          生物信息学分析流程导航
        </h1>
        <p className="text-slate-400 max-w-lg mx-auto">
          选择分析场景，查看标准化流程、推荐工具与权威文献。覆盖 DNA、RNA、表观遗传和微生物四大领域。
        </p>
      </div>

      <div className="mb-8">
        <CategoryTabs />
      </div>

      <div className="space-y-10">
        {dnaPipeline.length > 0 && (
          <Section title="DNA 分析" items={dnaPipeline} />
        )}
        {rnaPipeline.length > 0 && (
          <Section title="RNA 分析" items={rnaPipeline} />
        )}
        {epiPipeline.length > 0 && (
          <Section title="表观遗传" items={epiPipeline} />
        )}
        {microPipeline.length > 0 && (
          <Section title="微生物组" items={microPipeline} />
        )}
        {filtered.length === 0 && (
          <div className="text-center py-16 text-slate-500">
            <p className="text-lg">未找到匹配的分析流程</p>
            <p className="text-sm mt-1">尝试更换搜索词或分类筛选</p>
          </div>
        )}
      </div>
    </div>
  );
}

function Section({
  title,
  items,
}: {
  title: string;
  items: PipelineDefinition[];
}) {
  return (
    <div>
      <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">
        {title}
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {items.map((p) => (
          <PipelineCard key={p.id} pipeline={p} />
        ))}
      </div>
    </div>
  );
}
