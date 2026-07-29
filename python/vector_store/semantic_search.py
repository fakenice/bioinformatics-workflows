"""
Semantic Search — high-level interface.

Single entry point for semantic search over the FlowSeq knowledge base.
Hides the chunking → embedding → retrieval pipeline behind one function.
"""

from pathlib import Path
from typing import Optional

from vector_store.chroma_client import SearchHit, SearchResult, VectorStore
from vector_store.embedder import DummyEmbedder, EmbedderProvider, OpenAIEmbedder


class SemanticSearcher:
    """
    High-level semantic search over the FlowSeq knowledge base.

    Usage:
        searcher = SemanticSearcher()
        results = searcher.search("GWAS 质量控制标准")
        for hit in results.hits:
            print(hit.source_file, hit.section_title, hit.score)
    """

    def __init__(
        self,
        index_dir: Optional[str] = None,
        embedder: Optional[EmbedderProvider] = None,
    ):
        workspace = Path(__file__).parent.parent.parent
        self.index_dir = index_dir or str(workspace / "python" / "vector_data")
        self.embedder = embedder or DummyEmbedder(dim=128)
        self._store = VectorStore(persist_dir=self.index_dir)

    @property
    def store(self) -> VectorStore:
        return self._store

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_pipeline: Optional[str] = None,
        filter_tag: Optional[str] = None,
    ) -> SearchResult:
        """Semantic search over the knowledge base."""
        return self._store.query(
            query_text=query,
            embedder=self.embedder,
            n_results=n_results,
            filter_pipeline=filter_pipeline,
            filter_tag=filter_tag,
        )

    def format_results(self, results: SearchResult) -> str:
        """Format search results as Markdown for display."""
        lines = [f"## 语义检索结果: \"{results.query}\""]
        lines.append(f"*共检索 {results.total_candidates} 个文档块，返回 Top {len(results.hits)}，耗时 {results.latency_ms:.0f}ms*\n")

        for i, hit in enumerate(results.hits):
            lines.append(f"### {i+1}. {hit.section_title} [得分: {hit.score:.4f}]")
            lines.append(f"| 字段 | 值 |")
            lines.append(f"|------|------|")
            lines.append(f"| 来源 | `{hit.source_file}` |")
            lines.append(f"| 行范围 | L{hit.line_start}-L{hit.line_end} |")
            lines.append(f"| 相关管线 | {', '.join(hit.pipeline_ids) if hit.pipeline_ids else '无'} |")
            lines.append(f"| 标签 | {', '.join(hit.tags) if hit.tags else '无'} |")
            lines.append("")
            lines.append(f"```")
            lines.append(hit.content[:500])
            if len(hit.content) > 500:
                lines.append("...")
            lines.append(f"```")
            lines.append("")

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Standalone test
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    searcher = SemanticSearcher()

    queries = [
        "GWAS 人群分层怎么处理",
        "scRNA-seq 聚类分辨率怎么选",
        "Mutect2 配对肿瘤正常样本过滤",
    ]

    for q in queries:
        results = searcher.search(q, n_results=3)
        print(searcher.format_results(results))
        print("---\n")
