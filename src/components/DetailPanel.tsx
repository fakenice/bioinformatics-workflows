import { X, Box, Copy, Check } from "lucide-react";
import { useStore } from "../store/useStore";
import type { ToolInfo } from "../types/pipeline";
import ReactMarkdown from "react-markdown";
import { useState } from "react";

export default function DetailPanel() {
  const { selectedStep, setSelectedStep } = useStore();
  const [copied, setCopied] = useState<string | null>(null);

  if (!selectedStep) return null;

  const handleCopy = async (text: string, id: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 1500);
  };

  return (
    <>
      <div
        className="fixed inset-0 z-30"
        style={{ background: "oklch(0 0 0 / 0.15)" }}
        onClick={() => setSelectedStep(null)}
      />

      <div
        className="fixed right-0 top-0 bottom-0 z-40 w-[400px] flex flex-col shadow-2xl"
        style={{
          background: "var(--color-surface)",
          borderLeft: "1px solid var(--color-border)",
          animation: "slideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
        }}
      >
        <div
          className="flex items-center justify-between px-5 py-4 shrink-0"
          style={{ borderBottom: "1px solid var(--color-border)" }}
        >
          <div className="min-w-0">
            <div
              className="text-xs font-semibold uppercase tracking-wider"
              style={{ color: "var(--color-accent)" }}
            >
              Step Details
            </div>
            <h2
              className="text-base font-semibold mt-0.5 truncate"
              style={{ color: "var(--color-text-primary)" }}
            >
              {selectedStep.name}
            </h2>
          </div>
          <button
            onClick={() => setSelectedStep(null)}
            className="p-1.5 rounded-lg hover:bg-surface-alt transition-colors shrink-0"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-6">
          {selectedStep.description && (
            <p
              className="text-sm leading-relaxed"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {selectedStep.description}
            </p>
          )}

          {selectedStep.tools.length > 0 && (
            <div>
              <h3
                className="text-xs font-semibold uppercase tracking-wider mb-3"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                推荐工具
              </h3>
              <div className="space-y-3">
                {selectedStep.tools.map((tool: ToolInfo) => (
                  <div
                    key={tool.name}
                    className="p-3.5 rounded-lg"
                    style={{
                      background: "var(--color-surface-alt)",
                      border: "1px solid var(--color-border)",
                    }}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span
                        className="font-mono text-sm font-semibold"
                        style={{ color: "var(--color-accent)" }}
                      >
                        {tool.name}
                      </span>
                      {tool.version && (
                        <span
                          className="text-xs font-mono px-1.5 py-0.5 rounded"
                          style={{
                            background: "var(--color-accent-muted)",
                            color: "var(--color-accent)",
                          }}
                        >
                          {tool.version}
                        </span>
                      )}
                    </div>

                    {tool.params && (
                      <div className="relative group">
                        <div
                          className="p-2.5 rounded text-xs font-mono leading-relaxed overflow-x-auto"
                          style={{
                            background: "oklch(0.98 0.002 140)",
                            border: "1px solid var(--color-border)",
                            color: "var(--color-text-secondary)",
                          }}
                        >
                          <code>{tool.params}</code>
                        </div>
                        <button
                          onClick={() => handleCopy(tool.params!, tool.name)}
                          className="absolute top-1.5 right-1.5 p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                          style={{
                            background: "var(--color-surface)",
                            color: "var(--color-text-tertiary)",
                          }}
                        >
                          {copied === tool.name ? (
                            <Check className="w-3 h-3" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </button>
                      </div>
                    )}

                    {tool.docker && (
                      <div className="flex items-center gap-1.5 mt-2">
                        <Box
                          className="w-3 h-3"
                          style={{ color: "var(--color-text-tertiary)" }}
                        />
                        <code
                          className="text-xs"
                          style={{ color: "var(--color-text-tertiary)" }}
                        >
                          {tool.docker}
                        </code>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedStep.notes && (
            <div>
              <h3
                className="text-xs font-semibold uppercase tracking-wider mb-2"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                注意事项
              </h3>
              <div
                className="text-sm leading-relaxed prose prose-sm max-w-none"
                style={{ color: "var(--color-text-secondary)" }}
              >
                <ReactMarkdown>{selectedStep.notes}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </>
  );
}
