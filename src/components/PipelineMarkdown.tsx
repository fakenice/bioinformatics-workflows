import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { PipelineDefinition } from "../types/pipeline";
import { pipelineToMarkdown } from "../utils/pipelineToMarkdown";
import { useLanguage } from "../i18n";

interface PipelineMarkdownProps {
  pipeline: PipelineDefinition;
  sourceId?: string;
}

export default function PipelineMarkdown({ pipeline, sourceId }: PipelineMarkdownProps) {
  const { lang } = useLanguage();
  const effectiveSourceId = sourceId ?? pipeline.sources[0]?.id ?? "";
  const markdown = pipelineToMarkdown(pipeline, effectiveSourceId, lang);

  return (
    <div
      style={{
        background: "var(--color-surface)",
        borderRadius: 16,
        padding: "32px 36px",
        maxWidth: 900,
        margin: "0 auto",
        boxShadow: "var(--shadow-sm)",
      }}
    >
      <style>{`
        .pipeline-md table {
          width: 100%;
          border-collapse: collapse;
          margin: 16px 0;
          font-size: 14px;
        }
        .pipeline-md th {
          text-align: left;
          padding: 10px 12px;
          background: var(--color-surface-alt);
          border-bottom: 2px solid var(--color-accent-muted);
          color: var(--color-text-secondary);
          font-weight: 600;
          font-size: 13px;
        }
        .pipeline-md td {
          padding: 10px 12px;
          border-bottom: 1px solid var(--color-border);
          color: var(--color-text-primary);
          vertical-align: top;
        }
        .pipeline-md tr:nth-child(even) td {
          background: oklch(0.97 0.004 150 / 0.5);
        }
        .pipeline-md h1 {
          font-size: 24px;
          font-weight: 700;
          color: var(--color-text-primary);
          margin-bottom: 8px;
        }
        .pipeline-md h2 {
          font-size: 18px;
          font-weight: 600;
          color: var(--color-text-primary);
          margin-top: 28px;
          margin-bottom: 12px;
          padding-bottom: 6px;
          border-bottom: 1px solid var(--color-accent-muted);
        }
        .pipeline-md p {
          color: var(--color-text-secondary);
          line-height: 1.7;
          margin-bottom: 10px;
        }
        .pipeline-md a {
          color: var(--color-accent);
          text-decoration: none;
        }
        .pipeline-md a:hover {
          text-decoration: underline;
        }
        .pipeline-md code {
          background: var(--color-surface-alt);
          padding: 2px 6px;
          border-radius: 4px;
          font-family: "SF Mono", "Fira Code", "Fira Mono", "Roboto Mono", monospace;
          font-size: 13px;
          color: var(--color-text-primary);
        }
        .pipeline-md pre {
          background: var(--color-surface-alt);
          padding: 14px 16px;
          border-radius: 8px;
          overflow-x: auto;
          border: 1px solid var(--color-border);
        }
        .pipeline-md pre code {
          background: none;
          padding: 0;
          font-size: 13px;
        }
        .pipeline-md blockquote {
          border-left: 3px solid var(--color-accent);
          padding-left: 14px;
          color: var(--color-text-tertiary);
          margin: 12px 0;
        }
      `}</style>
      <div className="pipeline-md prose prose-sm max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
      </div>
    </div>
  );
}
