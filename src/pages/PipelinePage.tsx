import { useEffect, useState, useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, GitCompare, Code } from "lucide-react";
import { useStore } from "../store/useStore";
import { useT } from "../i18n";
import PipelineMarkdown from "../components/PipelineMarkdown";
import SourceSwitcher from "../components/SourceSwitcher";
import ReferenceAccordion from "../components/ReferenceAccordion";
import ExportModal from "../components/ExportModal";
import { generateNextflowScript } from "../utils/scriptExporter";

export default function PipelinePage() {
  const { id } = useParams<{ id: string }>();
  const { selectPipeline, selectedPipeline, selectedSourceId } = useStore();
  const [exportOpen, setExportOpen] = useState(false);
  const t = useT();

  const exportScript = useMemo(() => {
    if (!selectedPipeline) return "";
    return generateNextflowScript(selectedPipeline, selectedSourceId);
  }, [selectedPipeline, selectedSourceId]);

  const exportFileName = useMemo(() => {
    if (!selectedPipeline) return "pipeline.nf";
    return `${selectedPipeline.id}.nf`;
  }, [selectedPipeline]);

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
          <p className="text-sm">{t("pipeline.loading")}</p>
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
          background: "oklch(0.993 0.002 140 / 0.88)",
          backdropFilter: "blur(24px) saturate(1.5)",
          boxShadow: "var(--shadow-sm)",
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
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold truncate" style={{ color: "var(--color-text-primary)" }}>
                {selectedPipeline.nameZH}
              </h1>
              {selectedPipeline.version && (
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    padding: "1px 7px",
                    borderRadius: 999,
                    fontSize: 11,
                    fontWeight: 600,
                    background: "var(--color-accent-muted)",
                    color: "var(--color-accent)",
                    lineHeight: "18px",
                    flexShrink: 0,
                  }}
                >
                  v{selectedPipeline.version}
                </span>
              )}
            </div>
            <p className="text-xs truncate" style={{ color: "var(--color-text-tertiary)" }}>
              {selectedPipeline.name}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <SourceSwitcher />
          <button
            onClick={() => setExportOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
            style={{
              background: "var(--color-surface)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text-secondary)",
              cursor: "pointer",
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
            <Code className="w-3.5 h-3.5" />
            {t("pipeline.export")}
          </button>
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
            {t("pipeline.compareMode")}
          </Link>
        </div>
      </header>

      {/* 主体 */}
      <main className="px-5 py-6">
        <PipelineMarkdown pipeline={selectedPipeline} sourceId={selectedSourceId} />
        <div className="mt-4">
          <ReferenceAccordion references={source.references} />
        </div>
      </main>

      <ExportModal
        open={exportOpen}
        onClose={() => setExportOpen(false)}
        script={exportScript}
        fileName={exportFileName}
      />
    </div>
  );
}
