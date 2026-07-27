import { useStore } from "../store/useStore";
import { categoryLabels } from "../data/pipelines";

export default function CategoryTabs() {
  const { selectedCategory, setSelectedCategory } = useStore();
  const categories = ["dna", "rna", "epigenetics", "microbiome"];

  return (
    <div className="flex gap-2 flex-wrap">
      <button
        onClick={() => setSelectedCategory(null)}
        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
          selectedCategory === null
            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
            : "bg-slate-800 text-slate-400 border border-slate-700 hover:border-slate-600"
        }`}
      >
        全部
      </button>
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => setSelectedCategory(cat)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            selectedCategory === cat
              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
              : "bg-slate-800 text-slate-400 border border-slate-700 hover:border-slate-600"
          }`}
        >
          {categoryLabels[cat] || cat}
        </button>
      ))}
    </div>
  );
}
