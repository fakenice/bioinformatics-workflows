import { useStore } from "../store/useStore";

export default function SourceSwitcher() {
  const { selectedPipeline, selectedSourceId, setSelectedSourceId } = useStore();

  if (!selectedPipeline || selectedPipeline.sources.length <= 1) return null;

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs shrink-0" style={{ color: "var(--color-text-tertiary)" }}>
        参考来源      </span>
      <div
        className="flex rounded-lg p-0.5 gap-0.5"
        style={{ background: "var(--color-surface-alt)", border: "1px solid var(--color-border)" }}
      >
        {selectedPipeline.sources.map((src) => (
          <button
            key={src.id}
            onClick={() => setSelectedSourceId(src.id)}
            className="px-3 py-1.5 rounded-md text-xs font-medium transition-all"
            style={
              selectedSourceId === src.id
                ? { background: "var(--color-accent-muted)", color: "var(--color-accent)" }
                : { color: "var(--color-text-tertiary)", background: "transparent" }
            }
          >
            {src.name}
          </button>
        ))}
      </div>
    </div>
  );
}
