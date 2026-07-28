import { useNavigate } from "react-router-dom";
import type { PipelineDefinition } from "../types/pipeline";
import { Dna, Microscope, Layers, Bug, ArrowRight } from "lucide-react";
import { useLanguage, useT } from "../i18n";

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  dna: Dna,
  microscope: Microscope,
  layers: Layers,
  bacteria: Bug,
};

export default function PipelineCard({
  pipeline,
  accent,
}: {
  pipeline: PipelineDefinition;
  accent: string;
}) {
  const navigate = useNavigate();
  const { lang } = useLanguage();
  const t = useT();
  const Icon = iconMap[pipeline.icon] || Dna;
  const nameText = lang === "en" ? pipeline.name : pipeline.nameZH;
  const overviewText = lang === "en" ? (pipeline.overviewEn || pipeline.overview) : pipeline.overview;
  return (
    <button
      onClick={() => navigate(`/pipeline/${pipeline.id}`)}
      className="group w-full text-left p-5 rounded-2xl card-hover"
      style={{
        background: "var(--color-surface)",
        boxShadow: "var(--shadow-sm)",
        border: "1px solid transparent",
      }}
      onMouseEnter={(e) => {
        const el = e.currentTarget as HTMLElement;
        el.style.boxShadow = `var(--shadow-md), 0 0 0 1px ${accent}`;
      }}
      onMouseLeave={(e) => {
        const el = e.currentTarget as HTMLElement;
        el.style.boxShadow = "var(--shadow-sm)";
      }}
    >
      <div className="flex items-start gap-3.5">
        <div
          className="p-2.5 rounded-xl shrink-0"
          style={{
            background: `color-mix(in oklch, ${accent} 12%, transparent)`,
            color: accent,
          }}
        >
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h3
            className="font-semibold text-[15px] leading-snug"
            style={{ color: "var(--color-text-primary)" }}
          >
            {nameText}
          </h3>
          <p
            className="text-[13px] mt-1.5 line-clamp-2 leading-relaxed"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {overviewText}
          </p>
          <div className="flex gap-1.5 mt-3.5 flex-wrap items-center">
            <span
              className="text-[11px] px-2 py-0.5 rounded-md font-medium"
              style={{
                background: `color-mix(in oklch, ${accent} 14%, transparent)`,
                color: accent,
              }}
            >
              {t(`categories.${pipeline.category}`)}
            </span>
            {pipeline.tags.slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="text-[11px] px-2 py-0.5 rounded-md"
                style={{
                  background: "var(--color-surface-alt)",
                  color: "var(--color-text-tertiary)",
                }}
              >
                {tag}
              </span>
            ))}
            {pipeline.tags.length > 2 && (
              <span className="text-[11px]" style={{ color: "var(--color-text-tertiary)" }}>
                +{pipeline.tags.length - 2}
              </span>
            )}
          </div>
        </div>
        <div
          className="self-center shrink-0 opacity-0 group-hover:opacity-100 transition-all duration-200 -translate-x-1 group-hover:translate-x-0"
          style={{ color: accent }}
        >
          <ArrowRight className="w-4 h-4" />
        </div>
      </div>
    </button>
  );
}
