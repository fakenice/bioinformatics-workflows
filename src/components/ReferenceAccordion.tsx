import { ChevronDown, ChevronUp, ExternalLink, BookOpen } from "lucide-react";
import { useState } from "react";
import type { Reference } from "../types/pipeline";
import { useT } from "../i18n";

export default function ReferenceAccordion({ references }: { references: Reference[] }) {
  const [open, setOpen] = useState(false);
  const t = useT();

  const typeLabels: Record<string, string> = {
    official: t("references.types.official"),
    community: t("references.types.community"),
    paper: t("references.types.paper"),
  };

  const countLabel = t("references.count").replace("{count}", String(references.length));

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)" }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm transition-colors"
        style={{ color: "var(--color-text-secondary)" }}
      >
        <span className="flex items-center gap-2">
          <BookOpen className="w-4 h-4" />
          {countLabel}
        </span>
        {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {open && (
        <div className="px-4 pb-3 space-y-1" style={{ borderTop: "1px solid var(--color-border)" }}>
          {references.map((ref, i) => (
            <a
              key={i}
              href={ref.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start gap-2.5 px-2 py-2 rounded-lg transition-colors group"
              style={{ color: "var(--color-text-secondary)" }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = "var(--color-surface-alt)";
                (e.currentTarget as HTMLElement).style.color = "var(--color-accent)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = "transparent";
                (e.currentTarget as HTMLElement).style.color = "var(--color-text-secondary)";
              }}
            >
              <span
                className="text-xs px-1.5 py-0.5 rounded shrink-0 mt-0.5"
                style={{ background: "var(--color-accent-muted)", color: "var(--color-accent)" }}
              >
                {typeLabels[ref.type] || ref.type}
              </span>
              <span className="text-sm flex-1">{ref.title}</span>
              <ExternalLink className="w-3 h-3 shrink-0 mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity" />
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
