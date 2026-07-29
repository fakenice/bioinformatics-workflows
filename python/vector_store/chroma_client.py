"""
Lightweight vector store for FlowSeq knowledge base.

Uses NumPy + sklearn cosine similarity instead of ChromaDB
to avoid heavy dependency installations. All data persisted as .npy + .json.

Design: each collection = one knowledge domain (references / pipelines).
Metadata on every document enables precise source tracing.
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from vector_store.chunker import Chunk, chunk_all_references, chunk_pipeline_json
from vector_store.embedder import DummyEmbedder, EmbedderProvider, OpenAIEmbedder, embed_chunks, EmbeddingResult


@dataclass
class SearchHit:
    """A single search result with traceability metadata."""
    chunk_id: str
    content: str
    score: float               # Cosine similarity (0 to 1)
    source_file: str           # e.g., "references/study_designs.md"
    section_title: str         # e.g., "## 家系/Trio 分析"
    line_start: int
    line_end: int
    pipeline_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """Aggregated search results."""
    query: str
    hits: list[SearchHit]
    total_candidates: int
    latency_ms: float = 0.0


class VectorStore:
    """
    NumPy-based vector store with sklearn cosine similarity.

    Usage:
        store = VectorStore(persist_dir="./vector_data")
        store.build_index(references_dir, pipelines_dir, embedder)
        results = store.query("GWAS 质量控制标准", embedder)
    """

    def __init__(self, persist_dir: str = "./vector_data"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._embeddings: Optional["np.ndarray"] = None  # type: ignore
        self._documents: list[dict] = []  # Metadata per document

    # ──────────────── Build index ────────────────

    def build_index(
        self,
        references_dir: str,
        pipelines_dir: str,
        embedder: EmbedderProvider,
        force_rebuild: bool = False,
    ) -> int:
        """
        Build the vector index from references .md files and pipeline JSONs.

        Returns:
            Total number of documents indexed
        """
        embeddings_file = self.persist_dir / "embeddings.npy"
        docs_file = self.persist_dir / "documents.json"

        if force_rebuild or not embeddings_file.exists() or not docs_file.exists():
            pass  # Rebuild
        else:
            # Load existing
            import numpy as np
            self._embeddings = np.load(str(embeddings_file))
            self._documents = json.loads(docs_file.read_text(encoding="utf-8"))
            print(f"Loaded existing index: {len(self._documents)} documents")
            return len(self._documents)

        # Chunk references
        print("Chunking reference documents...")
        ref_results = chunk_all_references(references_dir)
        ref_chunks: list[Chunk] = [c for r in ref_results for c in r.chunks]

        # Chunk pipeline JSONs
        print("Chunking pipeline definitions...")
        pipe_chunks = chunk_pipeline_json(pipelines_dir)

        all_chunks = ref_chunks + pipe_chunks
        print(f"Total chunks: {len(all_chunks)} ({len(ref_chunks)} refs + {len(pipe_chunks)} pipelines)")

        if not all_chunks:
            print("No chunks to index.")
            return 0

        # Embed all chunks
        print(f"Embedding {len(all_chunks)} chunks...")
        embedded = embed_chunks(all_chunks, embedder)

        # Build numpy array and document metadata
        import numpy as np

        embeddings_array = np.array([e.embedding for e in embedded], dtype=np.float32)
        documents = []

        for e in embedded:
            c = e.chunk
            documents.append({
                "chunk_id": c.chunk_id,
                "content": c.content,
                "source_file": c.source_file,
                "section_title": c.section_title,
                "line_start": c.line_start,
                "line_end": c.line_end,
                "pipeline_ids": c.pipeline_ids,
                "tags": c.tags,
                "chunk_type": c.chunk_type,
            })

        # Normalize embeddings for cosine similarity
        from sklearn.preprocessing import normalize
        embeddings_array = normalize(embeddings_array)

        # Persist
        np.save(str(embeddings_file), embeddings_array)
        docs_file.write_text(json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8")

        self._embeddings = embeddings_array
        self._documents = documents

        print(f"Index built: {len(documents)} documents, dim={embeddings_array.shape[1]}")
        return len(documents)

    def _ensure_loaded(self):
        """Lazy-load embeddings and documents from disk."""
        if self._embeddings is not None and self._documents:
            return

        embeddings_file = self.persist_dir / "embeddings.npy"
        docs_file = self.persist_dir / "documents.json"

        if not embeddings_file.exists() or not docs_file.exists():
            raise FileNotFoundError(
                f"Index not found at {self.persist_dir}. Run build_index() first."
            )

        import numpy as np

        self._embeddings = np.load(str(embeddings_file))
        self._documents = json.loads(docs_file.read_text(encoding="utf-8"))
        print(f"Loaded index: {len(self._documents)} documents, dim={self._embeddings.shape[1]}")

    # ──────────────── Query ────────────────

    def query(
        self,
        query_text: str,
        embedder: EmbedderProvider,
        n_results: int = 5,
        filter_pipeline: Optional[str] = None,
        filter_tag: Optional[str] = None,
    ) -> SearchResult:
        """
        Semantic search over the knowledge base.

        Args:
            query_text: Natural language query
            embedder: Embedding provider (same as used for indexing)
            n_results: Number of results to return
            filter_pipeline: Optional pipeline ID to filter by
            filter_tag: Optional tag to filter by

        Returns:
            SearchResult with ranked hits
        """
        import numpy as np
        from sklearn.preprocessing import normalize

        self._ensure_loaded()

        # Generate query embedding and normalize
        query_emb = np.array(embedder.embed([query_text])[0], dtype=np.float32).reshape(1, -1)
        query_emb = normalize(query_emb)

        start = time.time()

        # Cosine similarity (dot product for normalized vectors)
        scores = np.dot(self._embeddings, query_emb.T).flatten()

        latency = (time.time() - start) * 1000

        # Build mask for filters
        mask = np.ones(len(self._documents), dtype=bool)
        if filter_pipeline or filter_tag:
            for i, doc in enumerate(self._documents):
                if filter_pipeline and filter_pipeline not in doc.get("pipeline_ids", []):
                    mask[i] = False
                if filter_tag and filter_tag not in doc.get("tags", []):
                    mask[i] = False

        # Get top-k indices
        # Set filtered-out scores to -inf
        scores_filtered = scores.copy()
        scores_filtered[~mask] = -np.inf

        # Get top-k indices
        if n_results > len(scores_filtered):
            n_results = len(scores_filtered)
        top_indices = np.argsort(scores_filtered)[::-1][:n_results]

        # Build hits
        hits: list[SearchHit] = []
        for idx in top_indices:
            if scores_filtered[idx] == -np.inf:
                continue
            doc = self._documents[idx]
            hits.append(SearchHit(
                chunk_id=doc["chunk_id"],
                content=doc["content"],
                score=round(float(scores[idx]), 4),
                source_file=doc["source_file"],
                section_title=doc["section_title"],
                line_start=doc["line_start"],
                line_end=doc["line_end"],
                pipeline_ids=doc.get("pipeline_ids", []),
                tags=doc.get("tags", []),
            ))

        return SearchResult(
            query=query_text,
            hits=hits,
            total_candidates=len(self._documents),
            latency_ms=round(latency, 2),
        )

    # ──────────────── Info ────────────────

    def stats(self) -> dict:
        """Return vector store statistics (lazy, doesn't require index loaded)."""
        try:
            self._ensure_loaded()
            return {
                "document_count": len(self._documents),
                "embedding_dim": self._embeddings.shape[1] if self._embeddings is not None else 0,
                "persist_dir": str(self.persist_dir),
            }
        except FileNotFoundError:
            return {
                "document_count": 0,
                "embedding_dim": 0,
                "persist_dir": str(self.persist_dir),
                "status": "not_initialized",
            }

    def delete_index(self):
        """Delete all persisted index files."""
        for f in self.persist_dir.glob("*"):
            f.unlink()
        self._embeddings = None
        self._documents = []
        print(f"Index at {self.persist_dir} deleted.")

    def count(self) -> int:
        """Return number of documents in the index."""
        try:
            self._ensure_loaded()
            return len(self._documents)
        except FileNotFoundError:
            return 0


# ──────────────────────────────────────────────────────────────
# Standalone: build index + test query
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    workspace = Path(__file__).parent.parent.parent
    ref_dir = workspace / "references"
    pipe_dir = workspace / "src" / "data" / "pipelines"
    persist = workspace / "python" / "vector_data"

    if len(sys.argv) > 1 and sys.argv[1] == "--build":
        print(f"Building vector index...")
        print(f"  References: {ref_dir}")
        print(f"  Pipelines: {pipe_dir}")
        print(f"  Persist: {persist}")

        embedder = DummyEmbedder(dim=128)
        store = VectorStore(persist_dir=str(persist))
        count = store.build_index(
            str(ref_dir), str(pipe_dir), embedder, force_rebuild=True
        )
        print(f"\nIndex built with {count} documents.")

        # Test queries
        queries = [
            "GWAS 人群分层怎么处理",
            "scRNA-seq 聚类分辨率怎么选",
            "Mutect2 配对肿瘤正常样本过滤",
        ]

        for q in queries:
            print(f"\n{'='*60}")
            print(f"Query: {q}")
            result = store.query(q, embedder, n_results=3)
            print(f"  Total: {result.total_candidates} docs, latency: {result.latency_ms:.2f}ms")
            for i, hit in enumerate(result.hits):
                print(f"  [{i+1}] score={hit.score:.4f} | {hit.section_title}")
                print(f"      {hit.source_file}:{hit.line_start}-{hit.line_end} | tags={hit.tags}")
                preview = hit.content[:120].replace('\n', ' ')
                print(f"      {preview}...")
    else:
        print("Usage: python chroma_client.py --build")
        print("  Builds the vector index from references/ and pipelines/")
