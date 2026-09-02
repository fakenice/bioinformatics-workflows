# -*- coding: utf-8 -*-
"""
FastEmbed 本地语义 Embedder (BAAI/bge-small-zh-v1.5, ONNX 推理)

接入 vector_store 的 EmbedderProvider 协议，让语义检索真正具备语义：

    from vector_store.fastembed_provider import FastEmbedProvider
    embedder = FastEmbedProvider()
    store.build_index(ref_dir, pipe_dir, embedder)   # 建索引
    searcher = SemanticSearcher(embedder=embedder)   # 检索

关键踩坑:
- fastembed 默认从 huggingface.co 下载, 走了 xet CAS 协议(cas-server.xethub.hf.co)
  国内网络会 401; 必须设 HF_ENDPOINT=https://hf-mirror.com 且 HF_HUB_DISABLE_XET=1
  强制降级普通 HTTP + 走镜像, 否则模型文件拉不下来。
- 模型下载一次后缓存于 python/.hf_cache, 之后离线可用。
- BAAI/bge-small-zh-v1.5: 512 维, 中文检索, 约 90MB, CPU 秒级编码。
  如需更强多语可换 BAAI/bge-m3 (非 fastembed 内置, 需 sentence-transformers 路线)。
"""
import os
from pathlib import Path

# 必须在 import fastembed 之前生效
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from typing import Optional  # noqa: E402

from vector_store.embedder import EmbedderProvider  # noqa: E402

_DEFAULT_CACHE = Path(__file__).parent.parent / ".hf_cache"


class FastEmbedProvider(EmbedderProvider):
    """embed(texts) -> list[list[float]]，纯本地 ONNX 推理，无需 API key。"""

    def __init__(
        self,
        model: str = "BAAI/bge-small-zh-v1.5",
        cache_dir: Optional[str] = None,
    ):
        from fastembed import TextEmbedding

        self.model = model
        self._te = TextEmbedding(
            model_name=model,
            cache_dir=cache_dir or str(_DEFAULT_CACHE),
            threads=0,  # 0 = auto, ONNX 自动用多核
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        vecs = self._te.embed(texts, batch_size=16)
        return [v.tolist() for v in vecs]


if __name__ == "__main__":
    # 自检: 三句中英文编码
    p = FastEmbedProvider()
    for v in p.embed(["GWAS 人群分层怎么处理", "单细胞聚类", "somatic filtering"]):
        assert len(v) == 512
    print("FastEmbedProvider OK (dim=512)")
