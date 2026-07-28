import type { I18nStrings } from "./en";

const zh: I18nStrings = {
  header: {
    searchPlaceholder: "搜索分析类型、工具名称… (Ctrl+K)",
    docs: "Skill 文档",
  },
  home: {
    title: "生物信息学分析流程导航",
    subtitle:
      "选择分析场景，查看标准化流程、推荐工具与权威文献。覆盖 DNA、RNA、表观遗传和微生物四大领域。",
    searchPlaceholder: "搜索分析类型、工具名称… (Ctrl+K)",
    noResults: "没有找到匹配的分析流程",
    noResultsHint: "尝试使用其他关键词或切换分类筛选",
  },
  categories: {
    dna: "DNA 分析",
    rna: "RNA 分析",
    epigenetics: "表观遗传",
    microbiome: "微生物组",
  },
  pipeline: {
    back: "返回",
    export: "导出 .nf",
    compare: "对比模式",
    version: "v",
    loading: "加载分析流程...",
    compareMode: "对比模式",
  },
  export: {
    title: "导出 Nextflow 脚本",
    copy: "复制脚本",
    copied: "已复制",
    download: "下载 .nf",
    close: "关闭",
  },
  search: {
    title: "搜索",
    placeholder: "搜索管线、文档…",
    pipelines: "管线",
    docs: "文档",
    noResults: "未找到匹配结果",
    close: "关闭",
  },
};

export default zh;
