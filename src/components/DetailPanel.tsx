import { X, Box } from "lucide-react";
import { useStore } from "../store/useStore";
import ReactMarkdown from "react-markdown";

export default function DetailPanel() {
  const { selectedStep, setSelectedStep } = useStore();

  if (!selectedStep) return null;

  return (
    <div className="fixed right-0 top-16 bottom-0 w-96 bg-slate-900 border-l border-slate-800 shadow-2xl z-40 overflow-y-auto animate-in slide-in-from-right">
      <div className="sticky top-0 bg-slate-900/95 backdrop-blur-sm border-b border-slate-800 p-4 flex items-center justify-between">
        <h2 className="font-semibold text-white text-sm">{selectedStep.name}</h2>
        <button
          onClick={() => setSelectedStep(null)}
          className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="p-4 space-y-5">
        <div>
          <p className="text-sm text-slate-300 leading-relaxed">{selectedStep.description}</p>
        </div>

        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
            推荐工具
          </h3>
          <div className="space-y-3">
            {selectedStep.tools.map((tool) => (
              <div
                key={tool.name}
                className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/50"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-sm text-emerald-400">{tool.name}</span>
                  <span className="text-xs text-slate-500">{tool.version}</span>
                </div>
                {tool.params && (
                  <div className="mt-2 p-2 rounded bg-slate-950/50 border border-slate-800">
                    <code className="text-xs text-slate-300 break-all">{tool.params}</code>
                  </div>
                )}
                {tool.docker && (
                  <div className="flex items-center gap-1.5 mt-2">
                    <Box className="w-3 h-3 text-slate-500" />
                    <code className="text-xs text-slate-500">{tool.docker}</code>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {selectedStep.notes && (
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              注意事项
            </h3>
            <div className="text-sm text-slate-300 prose prose-invert prose-sm max-w-none">
              <ReactMarkdown>{selectedStep.notes}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
