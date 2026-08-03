import { useStore } from "../store/useStore";
import { useT } from "../i18n";

export default function CategoryTabs() {
  const { selectedCategory, setSelectedCategory, categoryTree } = useStore();
  const parentKeys = Object.keys(categoryTree);
  const t = useT();

  const activeParent = selectedCategory
    ? (selectedCategory.includes(".") ? selectedCategory.split(".")[0] : selectedCategory)
    : null;

  return (
    <div className="flex flex-col gap-2">
      {/* parent tabs */}
      <div className="flex gap-1 flex-wrap">
        <button
          onClick={() => setSelectedCategory(null)}
          className="relative px-3.5 py-2 text-sm font-medium transition-colors"
          style={
            selectedCategory === null
              ? { color: "var(--color-accent)" }
              : { color: "var(--color-text-tertiary)" }
          }
        >
          {t("categories.all")}
          {selectedCategory === null && (
            <span
              className="absolute bottom-0 left-1/2 -translate-x-1/2 w-5 h-0.5 rounded-full"
              style={{ background: "var(--color-accent)" }}
            />
          )}
        </button>
        {parentKeys.map((pid) => {
          const parent = categoryTree[pid];
          const isActive = activeParent === pid;
          return (
            <button
              key={pid}
              onClick={() => setSelectedCategory(isActive ? null : pid)}
              className="relative px-3.5 py-2 text-sm font-medium transition-colors"
              style={{
                color: isActive ? (parent.accent || "var(--color-accent)") : "var(--color-text-tertiary)",
              }}
            >
              {t(`categories.${pid}._name`)}
              {isActive && (
                <span
                  className="absolute bottom-0 left-1/2 -translate-x-1/2 w-5 h-0.5 rounded-full"
                  style={{ background: parent.accent || "var(--color-accent)" }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* child tabs — show when a parent is active */}
      {activeParent && categoryTree[activeParent]?.children && (
        <div className="flex gap-1 flex-wrap ml-4 border-l-2 pl-3" style={{ borderColor: categoryTree[activeParent].accent || "var(--color-accent)" }}>
          <button
            onClick={() => setSelectedCategory(activeParent)}
            className="relative px-3.5 py-1.5 text-xs font-medium transition-colors"
            style={{
              color: selectedCategory === activeParent
                ? (categoryTree[activeParent].accent || "var(--color-accent)")
                : "var(--color-text-tertiary)",
            }}
          >
            {t("categories.allSub")}
            {selectedCategory === activeParent && (
              <span
                className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 rounded-full"
                style={{ background: categoryTree[activeParent].accent || "var(--color-accent)" }}
              />
            )}
          </button>
          {Object.entries(categoryTree[activeParent].children!).map(([cid, _child]) => {
            const isSubActive = selectedCategory === cid;
            return (
              <button
                key={cid}
                onClick={() => setSelectedCategory(cid)}
                className="relative px-3.5 py-1.5 text-xs font-medium transition-colors"
                style={{
                  color: isSubActive
                    ? (categoryTree[activeParent].accent || "var(--color-accent)")
                    : "var(--color-text-tertiary)",
                }}
              >
                {t(`categories.${cid}`)}
                {isSubActive && (
                  <span
                    className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 rounded-full"
                    style={{ background: categoryTree[activeParent].accent || "var(--color-accent)" }}
                  />
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
