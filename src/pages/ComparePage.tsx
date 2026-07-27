import { useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useStore } from "../store/useStore";
import FlowCanvas from "../components/FlowCanvas";

export default function ComparePage() {
  const { id } = useParams<{ id: string }>();
  const { selectPipeline, selectedPipeline } = useStore();

  useEffect(() => {
    if (id) selectPipeline(id);
  }, [id, selectPipeline]);

  if (!selectedPipeline || selectedPipeline.sources.length < 2) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <p className="text-slate-500">此分析类型仅有一个参考来源，无法对比。</p>
        <Link to={`/pipeline/${id}`} className="text-emerald-400 hover:underline text-sm mt-2 inline-block">
          返回流程图
        </Link>
      </div>
    );
  }

  const leftSource = selectedPipeline.sources[0];
  const rightSource = selectedPipeline.sources[1];

  const leftSteps = leftSource.steps;
  const rightSteps = rightSource.steps;
  const maxLen = Math.max(leftSteps.length, rightSteps.length);

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex items-center gap-3 mb-4">
        <Link
          to={`/pipeline/${selectedPipeline.id}`}
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <h1 className="text-xl font-bold text-white">
          {selectedPipeline.nameZH} — 流程对比
        </h1>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <h2 className="text-sm font-semibold text-emerald-400 mb-2">{leftSource.name}</h2>
          <div className="h-[400px]">
            <FlowCanvas steps={leftSteps} />
          </div>
          <StepList steps={leftSteps} maxLen={maxLen} color="emerald" />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-blue-400 mb-2">{rightSource.name}</h2>
          <div className="h-[400px]">
            <FlowCanvas steps={rightSteps} />
          </div>
          <StepList steps={rightSteps} maxLen={maxLen} color="blue" />
        </div>
      </div>
    </div>
  );
}

function StepList({
  steps,
  maxLen,
  color,
}: {
  steps: { name: string }[];
  maxLen: number;
  color: string;
}) {
  return (
    <div className="mt-3 space-y-1.5">
      {Array.from({ length: maxLen }).map((_, i) => {
        const step = steps[i];
        return (
          <div
            key={i}
            className={`text-xs px-2 py-1 rounded ${
              step
                ? `bg-${color}-500/10 text-${color}-300`
                : "bg-slate-800/30 text-slate-600 italic"
            }`}
          >
            {step ? step.name : "（无对应步骤）"}
          </div>
        );
      })}
    </div>
  );
}
