import { useCallback, useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
} from "reactflow";
import type { Node, Edge } from "reactflow";
import "reactflow/dist/style.css";
import type { PipelineStep } from "../types/pipeline";
import { useStore } from "../store/useStore";

const NODE_THEMES = [
  { accent: "var(--color-node-dna)", bg: "oklch(0.96 0.02 160)", border: "oklch(0.80 0.08 160)" },
  { accent: "var(--color-node-rna)", bg: "oklch(0.97 0.01 240)", border: "oklch(0.82 0.06 240)" },
  { accent: "var(--color-node-epi)", bg: "oklch(0.97 0.01 300)", border: "oklch(0.82 0.06 310)" },
  { accent: "var(--color-node-micro)", bg: "oklch(0.97 0.02 80)", border: "oklch(0.82 0.08 80)" },
];

function StepNode({ data }: { data: { label: string; tool: string; index: number; total: number } }) {
  const theme = NODE_THEMES[data.index % NODE_THEMES.length];
  return (
    <>
      <Handle type="target" position={Position.Top} style={{ visibility: "hidden" }} />
      <div
        className="relative flex items-center gap-0 rounded-xl overflow-hidden group"
        style={{
          background: theme.bg,
          border: `1px solid ${theme.border}`,
          minWidth: 220,
          boxShadow: "0 1px 3px oklch(0 0 0 / 0.06)",
          transition: "box-shadow 0.2s, transform 0.2s",
          cursor: "pointer",
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.boxShadow =
            `0 0 0 2px ${theme.accent}, 0 4px 16px oklch(0 0 0 / 0.08)`;
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.boxShadow = "0 1px 3px oklch(0 0 0 / 0.06)";
        }}
      >
        <div className="w-1.5 self-stretch shrink-0" style={{ background: theme.accent }} />

        <div
          className="flex items-center justify-center shrink-0 w-8 h-8 rounded-full text-xs font-bold ml-3"
          style={{ background: theme.accent, color: "#fff" }}
        >
          {data.index + 1}
        </div>

        <div className="flex-1 px-3 py-2.5 min-w-0">
          <div className="text-sm font-semibold text-text-primary truncate">{data.label}</div>
          <div
            className="text-xs mt-0.5 font-mono truncate"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {data.tool}
          </div>
        </div>

        <div className="pr-3 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path
              d="M6 4l4 4-4 4"
              stroke="var(--color-accent)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        {data.index === 0 && (
          <div
            className="absolute -top-2 right-3 text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full"
            style={{ background: theme.accent, color: "#fff" }}
          >
            START
          </div>
        )}
        {data.index === data.total - 1 && (
          <div
            className="absolute -bottom-2 right-3 text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full"
            style={{ background: theme.accent, color: "#fff" }}
          >
            END
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} style={{ visibility: "hidden" }} />
    </>
  );
}

const nodeTypes = { stepNode: StepNode };

export default function FlowCanvas({ steps }: { steps: PipelineStep[] }) {
  const { setSelectedStep } = useStore();

  const initialNodes: Node[] = useMemo(
    () =>
      steps.map((step, i) => ({
        id: step.id,
        type: "stepNode",
        position: step.position,
        data: {
          label: step.name,
          tool: step.tools[0]?.name || "",
          index: i,
          total: steps.length,
        },
      })),
    [steps]
  );

  const initialEdges: Edge[] = useMemo(
    () =>
      steps.slice(0, -1).map((_, i) => ({
        id: `e-${steps[i].id}-${steps[i + 1].id}`,
        source: steps[i].id,
        target: steps[i + 1].id,
        animated: true,
        style: {
          stroke: "var(--color-accent)",
          strokeWidth: 2,
          strokeDasharray: "6 3",
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: "var(--color-accent)",
          width: 16,
          height: 16,
        },
      })),
    [steps]
  );

  const [nodes] = useNodesState(initialNodes);
  const [edges] = useEdgesState(initialEdges);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const step = steps.find((s) => s.id === node.id);
      if (step) setSelectedStep(step);
    },
    [steps, setSelectedStep]
  );

  return (
    <div
      className="w-full h-full rounded-xl overflow-hidden"
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
      }}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{ padding: 0.4 }}
        defaultEdgeOptions={{ type: "smoothstep" }}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="var(--color-border)" gap={24} size={0.5} />
        <Controls
          style={{
            background: "var(--color-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: 10,
            overflow: "hidden",
          }}
        />
        <MiniMap
          style={{
            background: "var(--color-surface-alt)",
            border: "1px solid var(--color-border)",
            borderRadius: 8,
          }}
          maskColor="oklch(0.97 0.005 140 / 0.6)"
          nodeColor="var(--color-accent)"
        />
      </ReactFlow>
    </div>
  );
}
