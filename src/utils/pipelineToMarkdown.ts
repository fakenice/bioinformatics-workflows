import type { PipelineDefinition, PipelineSource } from "../types/pipeline";

const SOURCE_TYPE_LABEL: Record<string, string> = {
  official: "Official",
  community: "Community",
  paper: "Paper",
};

const REF_TYPE_LABEL: Record<string, string> = {
  official: "Official",
  community: "Community",
  paper: "Paper",
};

export function pipelineToMarkdown(pipeline: PipelineDefinition, sourceId: string): string {
  const source: PipelineSource | undefined =
    pipeline.sources.find((s) => s.id === sourceId) || pipeline.sources[0];

  if (!source) {
    return `# ${pipeline.nameZH}\n\n> No source data available.`;
  }

  const lines: string[] = [];

  // Title
  lines.push(`# ${pipeline.nameZH}`);
  lines.push("");

  // Source line
  const typeLabel = SOURCE_TYPE_LABEL[source.type] || source.type;
  lines.push(`**Source**: ${source.name} | [${typeLabel}](${source.url})`);
  lines.push("");

  // Overview
  lines.push("## 概述");
  lines.push("");
  lines.push(pipeline.overview);
  lines.push("");

  // Steps table
  lines.push("## 流程步骤");
  lines.push("");
  if (source.steps.length === 0) {
    lines.push("暂无步骤数据");
    lines.push("");
  } else {
    lines.push("| # | 步骤 | 推荐工具 | 关键参数 | 说明 |");
    lines.push("|---|------|---------|---------|------|");
    for (let i = 0; i < source.steps.length; i++) {
      const step = source.steps[i];
      const toolsCell = step.tools
        .map((t) => `${t.name}${t.version ? ` (v${t.version})` : ""}`)
        .join(", ");
      const firstParam = step.tools[0]?.params || "";
      let paramsCell = firstParam;
      if (paramsCell.length > 60) {
        paramsCell = paramsCell.slice(0, 60) + "...";
      }
      const notesCell = step.notes || "";
      lines.push(
        `| ${i + 1} | ${escapeMd(step.name)} | ${escapeMd(toolsCell)} | ${escapeMd(paramsCell)} | ${escapeMd(notesCell)} |`
      );
    }
    lines.push("");
  }

  // References
  lines.push("## 参考文献");
  lines.push("");
  if (source.references.length === 0) {
    lines.push("暂无参考文献");
    lines.push("");
  } else {
    lines.push("| 标题 | 类型 | 链接 |");
    lines.push("|------|------|------|");
    for (const ref of source.references) {
      const rType = REF_TYPE_LABEL[ref.type] || ref.type;
      lines.push(`| ${escapeMd(ref.title)} | ${rType} | [${rType}](${ref.url}) |`);
    }
    lines.push("");
  }

  return lines.join("\n");
}

function escapeMd(text: string): string {
  return text.replace(/\|/g, "\\|").replace(/\n/g, " ");
}
