import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { BookOpen, ChevronRight, FileText } from "lucide-react";
import { useT } from "../i18n";

interface DocEntry {
  slug: string;
  title: string;
  source: string;
}

const DOC_ENTRIES: DocEntry[] = [
  { slug: "skill", title: "Bioinformatics Workflows — Skill 概述", source: "skill" },
  { slug: "study_designs", title: "研究设计标准流程", source: "ref" },
  { slug: "patterns", title: "代码模式 (Nextflow/Snakemake/WDL)", source: "ref" },
  { slug: "sharp_edges", title: "常见陷阱 (Sharp Edges)", source: "ref" },
  { slug: "validations", title: "代码审查规则", source: "ref" },
];

const SKILL_MD_MODULES = import.meta.glob("../../SKILL.md", { query: "?raw", import: "default", eager: true });
const REF_MD_MODULES = import.meta.glob("../../references/*.md", { query: "?raw", import: "default", eager: true });

function getSkillMd(): string {
  const key = Object.keys(SKILL_MD_MODULES)[0];
  return (SKILL_MD_MODULES[key] as string) || "";
}

function getRefMd(filename: string): string {
  const key = Object.keys(REF_MD_MODULES).find((k) => k.includes(filename));
  if (!key) return "";
  return (REF_MD_MODULES[key] as string) || "";
}

export default function DocsPage() {
  const { slug } = useParams<{ slug?: string }>();
  const navigate = useNavigate();
  const [activeSlug, setActiveSlug] = useState<string>(slug || "skill");
  const t = useT();

  useEffect(() => {
    if (slug) setActiveSlug(slug);
  }, [slug]);

  const currentDoc = DOC_ENTRIES.find((d) => d.slug === activeSlug) || DOC_ENTRIES[0];
  const markdown =
    currentDoc.source === "skill" ? getSkillMd() : getRefMd(`${currentDoc.slug}.md`);

  const handleSelect = (s: string) => {
    setActiveSlug(s);
    navigate(`/docs/${s === "skill" ? "skill" : s}`, { replace: true });
  };

  return (
    <div style={{ display: "flex", minHeight: "calc(100vh - 52px)" }}>
      {/* Sidebar */}
      <aside
        style={{
          width: 260,
          flexShrink: 0,
          background: "var(--color-surface)",
          borderRight: "1px solid var(--color-border)",
          padding: "20px 0",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "0 20px 16px",
            borderBottom: "1px solid var(--color-border)",
            marginBottom: 8,
          }}
        >
          <BookOpen size={16} style={{ color: "var(--color-accent)" }} />
          <span style={{ fontWeight: 600, fontSize: 14, color: "var(--color-text-primary)" }}>
            {t("docs.sidebarTitle")}
          </span>
        </div>

        {DOC_ENTRIES.map((doc) => (
          <button
            key={doc.slug}
            onClick={() => handleSelect(doc.slug)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              width: "100%",
              padding: "9px 20px",
              border: "none",
              background: activeSlug === doc.slug ? "var(--color-accent-muted)" : "transparent",
              color:
                activeSlug === doc.slug
                  ? "var(--color-accent)"
                  : "var(--color-text-secondary)",
              cursor: "pointer",
              fontSize: 13,
              lineHeight: 1.4,
              textAlign: "left",
              fontFamily: "inherit",
              transition: "background 0.15s",
            }}
          >
            <FileText size={14} style={{ flexShrink: 0, opacity: 0.7 }} />
            {doc.title}
            {activeSlug === doc.slug && (
              <ChevronRight size={14} style={{ marginLeft: "auto", flexShrink: 0 }} />
            )}
          </button>
        ))}

        <div
          style={{
            margin: "20px 20px 0",
            padding: "12px",
            borderRadius: 8,
            background: "var(--color-surface-alt)",
            fontSize: 12,
            color: "var(--color-text-tertiary)",
            lineHeight: 1.5,
          }}
        >
          {t("docs.footerNote")}
        </div>
      </aside>

      {/* Content */}
      <main style={{ flex: 1, overflow: "auto", padding: "32px 40px" }}>
        <style>{`
          .docs-md table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 14px;
          }
          .docs-md th {
            text-align: left;
            padding: 10px 12px;
            background: var(--color-surface-alt);
            border-bottom: 2px solid var(--color-accent-muted);
            color: var(--color-text-secondary);
            font-weight: 600;
            font-size: 13px;
          }
          .docs-md td {
            padding: 10px 12px;
            border-bottom: 1px solid var(--color-border);
            color: var(--color-text-primary);
            vertical-align: top;
          }
          .docs-md tr:nth-child(even) td {
            background: oklch(0.97 0.004 150 / 0.5);
          }
          .docs-md h1 {
            font-size: 26px;
            font-weight: 700;
            color: var(--color-text-primary);
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--color-accent-muted);
          }
          .docs-md h2 {
            font-size: 20px;
            font-weight: 600;
            color: var(--color-text-primary);
            margin-top: 32px;
            margin-bottom: 12px;
            padding-bottom: 6px;
            border-bottom: 1px solid var(--color-accent-muted);
          }
          .docs-md h3 {
            font-size: 16px;
            font-weight: 600;
            color: var(--color-text-primary);
            margin-top: 24px;
            margin-bottom: 8px;
          }
          .docs-md h4 {
            font-size: 14px;
            font-weight: 600;
            color: var(--color-text-secondary);
            margin-top: 20px;
            margin-bottom: 6px;
          }
          .docs-md p {
            color: var(--color-text-secondary);
            line-height: 1.7;
            margin-bottom: 12px;
          }
          .docs-md a {
            color: var(--color-accent);
            text-decoration: none;
          }
          .docs-md a:hover {
            text-decoration: underline;
          }
          .docs-md code {
            background: var(--color-surface-alt);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "SF Mono", "Fira Code", "Fira Mono", "Roboto Mono", monospace;
            font-size: 13px;
            color: var(--color-text-primary);
          }
          .docs-md pre {
            background: var(--color-surface-alt);
            padding: 14px 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid var(--color-border);
            font-size: 13px;
            line-height: 1.5;
          }
          .docs-md pre code {
            background: none;
            padding: 0;
            font-size: 13px;
          }
          .docs-md blockquote {
            border-left: 3px solid var(--color-accent);
            padding-left: 14px;
            color: var(--color-text-tertiary);
            margin: 12px 0;
          }
          .docs-md ul, .docs-md ol {
            color: var(--color-text-secondary);
            padding-left: 24px;
            margin-bottom: 12px;
          }
          .docs-md li {
            margin-bottom: 4px;
            line-height: 1.6;
          }
          .docs-md hr {
            border: none;
            border-top: 1px solid var(--color-border);
            margin: 24px 0;
          }
          .docs-md strong {
            color: var(--color-text-primary);
          }
        `}</style>
        <div
          className="docs-md"
          style={{ maxWidth: 860, margin: "0 auto" }}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
        </div>
      </main>
    </div>
  );
}
