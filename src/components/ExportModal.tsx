import { useState } from "react";
import { Code, Copy, Download, X } from "lucide-react";

interface ExportModalProps {
  open: boolean;
  onClose: () => void;
  script: string;
  fileName: string;
}

export default function ExportModal({
  open,
  onClose,
  script,
  fileName,
}: ExportModalProps) {
  const [copied, setCopied] = useState(false);

  if (!open) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(script);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard may be unavailable; ignore silently
    }
  };

  const handleDownload = () => {
    const blob = new Blob([script], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(20, 24, 22, 0.55)",
        backdropFilter: "blur(8px)",
        padding: 24,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(820px, 100%)",
          maxHeight: "85vh",
          display: "flex",
          flexDirection: "column",
          background: "var(--color-surface)",
          borderRadius: 16,
          boxShadow: "0 20px 60px rgba(0,0,0,0.25)",
          border: "1px solid var(--color-border)",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "16px 20px",
            borderBottom: "1px solid var(--color-border)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Code size={18} style={{ color: "var(--color-accent)" }} />
            <span
              style={{
                fontWeight: 600,
                fontSize: 15,
                color: "var(--color-text-primary)",
              }}
            >
              导出 Nextflow 脚本
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <button
              onClick={handleCopy}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "7px 14px",
                borderRadius: 8,
                border: "1px solid var(--color-border)",
                background: "var(--color-surface-alt)",
                color: "var(--color-text-secondary)",
                fontSize: 13,
                fontWeight: 500,
                cursor: "pointer",
                fontFamily: "inherit",
              }}
            >
              <Copy size={14} />
              {copied ? "已复制" : "复制脚本"}
            </button>
            <button
              onClick={handleDownload}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "7px 14px",
                borderRadius: 8,
                border: "none",
                background: "var(--color-accent)",
                color: "#fff",
                fontSize: 13,
                fontWeight: 500,
                cursor: "pointer",
                fontFamily: "inherit",
              }}
            >
              <Download size={14} />
              下载 .nf
            </button>
            <button
              onClick={onClose}
              aria-label="关闭"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 32,
                height: 32,
                borderRadius: 8,
                border: "none",
                background: "transparent",
                color: "var(--color-text-tertiary)",
                cursor: "pointer",
              }}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Code block */}
        <div
          style={{
            flex: 1,
            overflow: "auto",
            background: "#1a1f1c",
            padding: "18px 20px",
          }}
        >
          <pre
            style={{
              margin: 0,
              fontFamily:
                '"SF Mono", "Fira Code", "Fira Mono", "Roboto Mono", monospace',
              fontSize: 13,
              lineHeight: 1.6,
              color: "#d6e4dc",
              whiteSpace: "pre",
            }}
          >
            {script}
          </pre>
        </div>
      </div>
    </div>
  );
}
