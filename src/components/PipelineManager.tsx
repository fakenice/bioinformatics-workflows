import { useState } from "react";
import { useStore } from "../store/useStore";
import { useT } from "../i18n";

const COLOR_PALETTE = [
  { name: "DNA Green",   value: "var(--color-node-dna)" },
  { name: "RNA Blue",    value: "var(--color-node-rna)" },
  { name: "Epi Purple",  value: "var(--color-node-epi)" },
  { name: "Micro Yellow",value: "var(--color-node-micro)" },
  { name: "Teal",        value: "#0d9488" },
  { name: "Orange",      value: "#ea580c" },
  { name: "Pink",        value: "#db2777" },
  { name: "Indigo",      value: "#4f46e5" },
  { name: "Rose",        value: "#e11d48" },
  { name: "Cyan",        value: "#0891b2" },
  { name: "Lime",        value: "#65a30d" },
  { name: "Violet",      value: "#7c3aed" },
];

function slugify(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export default function PipelineManager() {
  const {
    pipelines,
    hiddenPipelines,
    toggleHidden,
    resetOrder,
    deletePipeline,
    changePipelineCategory,
    categoryTree,
    addSubCategory,
    addTopLevelCategory,
    deleteTopLevelCategory,
  } = useStore();
  const t = useT();

  // ── collapse state ───────────────────────────────────────────
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());

  // ── pipeline row state ───────────────────────────────────────
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [editingCategory, setEditingCategory] = useState<string | null>(null);

  // ── add sub-category state ───────────────────────────────────
  const [addSubParent, setAddSubParent] = useState("");
  const [subLabel, setSubLabel] = useState("");
  const [subLabelZH, setSubLabelZH] = useState("");

  // ── add top-level state ──────────────────────────────────────
  const [showAddTop, setShowAddTop] = useState(false);
  const [topId, setTopId] = useState("");
  const [topLabel, setTopLabel] = useState("");
  const [topLabelZH, setTopLabelZH] = useState("");
  const [topAccent, setTopAccent] = useState(COLOR_PALETTE[0].value);

  // ── delete parent confirmation ───────────────────────────────
  const [deleteParentConfirm, setDeleteParentConfirm] = useState<string | null>(null);

  // ── feedback toast ───────────────────────────────────────────
  const [feedback, setFeedback] = useState<{ type: "ok" | "err"; text: string } | null>(null);

  // ── helpers ──────────────────────────────────────────────────
  function getName(id: string): string {
    return t(`pipeline.${id}.name`);
  }

  function catLabel(cat: string): string {
    const key = `categories.${cat}`;
    const trans = t(key);
    return trans !== key ? trans : cat;
  }

  function showFeedback(type: "ok" | "err", text: string) {
    setFeedback({ type, text });
    setTimeout(() => setFeedback(null), 3000);
  }

  // ── build flat category options for dropdown ──────────────────
  const categoryOptions: { id: string; label: string }[] = [];
  for (const [_pid, parent] of Object.entries(categoryTree)) {
    if (parent.children) {
      for (const [cid, child] of Object.entries(parent.children)) {
        categoryOptions.push({ id: cid, label: `${parent.labelZH} / ${child.labelZH}` });
      }
    }
  }

  // Group pipelines by top-level parent
  const parentKeys = Object.keys(categoryTree);
  const defaultParentOrder = ["dna", "rna", "epigenetics", "microbiome"];
  const sortedParentKeys = [
    ...defaultParentOrder.filter((k) => categoryTree[k]),
    ...parentKeys.filter((k) => !defaultParentOrder.includes(k)),
  ];

  const groupMap: Record<string, typeof pipelines> = {};
  for (const pid of sortedParentKeys) {
    groupMap[pid] = pipelines.filter((p) => p.category.startsWith(pid + "."));
  }

  function toggleCollapse(pid: string) {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(pid)) next.delete(pid);
      else next.add(pid);
      return next;
    });
  }

  // ── add sub-category ─────────────────────────────────────────
  function handleAddSub() {
    if (!addSubParent || !subLabel.trim() || !subLabelZH.trim()) return;
    const childId = `${addSubParent}.${slugify(subLabel)}`;
    addSubCategory(addSubParent, childId, subLabel.trim(), subLabelZH.trim());
    showFeedback("ok", `Added "${subLabel.trim()}"`);
    setSubLabel("");
    setSubLabelZH("");
    setAddSubParent("");
  }

  // ── add top-level ────────────────────────────────────────────
  function handleAddTop() {
    if (!topId.trim() || !topLabel.trim() || !topLabelZH.trim()) return;
    const id = slugify(topId.trim());
    if (categoryTree[id]) {
      showFeedback("err", t("manager.categories.duplicate"));
      return;
    }
    addTopLevelCategory(id, topLabel.trim(), topLabelZH.trim(), topAccent);
    showFeedback("ok", `Added "${topLabel.trim()}"`);
    setTopId("");
    setTopLabel("");
    setTopLabelZH("");
    setTopAccent(COLOR_PALETTE[0].value);
    setShowAddTop(false);
  }

  // ── delete top-level parent ──────────────────────────────────
  function handleDeleteParent(pid: string) {
    deleteTopLevelCategory(pid);
    showFeedback("ok", `Deleted "${pid}"`);
    setDeleteParentConfirm(null);
  }

  // ── reset ────────────────────────────────────────────────────
  function handleReset() {
    localStorage.removeItem("flowseq-categories");
    resetOrder();
    showFeedback("ok", t("manager.resetDone"));
  }

  // ── build status state ───────────────────────────────────────
  const [building, setBuilding] = useState(false);

  // ── update project ───────────────────────────────────────────
  async function handleUpdateProject() {
    setBuilding(true);

    // Collect localStorage data
    const rawCategories = localStorage.getItem("flowseq-categories");
    const rawDeleted = localStorage.getItem("flowseq-deleted");
    const rawCategoryMap = localStorage.getItem("flowseq-category-map");

    const body: Record<string, unknown> = {};
    if (rawCategories) {
      try { body.categoryOverrides = JSON.parse(rawCategories); } catch { /* ignore */ }
    }
    if (rawDeleted) {
      try { body.deletedPipelines = JSON.parse(rawDeleted); } catch { /* ignore */ }
    }
    if (rawCategoryMap) {
      try { body.categoryMap = JSON.parse(rawCategoryMap); } catch { /* ignore */ }
    }

    try {
      const resp = await fetch("/api/build-project", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const result = await resp.json();

      if (result.success) {
        showFeedback("ok", t("manager.buildSuccess"));
      } else {
        const errMsg = result.error || "Unknown error";
        showFeedback("err", `${t("manager.buildFailed")}: ${errMsg.slice(0, 120)}`);
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      showFeedback("err", `${t("manager.buildFailed")}: ${msg.slice(0, 120)}`);
    } finally {
      setBuilding(false);
    }
  }

  // ── render ───────────────────────────────────────────────────
  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-16">
      {/* header */}
      <div className="flex items-start justify-between mb-5">
        <div>
          <h1 className="text-2xl font-bold">{t("manager.title")}</h1>
          <p className="text-sm mt-1" style={{ color: "var(--color-text-tertiary)" }}>
            {t("manager.desc")}
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleReset}
            className="px-3 py-1.5 text-sm rounded-full border transition-colors"
            style={{ borderColor: "var(--color-text-tertiary)", color: "var(--color-text-tertiary)" }}
            onMouseOver={(e) => {
              e.currentTarget.style.borderColor = "var(--color-accent)";
              e.currentTarget.style.color = "var(--color-accent)";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.borderColor = "var(--color-text-tertiary)";
              e.currentTarget.style.color = "var(--color-text-tertiary)";
            }}
          >
            {t("manager.reset")}
          </button>
          <button
            onClick={handleUpdateProject}
            disabled={building}
            className="px-3 py-1.5 text-sm rounded-full border transition-colors"
            style={{ borderColor: "var(--color-accent)", color: "var(--color-accent)", opacity: building ? 0.6 : 1 }}
            onMouseOver={(e) => {
              if (!building) e.currentTarget.style.background = "var(--color-accent-muted)";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = "transparent";
            }}
          >
            {building ? t("manager.building") : t("manager.categories.updateProject")}
          </button>
        </div>
      </div>

      {/* feedback toast */}
      {feedback && (
        <div
          className="mb-4 px-3 py-2 text-sm rounded-lg"
          style={{
            background: feedback.type === "ok" ? "var(--color-accent-muted)" : "var(--color-danger-muted)",
            color: feedback.type === "ok" ? "var(--color-accent)" : "var(--color-danger)",
          }}
        >
          {feedback.text}
        </div>
      )}

      {/* ── Pipeline Groups ────────────────────────────────── */}
      {sortedParentKeys.map((pid) => {
        const parent = categoryTree[pid];
        const items = groupMap[pid] || [];
        const isCollapsed = collapsed.has(pid);
        const accent = parent.accent || "var(--color-accent)";
        const canDelete = items.length === 0;
        const isDeletePending = deleteParentConfirm === pid;

        return (
          <section key={pid} className="mb-5">
            {/* group header */}
            <div
              className="flex items-center gap-2 mb-2 cursor-pointer select-none group"
              onClick={() => toggleCollapse(pid)}
            >
              <span className="text-xs shrink-0 transition-transform" style={{ color: "var(--color-text-tertiary)", transform: isCollapsed ? "" : "rotate(90deg)" }}>
                ▶
              </span>
              <span
                className="text-sm font-semibold uppercase tracking-wide"
                style={{ color: accent }}
              >
                {parent.labelZH}
              </span>
              <span className="text-xs" style={{ color: "var(--color-text-tertiary)" }}>
                ({items.length})
              </span>

              {/* [+子类] — stop propagation to prevent collapse toggle */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setAddSubParent(addSubParent === pid ? "" : pid);
                }}
                className="text-xs px-1.5 py-0.5 rounded border transition-colors opacity-0 group-hover:opacity-100"
                style={{
                  borderColor: "var(--color-accent)",
                  color: "var(--color-accent)",
                  background: addSubParent === pid ? "var(--color-accent-muted)" : "transparent",
                }}
              >
                +{t("manager.categories.addSub")}
              </button>

              {/* [✕] delete parent — empty categories can be deleted */}
              {isDeletePending ? (
                  <span className="flex items-center gap-1 text-xs" onClick={(e) => e.stopPropagation()}>
                    <span style={{ color: "var(--color-danger)" }}>{t("manager.categories.deleteConfirmText")}</span>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteParent(pid); }}
                      className="underline font-medium"
                      style={{ color: "var(--color-danger)" }}
                    >
                      {t("manager.categories.deleteConfirm")}
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); setDeleteParentConfirm(null); }}
                      className="underline"
                      style={{ color: "var(--color-text-tertiary)" }}
                    >
                      {t("manager.categories.deleteCancel")}
                    </button>
                  </span>
                ) : (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (canDelete) setDeleteParentConfirm(pid);
                    }}
                    className="text-xs px-1.5 py-0.5 rounded border transition-colors opacity-0 group-hover:opacity-100"
                    style={{
                      borderColor: canDelete ? "var(--color-danger)" : "var(--color-text-tertiary)",
                      color: canDelete ? "var(--color-danger)" : "var(--color-text-tertiary)",
                      opacity: canDelete ? undefined : 0.3,
                      cursor: canDelete ? "pointer" : "not-allowed",
                    }}
                    title={canDelete ? t("manager.categories.deleteParent") : t("manager.categories.deleteParentBlocked")}
                    disabled={!canDelete}
                  >
                    ✕
                  </button>
                )
              }
            </div>

            {/* add sub form inline */}
            {addSubParent === pid && (
              <div className="mb-2 ml-6 flex items-center gap-1.5 flex-wrap">
                <input
                  type="text"
                  placeholder="Label (EN)"
                  value={subLabel}
                  onChange={(e) => setSubLabel(e.target.value)}
                  className="text-xs px-2 py-1 rounded-md border w-28"
                  style={{ borderColor: "var(--color-border)", background: "var(--color-page)" }}
                />
                <input
                  type="text"
                  placeholder="Label (ZH)"
                  value={subLabelZH}
                  onChange={(e) => setSubLabelZH(e.target.value)}
                  className="text-xs px-2 py-1 rounded-md border w-28"
                  style={{ borderColor: "var(--color-border)", background: "var(--color-page)" }}
                />
                <button
                  onClick={handleAddSub}
                  className="text-xs px-2 py-1 rounded-md font-medium"
                  style={{ background: "var(--color-accent)", color: "#fff" }}
                >
                  {t("manager.categories.confirm")}
                </button>
              </div>
            )}

            {/* pipeline rows */}
            {!isCollapsed && (
              <div className="rounded-xl overflow-hidden ml-4" style={{ background: "var(--color-surface)" }}>
                {items.length === 0 ? (
                  <div
                    className="px-4 py-3 text-xs italic"
                    style={{ color: "var(--color-text-tertiary)" }}
                  >
                    {t("manager.noPipelines")}
                  </div>
                ) : (
                  items.map((p) => {
                    const isHidden = hiddenPipelines.includes(p.id);
                    const isDeletePending = deleteConfirm === p.id;
                    const isEditingCat = editingCategory === p.id;
                    return (
                      <div
                        key={p.id}
                        className="flex items-center gap-3 px-4 py-2.5 transition-colors border-b last:border-b-0"
                        style={{ borderColor: "var(--color-border)" }}
                      >
                        <div className="flex-1 min-w-0">
                          <div
                            className={`text-sm font-medium truncate ${isHidden ? "line-through" : ""}`}
                            style={{
                              color: isHidden ? "var(--color-text-tertiary)" : "var(--color-text-primary)",
                            }}
                          >
                            {getName(p.id)}
                          </div>
                          <div className="text-xs mt-0.5" style={{ color: "var(--color-text-tertiary)" }}>
                            {p.version}
                          </div>
                        </div>

                        {/* category dropdown */}
                        {isEditingCat ? (
                          <select
                            value={p.category}
                            onChange={(e) => {
                              changePipelineCategory(p.id, e.target.value);
                              setEditingCategory(null);
                            }}
                            onBlur={() => setEditingCategory(null)}
                            autoFocus
                            className="shrink-0 text-xs px-2 py-1 rounded-md border"
                            style={{ borderColor: "var(--color-border)", background: "var(--color-page)", maxWidth: "150px" }}
                          >
                            {categoryOptions.map((opt) => (
                              <option key={opt.id} value={opt.id}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <button
                            onClick={() => setEditingCategory(p.id)}
                            className="shrink-0 text-xs px-2 py-1 rounded-full border transition-colors truncate max-w-[140px]"
                            style={{ borderColor: "var(--color-text-tertiary)", color: "var(--color-text-tertiary)" }}
                            title={t("manager.pipelines.changeCategory")}
                          >
                            {catLabel(p.category)}
                          </button>
                        )}

                        <button
                          onClick={() => toggleHidden(p.id)}
                          className={`shrink-0 px-3 py-1 text-xs rounded-full transition-colors border ${
                            isHidden ? "border-transparent" : ""
                          }`}
                          style={
                            isHidden
                              ? { background: "var(--color-accent)", color: "#fff" }
                              : { borderColor: "var(--color-text-tertiary)", color: "var(--color-text-tertiary)" }
                          }
                        >
                          {isHidden ? t("manager.show") : t("manager.hide")}
                        </button>

                        {/* delete button */}
                        {isDeletePending ? (
                          <span className="shrink-0 flex items-center gap-1 text-xs">
                            <span style={{ color: "var(--color-danger)" }}>
                              {t("manager.pipelines.deleteConfirm", { name: getName(p.id) })}
                            </span>
                            <button
                              onClick={() => {
                                deletePipeline(p.id);
                                setDeleteConfirm(null);
                              }}
                              className="underline font-medium"
                              style={{ color: "var(--color-danger)" }}
                            >
                              {t("manager.categories.deleteConfirm")}
                            </button>
                            <button
                              onClick={() => setDeleteConfirm(null)}
                              className="underline"
                              style={{ color: "var(--color-text-tertiary)" }}
                            >
                              {t("manager.categories.deleteCancel")}
                            </button>
                          </span>
                        ) : (
                          <button
                            onClick={() => setDeleteConfirm(p.id)}
                            className="shrink-0 w-7 h-7 flex items-center justify-center rounded-full text-xs transition-colors border-0"
                            style={{ color: "var(--color-text-tertiary)" }}
                            title={t("manager.pipelines.delete")}
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="3,6 5,6 21,6" />
                              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                              <line x1="10" y1="11" x2="10" y2="17" />
                              <line x1="14" y1="11" x2="14" y2="17" />
                            </svg>
                          </button>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            )}
          </section>
        );
      })}

      {/* ── Add Top-Level Category ─────────────────────────── */}
      <div className="mt-6">
        {!showAddTop ? (
          <button
            onClick={() => setShowAddTop(true)}
            className="text-sm px-3 py-2 rounded-lg border border-dashed w-full transition-colors"
            style={{ borderColor: "var(--color-border)", color: "var(--color-text-tertiary)" }}
          >
            + {t("manager.categories.addTop")}
          </button>
        ) : (
          <div
            className="rounded-lg p-3"
            style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)" }}
          >
            <h3 className="text-sm font-semibold mb-2">{t("manager.categories.addTop")}</h3>
            <div className="flex flex-wrap items-end gap-2">
              <div className="flex flex-col gap-1">
                <label className="text-xs" style={{ color: "var(--color-text-tertiary)" }}>ID</label>
                <input
                  type="text"
                  placeholder="e.g. proteomics"
                  value={topId}
                  onChange={(e) => setTopId(e.target.value)}
                  className="text-xs px-2 py-1 rounded-md border w-28"
                  style={{ borderColor: "var(--color-border)", background: "var(--color-page)" }}
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs" style={{ color: "var(--color-text-tertiary)" }}>{t("manager.categories.label")} (EN)</label>
                <input
                  type="text"
                  placeholder="Proteomics"
                  value={topLabel}
                  onChange={(e) => setTopLabel(e.target.value)}
                  className="text-xs px-2 py-1 rounded-md border w-28"
                  style={{ borderColor: "var(--color-border)", background: "var(--color-page)" }}
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs" style={{ color: "var(--color-text-tertiary)" }}>{t("manager.categories.labelZH")} (ZH)</label>
                <input
                  type="text"
                  placeholder="蛋白质组"
                  value={topLabelZH}
                  onChange={(e) => setTopLabelZH(e.target.value)}
                  className="text-xs px-2 py-1 rounded-md border w-28"
                  style={{ borderColor: "var(--color-border)", background: "var(--color-page)" }}
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs" style={{ color: "var(--color-text-tertiary)" }}>{t("manager.categories.accent")}</label>
                <div className="flex gap-1 flex-wrap">
                  {COLOR_PALETTE.map((c) => (
                    <button
                      key={c.value}
                      onClick={() => setTopAccent(c.value)}
                      className="w-5 h-5 rounded-full border-2 transition-colors"
                      style={{
                        background: c.value,
                        borderColor: topAccent === c.value ? "var(--color-text-primary)" : "transparent",
                      }}
                      title={c.name}
                    />
                  ))}
                </div>
              </div>
              <button
                onClick={handleAddTop}
                className="text-xs px-3 py-1 rounded-md font-medium h-[26px]"
                style={{ background: "var(--color-accent)", color: "#fff" }}
              >
                {t("manager.categories.confirm")}
              </button>
              <button
                onClick={() => setShowAddTop(false)}
                className="text-xs px-3 py-1 rounded-md font-medium h-[26px]"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                {t("manager.categories.deleteCancel")}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
