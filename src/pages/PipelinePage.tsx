import { useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, GitCompare } from "lucide-react";
import { useStore } from "../store/useStore";
import FlowCanvas from "../components/FlowCanvas";
import DetailPanel from "../components/DetailPanel";
import SourceSwitcher from "../components/SourceSwitcher";
import ReferenceAccordion from "../components/ReferenceAccordion";

export default function PipelinePage() {
  const { id } = useParams<{ id: string }>();
  const { selectPipeline, selectedPipeline, selectedSourceId } = useStore();

  useEffect(() => {
    if (id) selectPipeline(id);
  }, [id, selectPipeline]);

  if (!selectedPipeline) {
    return (
      <div
        className="flex items-center justify-center h-64"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        <div className="text-center">
          <div
            className="w-8 h-8 mx-auto mb-3 rounded-full border-2 animate-spin"
            style={{
              borderColor: "var(--color-accent)",
              borderTopColor: "transparent",
            }}
          />
          <p className="text-sm">加载分析流程...</p>
        </div>
      </div>
    );
  }

  const source =
    selectedPipeline.sources.find((s) => s.id === selectedSourceId) ||
    selectedPipeline.sources[0];

  return (
    <div className="min-h-screen" style={{ background: "var(--color-page)" }}>
      {/* 顶部导航 */}
      <header
        className="sticky top-0 z-20 px-5 py-3 flex items-center justify-between"
        style={{
          background: "oklch(1 0 0 / 0.85)",
          backdropFilter: "blur(16px) saturate(1.5)",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        <div className="flex items-center gap-3 min-w-0">
          <Link
            to="/"
            className="p-2 -ml-2 rounded-lg hover:bg-surface-alt transition-colors"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="min-w-0">
            <h1 className="text-lg font-bold truncate" style={{ color: "var(--color-text-primary)" }}>
              {selectedPipeline.nameZH}
            </h1>
            <p className="text-xs truncate" style={{ color: "var(--color-text-tertiary)" }}>
              {selectedPipeline.name}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <SourceSwitcher />
          <Link
            to={`/compare/${selectedPipeline.id}`}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
            style={{
              background: "var(--color-surface)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text-secondary)",
            }}
            onMouseEnter={(e) => {
              const el = e.currentTarget as HTMLElement;
              el.style.borderColor = "var(--color-accent)";
              el.style.color = "var(--color-accent)";
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget as HTMLElement;
              el.style.borderColor = "var(--color-border)";
              el.style.color = "var(--color-text-secondary)";
            }}
          >
            <GitCompare className="w-3.5 h-3.5" />
            对比模式
          </Link>
        </div>
      </header>

      {/* 主体 */}
      <main className="px-5 py-4">
        <div style={{ height: "calc(100vh - 152px)" }}>
          <FlowCanvas steps={source.steps} />
        </div>
        <DetailPanel />
        <div className="mt-4">
          <ReferenceAccordion references={source.references} />
        </div>
      </main>
    </div>
  );
}
