import { useCallback, useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from "reactflow";
import type { Node, Edge } from "reactflow";
import "reactflow/dist/style.css";
import type { PipelineStep } from "../types/pipeline";
import { useStore } from "../store/useStore";

const nodeColors: Record<number, string> = {
  0: "from-emerald-500 to-teal-600",
  1: "from-blue-500 to-cyan-600",
  2: "from-purple-500 to-pink-600",
  3: "from-amber-500 to-orange-600",
};

function StepNode({ data }: { data: { label: string; tool: string; index: number } }) {
  const color = nodeColors[data.index % 4] || nodeColors[0];
  return (
    <div
      className={`px-4 py-3 rounded-xl bg-gradient-to-br ${color} shadow-lg cursor-pointer transition-transform hover:scale-105 min-w-[200px]`}
    >
      <div className="text-xs text-white/60 font-mono">Step {data.index + 1}</div>
      <div className="text-sm font-semibold text-white mt-0.5">{data.label}</div>
      <div className="text-xs text-white/70 mt-1">{data.tool}</div>
    </div>
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
        style: { stroke: "#475569", strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#475569" },
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
    <div className="w-full h-[calc(100vh-180px)] bg-slate-900 rounded-xl border border-slate-800">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        defaultEdgeOptions={{ type: "smoothstep" }}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#1e293b" gap={20} />
        <Controls className="!bg-slate-800 !border-slate-700 !fill-slate-300" />
        <MiniMap
          style={{ backgroundColor: "#0f172a" }}
          maskColor="rgba(15, 23, 42, 0.7)"
          nodeColor="#10b981"
        />
      </ReactFlow>
    </div>
  );
}
