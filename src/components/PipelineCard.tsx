import { useNavigate } from "react-router-dom";
import type { PipelineDefinition } from "../types/pipeline";
import { Dna, Microscope, Layers, Bug, ArrowRight } from "lucide-react";
import { categoryLabels } from "../data/pipelines";

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
  const Icon = iconMap[pipeline.icon] || Dna;

  return (
    <button
      onClick={() => navigate(`/pipeline/${pipeline.id}`)}
      className="group w-full text-left p-4 rounded-xl transition-all duration-200"
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLElement).style.borderColor = accent;
        (e.currentTarget as HTMLElement).style.boxShadow =
          `0 2px 12px oklch(0 0 0 / 0.06), 0 0 0 1px ${accent}`;
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLElement).style.borderColor = "var(--color-border)";
        (e.currentTarget as HTMLElement).style.boxShadow = "none";
      }}
    >
      <div className="flex items-start gap-3">
        <div
          className="p-2 rounded-lg shrink-0 transition-colors"
          style={{
            background: `color-mix(in oklch, ${accent} 10%, transparent)`,
            color: accent,
          }}
        >
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h3
            className="font-semibold text-sm transition-colors"
            style={{ color: "var(--color-text-primary)" }}
          >
            {pipeline.nameZH}
          </h3>
          <p
            className="text-xs mt-1 line-clamp-2"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {pipeline.overview}
          </p>
          <div className="flex gap-1.5 mt-3 flex-wrap">
            <span
              className="text-xs px-2 py-0.5 rounded-full"
              style={{
                background: `color-mix(in oklch, ${accent} 10%, transparent)`,
                color: accent,
              }}
            >
              {categoryLabels[pipeline.category] || pipeline.category}
            </span>
            {pipeline.tags.slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="text-xs px-2 py-0.5 rounded-full"
                style={{
                  background: "var(--color-surface-alt)",
                  color: "var(--color-text-tertiary)",
                }}
              >
                {tag}
              </span>
            ))}
            {pipeline.tags.length > 2 && (
              <span className="text-xs px-2 py-0.5" style={{ color: "var(--color-text-tertiary)" }}>
                +{pipeline.tags.length - 2}
              </span>
            )}
          </div>
        </div>
        <div
          className="self-center shrink-0 opacity-0 group-hover:opacity-100 transition-all -translate-x-1 group-hover:translate-x-0"
          style={{ color: "var(--color-accent)" }}
        >
          <ArrowRight className="w-4 h-4" />
        </div>
      </div>
    </button>
  );
}
