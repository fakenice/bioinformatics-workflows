import { useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Check, Minus } from "lucide-react";
import { useStore } from "../store/useStore";
import { useT, useLanguage } from "../i18n";
import FlowCanvas from "../components/FlowCanvas";

const COLORS = ["var(--color-node-dna)", "var(--color-node-rna)"];

export default function ComparePage() {
  const { id } = useParams<{ id: string }>();
  const { selectPipeline, selectedPipeline } = useStore();
  const t = useT();
  const { lang } = useLanguage();

  useEffect(() => {
    if (id) selectPipeline(id);
  }, [id, selectPipeline]);

  if (!selectedPipeline || selectedPipeline.sources.length < 2) {
    return (
      <div
        className="flex flex-col items-center justify-center min-h-[60vh]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        <p className="text-lg">{t("compare.singleSourceNotice")}</p>
        <Link
          to={`/pipeline/${id}`}
          className="text-sm mt-2 underline"
          style={{ color: "var(--color-accent)" }}
        >
          {t("compare.backToPipeline")}
        </Link>
      </div>
    );
  }

  const sources = selectedPipeline.sources.slice(0, 2);
  const leftSource = sources[0];
  const rightSource = sources[1];
  const maxLen = Math.max(leftSource.steps.length, rightSource.steps.length);

  const pipelineName = lang === "en" ? selectedPipeline.name : selectedPipeline.nameZH;

  return (
    <div className="min-h-screen px-5 py-4" style={{ background: "var(--color-page)" }}>
      <header
        className="sticky top-0 z-20 mb-4 px-1 py-3 flex items-center gap-3"
        style={{
          background: "oklch(1 0 0 / 0.85)",
          backdropFilter: "blur(16px) saturate(1.5)",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        <Link
          to={`/pipeline/${selectedPipeline.id}`}
          className="p-2 -ml-2 rounded-lg transition-colors"
          style={{ color: "var(--color-text-tertiary)" }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.background = "var(--color-surface-alt)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.background = "transparent";
          }}
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <h1 className="text-lg font-bold" style={{ color: "var(--color-text-primary)" }}>
          {pipelineName}
        </h1>
        <span
          className="text-xs px-2 py-0.5 rounded-full font-medium"
          style={{ background: "var(--color-accent-muted)", color: "var(--color-accent)" }}
        >
          {t("compare.title")}
        </span>
      </header>

      <div className="grid grid-cols-2 gap-4">
        {sources.map((source, si) => (
          <div key={source.id}>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2.5 h-2.5 rounded-full" style={{ background: COLORS[si] }} />
              <h2 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
                {lang === "en" ? (source.nameEn || source.name) : source.name}
              </h2>
            </div>

            <div
              className="rounded-xl overflow-hidden mb-4"
              style={{ height: 380, border: "1px solid var(--color-border)" }}
            >
              <FlowCanvas steps={source.steps} />
            </div>

            <div className="space-y-1.5">
              {Array.from({ length: maxLen }).map((_, i) => {
                const step = source.steps[i];
                return (
                  <div
                    key={i}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs"
                    style={{
                      background: step
                        ? `color-mix(in oklch, ${COLORS[si]} 6%, transparent)`
                        : "var(--color-surface-alt)",
                      border: step
                        ? `1px solid color-mix(in oklch, ${COLORS[si]} 15%, transparent)`
                        : "1px solid var(--color-border)",
                      color: step ? "var(--color-text-primary)" : "var(--color-text-tertiary)",
                    }}
                  >
                    {step ? (
                      <Check className="w-3 h-3 shrink-0" style={{ color: COLORS[si] }} />
                    ) : (
                      <Minus className="w-3 h-3 shrink-0" style={{ color: "var(--color-text-tertiary)" }} />
                    )}
                    <span className={step ? "" : "italic"}>
                      {step
                        ? lang === "en"
                          ? step.nameEn || step.name
                          : step.name
                        : t("compare.noCorrespondingStep")}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
