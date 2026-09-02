# -*- coding: utf-8 -*-
"""一键重建「真语义」向量索引并验证检索。

用法 (仓库根目录):
    python python/vector_store/build_semantic_index.py --build    # 全量重建
    python python/vector_store/build_semantic_index.py            # 重建后跑验证查询

依赖:
    pip install fastembed numpy scikit-learn
模型: BAAI/bge-small-zh-v1.5 (512 维, 首次自动经 hf-mirror 下载到 python/.hf_cache)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vector_store.chroma_client import VectorStore          # noqa: E402
from vector_store.fastembed_provider import FastEmbedProvider  # noqa: E402
from vector_store.semantic_search import SemanticSearcher   # noqa: E402

REPO = Path(__file__).parent.parent.parent
REF_DIR = REPO / "references"
PIPE_DIR = REPO / "src" / "data" / "pipelines"
PERSIST = Path(__file__).parent.parent / "vector_data"


def main() -> None:
    build = len(sys.argv) > 1 and sys.argv[1] == "--build"
    embedder = FastEmbedProvider()

    if build:
        store = VectorStore(persist_dir=str(PERSIST))
        n = store.build_index(str(REF_DIR), str(PIPE_DIR), embedder, force_rebuild=True)
        dim = store.stats()["embedding_dim"]
        print(f"\n[BUILD] 全量语义索引: {n} chunks, dim={dim}")
    else:
        searcher = SemanticSearcher(embedder=embedder)
        queries = [
            "GWAS 人群分层怎么处理",
            "scRNA-seq 聚类分辨率怎么选",
            "Mutect2 配对肿瘤正常样本过滤",
            "孟德尔随机化工具变量选择",
            "家系 WGS 怎么找新发变异",
        ]
        for q in queries:
            print(f"\n{'=' * 70}\nQ: {q}")
            for i, h in enumerate(searcher.search(q, n_results=5).hits):
                print(f"  [{i + 1}] {h.score:.4f} | {h.section_title} | {h.source_file}:L{h.line_start}")


if __name__ == "__main__":
    main()
