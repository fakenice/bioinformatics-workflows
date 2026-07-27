import { useNavigate } from "react-router-dom";
import type { PipelineDefinition } from "../types/pipeline";
import { Dna, Microscope, Layers, Bug } from "lucide-react";
import { categoryLabels } from "../data/pipelines";

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  dna: Dna,
  microscope: Microscope,
  layers: Layers,
  bacteria: Bug,
};

export default function PipelineCard({ pipeline }: { pipeline: PipelineDefinition }) {
  const navigate = useNavigate();
  const Icon = iconMap[pipeline.icon] || Dna;

  return (
    <button
      onClick={() => navigate(`/pipeline/${pipeline.id}`)}
      className="group w-full text-left p-5 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-emerald-500/30 hover:bg-slate-800 transition-all duration-200"
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 group-hover:bg-emerald-500/20 transition-colors">
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white group-hover:text-emerald-400 transition-colors">
            {pipeline.nameZH}
          </h3>
          <p className="text-sm text-slate-400 mt-1 line-clamp-2">{pipeline.overview}</p>
          <div className="flex gap-1.5 mt-3 flex-wrap">
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-700 text-slate-300">
              {categoryLabels[pipeline.category] || pipeline.category}
            </span>
            {pipeline.tags.slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="text-xs px-2 py-0.5 rounded-full bg-slate-700/50 text-slate-400"
              >
                {tag}
              </span>
            ))}
            {pipeline.tags.length > 2 && (
              <span className="text-xs px-2 py-0.5 text-slate-500">+{pipeline.tags.length - 2}</span>
            )}
          </div>
        </div>
        <div className="text-slate-500 group-hover:text-emerald-400 transition-colors self-center">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </button>
  );
}
