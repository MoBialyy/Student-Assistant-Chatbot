from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Config:
    """
    Centralized configuration for Project 2.
    Easy to switch providers, models, and parameters.
    
    All tunables in one place - update here to affect the entire app.
    """
    
    # --- RAG Chunking Settings ---
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # --- Retrieval Settings ---
    retrieval_k: int = 8
    retrieval_strategy: str = "similarity"  
    
    # --- Relevance Filtering Thresholds ---
    # Used by RAGPipeline to determine if retrieved docs are actually relevant
    similarity_threshold: float = 0.65  # Minimum similarity score (0-1 scale)
    min_relevant_docs: int = 1  # Minimum number of documents that must meet similarity threshold
    min_context_length: int = 200  # Minimum characters of context to use documents (quality gate)
    
    # --- Embedding Settings ---
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 384
    
    # --- LLM Settings ---
    llm_provider: str = "openai" 
    model_name: str = "gpt-5"
    temperature: float = 1  # Fixed: was 1 (too high)
    max_tokens: int = 2048
    
    # --- Vector Store Settings ---
    persist_directory: str = ".chroma_v7/student-rag"  # Fixed: was .chroma_v3
    
    # --- File Upload Settings ---
    max_file_size_mb: int = 50
    max_pdf_count: int = 10
    allowed_file_types: List[str] = None
    
    def __post_init__(self):
        """Set defaults after initialization"""
        if self.allowed_file_types is None:
            self.allowed_file_types = [".pdf"]
    
    def __str__(self):
        """Pretty print configuration"""
        return (
            f"Config(\n"
            f"  Chunking: size={self.chunk_size}, overlap={self.chunk_overlap}\n"
            f"  Retrieval: k={self.retrieval_k}, strategy={self.retrieval_strategy}\n"
            f"  Relevance Filtering:\n"
            f"    - similarity_threshold={self.similarity_threshold}\n"
            f"    - min_relevant_docs={self.min_relevant_docs}\n"
            f"    - min_context_length={self.min_context_length}\n"
            f"  Embedding: {self.embedding_model}\n"
            f"  LLM: {self.llm_provider}/{self.model_name}, temp={self.temperature}\n"
            f"  Vector Store: {self.persist_directory}\n"
            f"  Max file size: {self.max_file_size_mb}MB, Max PDFs: {self.max_pdf_count}\n"
            f")"
        )


# Global config instance - import this everywhere
CONFIG = Config()