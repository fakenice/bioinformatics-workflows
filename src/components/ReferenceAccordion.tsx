import { ChevronDown, ChevronUp, ExternalLink, BookOpen } from "lucide-react";
import { useState } from "react";
import type { Reference } from "../types/pipeline";

const typeLabels: Record<string, string> = {
  official: "官方文档",
  community: "社区资源",
  paper: "学术论文",
};

export default function ReferenceAccordion({ references }: { references: Reference[] }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-6 border-t border-slate-800 pt-4">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between text-sm text-slate-400 hover:text-white transition-colors"
      >
        <span className="flex items-center gap-2">
          <BookOpen className="w-4 h-4" />
          参考文献 ({references.length})
        </span>
        {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {open && (
        <div className="mt-3 space-y-2">
          {references.map((ref, i) => (
            <a
              key={i}
              href={ref.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start gap-2 p-2 rounded-lg hover:bg-slate-800 transition-colors group"
            >
              <span className="text-xs px-1.5 py-0.5 rounded bg-slate-800 text-slate-500 shrink-0 mt-0.5">
                {typeLabels[ref.type] || ref.type}
              </span>
              <span className="text-sm text-slate-300 group-hover:text-emerald-400 transition-colors flex-1">
                {ref.title}
              </span>
              <ExternalLink className="w-3 h-3 text-slate-600 group-hover:text-slate-400 shrink-0 mt-0.5" />
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
