"""FlowSeq Vector Store module.

Semantic search over the bioinformatics knowledge base.
Chunking → Embedding → ChromaDB → Semantic Retrieval.

Usage:
    from vector_store.semantic_search import SemanticSearcher
    searcher = SemanticSearcher()
    results = searcher.search("GWAS 质量控制标准")
"""
