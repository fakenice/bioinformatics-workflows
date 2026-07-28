import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Search, X, Dna, BookOpen } from "lucide-react";
import { useT } from "../i18n";
import { searchAll, type SearchResult } from "../utils/searchEngine";

interface SearchOverlayProps {
  open: boolean;
  onClose: () => void;
}

export default function SearchOverlay({ open, onClose }: SearchOverlayProps) {
  const t = useT();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Focus input on open
  useEffect(() => {
    if (open) {
      setQuery("");
      setResults([]);
      // Small delay to let the DOM render
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  // Debounced search
  const doSearch = useCallback((q: string) => {
    if (q.trim().length < 2) {
      setResults([]);
      return;
    }
    const hits = searchAll(q);
    setResults(hits);
  }, []);

  const handleInput = (value: string) => {
    setQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(value), 200);
  };

  const handleSelect = (result: SearchResult) => {
    navigate(result.route);
    onClose();
  };

  if (!open) return null;

  const pipeResults = results.filter((r) => r.type === "pipeline");
  const docResults = results.filter((r) => r.type === "doc");

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        paddingTop: "12vh",
        background: "rgba(20, 24, 22, 0.55)",
        backdropFilter: "blur(12px)",
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(640px, 92vw)",
          background: "var(--color-surface)",
          borderRadius: 16,
          boxShadow: "0 20px 60px rgba(0,0,0,0.25)",
          border: "1px solid var(--color-border)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          maxHeight: "min(560px, 65vh)",
        }}
      >
        {/* Input row */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "14px 16px",
            borderBottom: results.length > 0 ? "1px solid var(--color-border)" : "none",
          }}
        >
          <Search size={18} style={{ color: "var(--color-text-tertiary)", flexShrink: 0 }} />
          <input
            ref={inputRef}
            type="text"
            placeholder={t("search.placeholder")}
            value={query}
            onChange={(e) => handleInput(e.target.value)}
            style={{
              flex: 1,
              border: "none",
              outline: "none",
              background: "transparent",
              fontSize: 15,
              color: "var(--color-text-primary)",
              fontFamily: "inherit",
            }}
          />
          <button
            onClick={onClose}
            aria-label="关闭"
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: 28,
              height: 28,
              borderRadius: 6,
              border: "none",
              background: "var(--color-surface-alt)",
              color: "var(--color-text-tertiary)",
              cursor: "pointer",
              flexShrink: 0,
            }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Results */}
        {results.length > 0 && (
          <div style={{ overflow: "auto", flex: 1, padding: "8px 0" }}>
            {/* Pipelines section */}
            {pipeResults.length > 0 && (
              <div>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    padding: "6px 16px",
                    fontSize: 12,
                    fontWeight: 600,
                    color: "var(--color-text-tertiary)",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                  }}
                >
                  <Dna size={12} />
                  {t("search.pipelines")}
                </div>
                {pipeResults.map((r, i) => (
                  <button
                    key={`pipe-${i}`}
                    onClick={() => handleSelect(r)}
                    style={{
                      display: "block",
                      width: "100%",
                      textAlign: "left",
                      padding: "10px 16px",
                      border: "none",
                      background: "transparent",
                      cursor: "pointer",
                      fontFamily: "inherit",
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.background =
                        "var(--color-surface-alt)";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.background = "transparent";
                    }}
                  >
                    <div
                      style={{
                        fontSize: 14,
                        fontWeight: 600,
                        color: "var(--color-text-primary)",
                        marginBottom: 2,
                      }}
                    >
                      {highlightMatch(r.title, query)}
                    </div>
                    <div
                      style={{
                        fontSize: 12,
                        color: "var(--color-text-tertiary)",
                      }}
                    >
                      {r.subtitle}
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Docs section */}
            {docResults.length > 0 && (
              <div>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    padding: pipeResults.length > 0 ? "14px 16px 6px" : "6px 16px",
                    fontSize: 12,
                    fontWeight: 600,
                    color: "var(--color-text-tertiary)",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    borderTop:
                      pipeResults.length > 0 ? "1px solid var(--color-border)" : "none",
                  }}
                >
                  <BookOpen size={12} />
                  {t("search.docs")}
                </div>
                {docResults.map((r, i) => (
                  <button
                    key={`doc-${i}`}
                    onClick={() => handleSelect(r)}
                    style={{
                      display: "block",
                      width: "100%",
                      textAlign: "left",
                      padding: "10px 16px",
                      border: "none",
                      background: "transparent",
                      cursor: "pointer",
                      fontFamily: "inherit",
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.background =
                        "var(--color-surface-alt)";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.background = "transparent";
                    }}
                  >
                    <div
                      style={{
                        fontSize: 14,
                        fontWeight: 600,
                        color: "var(--color-text-primary)",
                        marginBottom: 2,
                      }}
                    >
                      {highlightMatch(r.title, query)}
                    </div>
                    {r.subtitle && (
                      <div
                        style={{
                          fontSize: 12,
                          color: "var(--color-text-tertiary)",
                          marginBottom: 4,
                        }}
                      >
                        {r.subtitle}
                      </div>
                    )}
                    <div
                      style={{
                        fontSize: 12,
                        color: "var(--color-text-secondary)",
                        lineHeight: 1.5,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                      }}
                    >
                      {highlightMatch(r.match.slice(0, 150), query)}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Empty state */}
        {query.trim().length >= 2 && results.length === 0 && (
          <div
            style={{
              padding: "32px 16px",
              textAlign: "center",
              fontSize: 14,
              color: "var(--color-text-tertiary)",
            }}
          >
            {t("search.noResults")}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Highlight matching substrings in text, using accent color.
 */
function highlightMatch(text: string, query: string): React.ReactNode {
  if (!query || query.length < 2) return text;

  try {
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`(${escaped})`, "gi");
    const parts = text.split(regex);

    return parts.map((part, i) =>
      regex.test(part) ? (
        <mark
          key={i}
          style={{
            background: "var(--color-accent-muted)",
            color: "var(--color-accent)",
            borderRadius: 2,
            padding: "1px 2px",
            fontWeight: 600,
          }}
        >
          {part}
        </mark>
      ) : (
        part
      )
    );
  } catch {
    return text;
  }
}
