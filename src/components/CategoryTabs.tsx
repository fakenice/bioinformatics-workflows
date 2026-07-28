import { useStore } from "../store/useStore";
import { useT } from "../i18n";

const CAT_ACCENTS: Record<string, string> = {
  dna: "var(--color-node-dna)",
  rna: "var(--color-node-rna)",
  epigenetics: "var(--color-node-epi)",
  microbiome: "var(--color-node-micro)",
};

const categories = ["dna", "rna", "epigenetics", "microbiome"];

export default function CategoryTabs() {
  const { selectedCategory, setSelectedCategory } = useStore();
  const t = useT();

  return (
    <div className="flex gap-1 flex-wrap">
      <button
        onClick={() => setSelectedCategory(null)}
        className="relative px-3.5 py-2 text-sm font-medium transition-colors"
        style={
          selectedCategory === null
            ? { color: "var(--color-accent)" }
            : { color: "var(--color-text-tertiary)" }
        }
      >
        {t("categories.all")}
        {selectedCategory === null && (
          <span
            className="absolute bottom-0 left-1/2 -translate-x-1/2 w-5 h-0.5 rounded-full"
            style={{ background: "var(--color-accent)" }}
          />
        )}
      </button>
      {categories.map((cat) => {
        const accent = CAT_ACCENTS[cat];
        const isActive = selectedCategory === cat;
        return (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className="relative px-3.5 py-2 text-sm font-medium transition-colors"
            style={{
              color: isActive ? accent : "var(--color-text-tertiary)",
            }}
          >
            {t(`categories.${cat}`)}
            {isActive && (
              <span
                className="absolute bottom-0 left-1/2 -translate-x-1/2 w-5 h-0.5 rounded-full"
                style={{ background: accent }}
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
