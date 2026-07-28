import { useStore } from "../store/useStore";
import { categoryLabels } from "../data/pipelines";

const CAT_ACCENTS: Record<string, string> = {
  dna: "var(--color-node-dna)",
  rna: "var(--color-node-rna)",
  epigenetics: "var(--color-node-epi)",
  microbiome: "var(--color-node-micro)",
};

const categories = ["dna", "rna", "epigenetics", "microbiome"];

export default function CategoryTabs() {
  const { selectedCategory, setSelectedCategory } = useStore();

  return (
    <div className="flex gap-2 flex-wrap">
      <button
        onClick={() => setSelectedCategory(null)}
        className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
        style={
          selectedCategory === null
            ? { background: "var(--color-accent-muted)", color: "var(--color-accent)", border: "1px solid var(--color-accent)" }
            : { background: "var(--color-surface)", color: "var(--color-text-tertiary)", border: "1px solid var(--color-border)" }
        }
      >
        全部
      </button>
      {categories.map((cat) => {
        const accent = CAT_ACCENTS[cat];
        return (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={
              selectedCategory === cat
                ? { background: `color-mix(in oklch, ${accent} 12%, transparent)`, color: accent, border: `1px solid ${accent}` }
                : { background: "var(--color-surface)", color: "var(--color-text-tertiary)", border: "1px solid var(--color-border)" }
            }
          >
            {categoryLabels[cat] || cat}
          </button>
        );
      })}
    </div>
  );
}
