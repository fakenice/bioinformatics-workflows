"""
Embedding generator for FlowSeq document chunks.

Supports OpenAI-compatible embedding APIs. Designed to be modular —
swap the model or provider without touching the chunker or retriever.

Default: OpenAI text-embedding-3-small (1536 dim)
Also compatible with: any OpenAI-compatible endpoint (local Ollama, vLLM, etc.)
"""

import os
from dataclasses import dataclass
from typing import Optional, Protocol

from vector_store.chunker import Chunk


# ──────────────────────────────────────────────────────────────
# Embedding provider protocol (swap implementations easily)
# ──────────────────────────────────────────────────────────────


class EmbedderProvider(Protocol):
    """Protocol for embedding providers."""
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


@dataclass
class EmbeddingResult:
    """A chunk with its embedding vector."""
    chunk: Chunk
    embedding: list[float]


# ──────────────────────────────────────────────────────────────
# OpenAI embedder
# ──────────────────────────────────────────────────────────────


class OpenAIEmbedder:
    """
    Embedding provider using OpenAI-compatible API.

    Config via environment variables:
    - OPENAI_API_KEY (required)
    - OPENAI_BASE_URL (optional, for proxies/alternatives)
    - EMBEDDING_MODEL (default: text-embedding-3-small)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        batch_size: int = 20,
    ):
        self.model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.batch_size = batch_size

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts using OpenAI API."""
        import openai

        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            response = client.embeddings.create(
                model=self.model,
                input=batch,
            )
            for item in response.data:
                all_embeddings.append(item.embedding)

        return all_embeddings


# ──────────────────────────────────────────────────────────────
# Dummy embedder (for testing without API key)
# ──────────────────────────────────────────────────────────────


class DummyEmbedder:
    """
    Generates deterministic pseudo-embeddings from text hash.
    Used for testing chunking and retrieval logic without API calls.
    NOT for production — embeddings have no semantic meaning.
    """

    def __init__(self, dim: int = 128):
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        import hashlib

        embeddings: list[list[float]] = []
        for text in texts:
            # Deterministic pseudo-embedding from SHA-256
            h = hashlib.sha256(text.encode("utf-8")).digest()
            vec: list[float] = []
            for j in range(self.dim):
                byte_val = h[j % len(h)]
                vec.append((byte_val / 255.0) * 2 - 1)  # [-1, 1]
            embeddings.append(vec)
        return embeddings


# ──────────────────────────────────────────────────────────────
# Utility: embed a list of chunks
# ──────────────────────────────────────────────────────────────


def embed_chunks(
    chunks: list[Chunk],
    embedder: EmbedderProvider,
) -> list[EmbeddingResult]:
    """
    Embed all chunks using the given provider.

    Returns a list of EmbeddingResult with chunk + embedding.
    """
    texts = [c.content for c in chunks]
    embeddings = embedder.embed(texts)

    return [
        EmbeddingResult(chunk=chunk, embedding=emb)
        for chunk, emb in zip(chunks, embeddings)
    ]


# ──────────────────────────────────────────────────────────────
# Standalone test
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from chunker import chunk_all_references
    from pathlib import Path

    workspace = Path(__file__).parent.parent.parent
    ref_dir = workspace / "references"

    print("Testing with DummyEmbedder...")
    results = chunk_all_references(str(ref_dir))
    all_chunks = [c for r in results for c in r.chunks]

    embedder = DummyEmbedder(dim=128)
    embedded = embed_chunks(all_chunks, embedder)

    print(f"Embedded {len(embedded)} chunks")
    if embedded:
        print(f"Embedding dimension: {len(embedded[0].embedding)}")
        print(f"Sample chunk: {embedded[0].chunk.chunk_id}")
