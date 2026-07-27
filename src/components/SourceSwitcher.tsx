import { useStore } from "../store/useStore";

export default function SourceSwitcher() {
  const { selectedPipeline, selectedSourceId, setSelectedSourceId } = useStore();

  if (!selectedPipeline || selectedPipeline.sources.length <= 1) return null;

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-slate-500">参考来源:</span>
      <div className="flex rounded-lg bg-slate-800 p-0.5 gap-0.5">
        {selectedPipeline.sources.map((src) => (
          <button
            key={src.id}
            onClick={() => setSelectedSourceId(src.id)}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              selectedSourceId === src.id
                ? "bg-emerald-500/20 text-emerald-400"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {src.name}
          </button>
        ))}
      </div>
    </div>
  );
}
