import { useState, useEffect } from "react";
import { Search, Dna, BookOpen, Settings } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { useStore } from "../store/useStore";
import { useLanguage, useT } from "../i18n";
import SearchOverlay from "./SearchOverlay";

export default function Header() {
  const { searchQuery, setSearchQuery, searchOverlayOpen, setSearchOverlayOpen } =
    useStore();
  const [focused, setFocused] = useState(false);
  const location = useLocation();
  const { lang, setLang } = useLanguage();
  const t = useT();

  const toggleLang = () => {
    setLang(lang === "zh" ? "en" : "zh");
  };

  // Ctrl+K / Cmd+K shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setSearchOverlayOpen(true);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [setSearchOverlayOpen]);

  return (
    <>
      <header
        className="sticky top-0 z-50 glass-panel"
        style={{ boxShadow: "var(--shadow-sm)" }}
      >
        <div className="max-w-5xl mx-auto px-5 h-13 flex items-center gap-5">
          <Link to="/" className="flex items-center gap-2.5 shrink-0 group">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
              style={{ background: "var(--color-accent-muted)" }}
            >
              <Dna className="w-4 h-4" style={{ color: "var(--color-accent)" }} />
            </div>
            <span
              className="font-semibold text-[15px] tracking-tight"
              style={{ color: "var(--color-text-primary)" }}
            >
              FlowSeq
            </span>
          </Link>

          <div
            className="flex-1 max-w-lg flex items-center gap-2.5 px-3.5 py-2 rounded-full transition-all duration-200 cursor-pointer"
            onClick={() => setSearchOverlayOpen(true)}
            style={{
              background: focused ? "var(--color-surface)" : "var(--color-surface-alt)",
              boxShadow: focused
                ? "0 0 0 2px var(--color-accent-muted), var(--shadow-sm)"
                : "none",
            }}
          >
            <Search
              className="w-3.5 h-3.5 shrink-0"
              style={{ color: "var(--color-text-tertiary)" }}
            />
            <input
              type="text"
              placeholder={t("header.searchPlaceholder")}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              readOnly
              className="bg-transparent border-none outline-none text-sm w-full placeholder:text-text-tertiary cursor-pointer"
              style={{ color: "var(--color-text-primary)" }}
            />
          </div>

          <Link
            to="/docs"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 5,
              padding: "6px 12px",
              borderRadius: 8,
              fontSize: 13,
              fontWeight: 500,
              textDecoration: "none",
              color: location.pathname.startsWith("/docs")
                ? "var(--color-accent)"
                : "var(--color-text-secondary)",
              background: location.pathname.startsWith("/docs")
                ? "var(--color-accent-muted)"
                : "transparent",
              transition: "background 0.15s",
              whiteSpace: "nowrap",
            }}
          >
            <BookOpen size={14} />
            {t("header.docs")}
          </Link>

          <Link
            to="/manager"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 5,
              padding: "6px 12px",
              borderRadius: 8,
              fontSize: 13,
              fontWeight: 500,
              textDecoration: "none",
              color: location.pathname.startsWith("/manager")
                ? "var(--color-accent)"
                : "var(--color-text-secondary)",
              background: location.pathname.startsWith("/manager")
                ? "var(--color-accent-muted)"
                : "transparent",
              transition: "background 0.15s",
              whiteSpace: "nowrap",
            }}
          >
            <Settings size={14} />
            {t("header.manage")}
          </Link>

          <button
            onClick={toggleLang}
            className="shrink-0 px-2 py-1 rounded-md text-xs font-semibold transition-colors hover:bg-surface-alt"
            style={{
              color: "var(--color-text-secondary)",
              background: "var(--color-surface-alt)",
              border: "1px solid var(--color-border)",
              cursor: "pointer",
              fontFamily: "inherit",
            }}
            aria-label="Switch language"
          >
            {lang === "zh" ? "EN" : "中"}
          </button>

          <a
            href="https://github.com/fakenice/bioinformatics-workflows"
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 p-1.5 rounded-lg transition-colors hover:bg-surface-alt"
            style={{ color: "var(--color-text-tertiary)" }}
            aria-label="GitHub"
          >
            <svg className="w-4.5 h-4.5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
          </a>
        </div>
      </header>

      <SearchOverlay
        open={searchOverlayOpen}
        onClose={() => setSearchOverlayOpen(false)}
      />
    </>
  );
}
