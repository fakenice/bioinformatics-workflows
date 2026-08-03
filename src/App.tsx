import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import HomePage from "./pages/HomePage";
import PipelinePage from "./pages/PipelinePage";
import ComparePage from "./pages/ComparePage";
import DocsPage from "./pages/DocsPage";
import PipelineManager from "./components/PipelineManager";

export default function App() {
  return (
    <BrowserRouter basename="/bioinformatics-workflows">
      <div className="min-h-screen" style={{ background: "var(--color-page)" }}>
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/pipeline/:id" element={<PipelinePage />} />
          <Route path="/compare/:id" element={<ComparePage />} />
          <Route path="/docs" element={<DocsPage />} />
          <Route path="/docs/:slug" element={<DocsPage />} />
          <Route path="/manager" element={<PipelineManager />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
