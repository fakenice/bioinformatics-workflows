import { useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, GitCompare } from "lucide-react";
import { useStore } from "../store/useStore";
import FlowCanvas from "../components/FlowCanvas";
import DetailPanel from "../components/DetailPanel";
import SourceSwitcher from "../components/SourceSwitcher";
import ReferenceAccordion from "../components/ReferenceAccordion";

export default function PipelinePage() {
  const { id } = useParams<{ id: string }>();
  const { selectPipeline, selectedPipeline, selectedSourceId } = useStore();

  useEffect(() => {
    if (id) selectPipeline(id);
  }, [id, selectPipeline]);

  if (!selectedPipeline) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-500">
        加载中...
      </div>
    );
  }

  const source = selectedPipeline.sources.find((s) => s.id === selectedSourceId) || selectedPipeline.sources[0];

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Link
            to="/"
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-white">{selectedPipeline.nameZH}</h1>
            <p className="text-sm text-slate-400">{selectedPipeline.name}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <SourceSwitcher />
          <Link
            to={`/compare/${selectedPipeline.id}`}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:border-emerald-500/30 hover:text-emerald-400 transition-all"
          >
            <GitCompare className="w-3.5 h-3.5" />
            对比模式
          </Link>
        </div>
      </div>

      <FlowCanvas steps={source.steps} />
      <DetailPanel />
      <ReferenceAccordion references={source.references} />
    </div>
  );
}
