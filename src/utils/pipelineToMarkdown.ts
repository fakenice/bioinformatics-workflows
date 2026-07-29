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

export function pipelineToMarkdown(
  pipeline: PipelineDefinition,
  sourceId: string,
  lang: string = "zh"
): string {
  const source: PipelineSource | undefined =
    pipeline.sources.find((s) => s.id === sourceId) || pipeline.sources[0];

  if (!source) {
    return `# ${pipeline.nameZH}\n\n> No source data available.`;
  }

  const isEn = lang === "en";

  const lines: string[] = [];

  // Title
  const titleText = isEn ? (pipeline.nameEn || pipeline.name) : pipeline.nameZH;
  lines.push(`# ${titleText}`);
  lines.push("");

  // Source line
  const typeLabel = SOURCE_TYPE_LABEL[source.type] || source.type;
  const sourceName = isEn ? (source.nameEn || source.name) : source.name;
  lines.push(`**Source**: ${sourceName} | [${typeLabel}](${source.url})`);
  lines.push("");

  // Overview
  const overviewText = isEn ? (pipeline.overviewEn || pipeline.overview) : pipeline.overview;
  lines.push(`## ${isEn ? "Overview" : "概述"}`);
  lines.push("");
  lines.push(overviewText);
  lines.push("");

  // Steps table
  lines.push(`## ${isEn ? "Workflow Steps" : "流程步骤"}`);
  lines.push("");
  if (source.steps.length === 0) {
    lines.push(isEn ? "No steps available" : "暂无步骤数据");
    lines.push("");
  } else {
    const stepHeader = isEn ? "Step" : "步骤";
    const toolHeader = isEn ? "Recommended Tools" : "推荐工具";
    const paramHeader = isEn ? "Key Parameters" : "关键参数";
    const noteHeader = isEn ? "Notes" : "说明";
    lines.push(`| # | ${stepHeader} | ${toolHeader} | ${paramHeader} | ${noteHeader} |`);
    lines.push("|---|------|---------|---------|------|");
    for (let i = 0; i < source.steps.length; i++) {
      const step = source.steps[i];
      const stepName = isEn ? (step.nameEn || step.name) : step.name;
      const toolsCell = step.tools
        .map((t) => `${t.name}${t.version ? ` (v${t.version})` : ""}`)
        .join(", ");
      const firstParam = step.tools[0]?.params || "";
      let paramsCell = firstParam;
      if (paramsCell.length > 60) {
        paramsCell = paramsCell.slice(0, 60) + "...";
      }
      const notesCell = isEn
        ? (step.notesEn || step.notes || "")
        : (step.notes || "");
      lines.push(
        `| ${i + 1} | ${escapeMd(stepName)} | ${escapeMd(toolsCell)} | ${escapeMd(paramsCell)} | ${escapeMd(notesCell)} |`
      );
    }
    lines.push("");
  }

  // References
  lines.push(`## ${isEn ? "References" : "参考文献"}`);
  lines.push("");
  if (!source.references || source.references.length === 0) {
    lines.push(isEn ? "No references available" : "暂无参考文献");
    lines.push("");
  } else {
    const refTitleHeader = isEn ? "Title" : "标题";
    const refTypeHeader = isEn ? "Type" : "类型";
    const refLinkHeader = isEn ? "Link" : "链接";
    lines.push(`| ${refTitleHeader} | ${refTypeHeader} | ${refLinkHeader} |`);
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
