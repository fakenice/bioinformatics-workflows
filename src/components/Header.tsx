import { useState } from "react";
import { Search, Dna } from "lucide-react";
import { Link } from "react-router-dom";
import { useStore } from "../store/useStore";

export default function Header() {
  const { searchQuery, setSearchQuery } = useStore();
  const [focused, setFocused] = useState(false);

  return (
    <header
      className="sticky top-0 z-50 border-b"
      style={{
        background: "oklch(1 0 0 / 0.85)",
        backdropFilter: "blur(16px) saturate(1.5)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-4">
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <Dna className="w-6 h-6" style={{ color: "var(--color-accent)" }} />
          <span
            className="font-bold text-base tracking-tight"
            style={{ color: "var(--color-text-primary)" }}
          >
            FlowSeq
          </span>
        </Link>

        <div
          className="flex-1 max-w-xl mx-auto flex items-center gap-2 px-3.5 py-2 rounded-lg transition-all"
          style={{
            background: focused ? "var(--color-surface)" : "var(--color-surface-alt)",
            border: focused
              ? "2px solid var(--color-accent)"
              : "1px solid var(--color-border)",
          }}
        >
          <Search className="w-4 h-4 shrink-0" style={{ color: "var(--color-text-tertiary)" }} />
          <input
            type="text"
            placeholder="搜索分析类型、工具名称.."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            className="bg-transparent border-none outline-none text-sm w-full"
            style={{ color: "var(--color-text-primary)" }}
          />
        </div>

        <a
          href="https://github.com/fakenice/flowseq"
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 transition-colors"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
          </svg>
        </a>
      </div>
    </header>
  );
}
