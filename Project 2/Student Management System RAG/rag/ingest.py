"""
RAG Ingest Module - PDF Upload, Chunking, Embedding, and Storage

This module handles:
1. PDF file validation
2. PDF text extraction
3. Text chunking
4. Embedding generation (via OpenAI)
5. Storage in Chroma vector database (per-session)
"""

import os
import sys
import time
import tempfile
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from chromadb import PersistentClient


class PDFIngestor:
    """
    Handles PDF ingestion for RAG system.
    
    Features:
    - Text extraction from PDFs
    - Intelligent chunking with overlap
    - Embedding generation via OpenAI
    - Storage in Chroma vector database
    
    Each session has its own isolated Chroma collection.
    """
    
    def __init__(self):
        """Initialize the ingestor with config settings."""
        self.chunk_size = CONFIG.chunk_size
        self.chunk_overlap = CONFIG.chunk_overlap
        self.max_file_size_mb = CONFIG.max_file_size_mb
        self.allowed_file_types = CONFIG.allowed_file_types
        self.persist_directory = CONFIG.persist_directory
        
        # Initialize embeddings (uses OPENAI_API_KEY from environment)
        self.embeddings = OpenAIEmbeddings(
            model=CONFIG.embedding_model,
            dimensions=CONFIG.embedding_dimensions
        )
        
        # Initialize Chroma client
        self.chroma_client = PersistentClient(
            path=self.persist_directory
        )
    
    def ingest_pdfs(self, pdf_files: List, session_id: str) -> Dict:
        """
        Ingest PDF files and store embeddings in Chroma.
        
        Returns the collection name for retriever to use.
        """
        try:
            # Validate files
            validation_result = self._validate_files(pdf_files)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "chunks_created": 0,
                    "files_processed": 0,
                    "message": "",
                    "error": validation_result["error"],
                    "collection_name": None
                }
            
            # Use existing collection for this session (don't create new ones)
            collection_name = f"session_{session_id}"
            
            # Get or create collection - will reuse existing if it exists
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Using collection: {collection_name}")
            
            total_chunks = 0
            files_processed = 0
            
            # Process each PDF
            for pdf_file in pdf_files:
                try:
                    # Process text from PDF
                    text_chunks = self._process_pdf_text(pdf_file, files_processed)
                    
                    if text_chunks:
                        # Add chunks to Chroma collection
                        self._add_chunks_to_chroma(collection, text_chunks)
                        total_chunks += len(text_chunks)
                        files_processed += 1
                        
                        print(f"  {pdf_file.name}: {len(text_chunks)} text chunks")
                    
                except Exception as e:
                    error_msg = f"Error processing {pdf_file.name}: {str(e)}"
                    print(f"ERROR: {error_msg}")
                    return {
                        "success": False,
                        "chunks_created": 0,
                        "files_processed": 0,
                        "message": "",
                        "error": error_msg,
                        "collection_name": None
                    }
            
            message = f"✅ Processed {files_processed} file(s) → {total_chunks} chunks created"
            
            return {
                "success": True,
                "chunks_created": total_chunks,
                "files_processed": files_processed,
                "message": message,
                "collection_name": collection_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "chunks_created": 0,
                "files_processed": 0,
                "message": "",
                "error": f"Ingestion failed: {str(e)}",
                "collection_name": None
            }
    
    def _validate_files(self, pdf_files: List) -> Dict:
        """
        Validate uploaded PDF files.
        
        Checks:
        - File exists and not empty
        - File type is .pdf
        - File size is within limit
        - Number of files is within limit
        
        Args:
            pdf_files: List of uploaded files
            
        Returns:
            Dict with 'valid' (bool) and 'error' (str) keys
        """
        if not pdf_files:
            return {
                "valid": False,
                "error": "No files uploaded."
            }
        
        if len(pdf_files) > CONFIG.max_pdf_count:
            return {
                "valid": False,
                "error": f"Too many files. Max {CONFIG.max_pdf_count} PDFs allowed."
            }
        
        for pdf_file in pdf_files:
            # Check file type
            if not pdf_file.name.lower().endswith('.pdf'):
                return {
                    "valid": False,
                    "error": f"Invalid file type: {pdf_file.name}. Only .pdf files allowed."
                }
            
            # Check file size
            file_size_mb = len(pdf_file.getvalue()) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return {
                    "valid": False,
                    "error": f"File too large: {pdf_file.name} ({file_size_mb:.2f}MB). Max {self.max_file_size_mb}MB allowed."
                }
        
        return {"valid": True}
    
    def _process_pdf_text(self, pdf_file, file_index: int) -> List[Dict]:
        """
        Process a single PDF file: extract text and create chunks.
        
        Args:
            pdf_file: Streamlit uploaded file object
            file_index: Index of this file (for tracking)
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Load PDF
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
            
            if not documents:
                return []
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", " ", ""]
            )
            
            chunks = []
            for doc in documents:
                # doc.metadata contains 'source' and 'page' from PyPDFLoader
                page_number = doc.metadata.get('page', 0)
                
                split_texts = text_splitter.split_text(doc.page_content)
                
                for chunk_text in split_texts:
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "source": pdf_file.name,
                            "page": page_number
                        }
                    })
            
            return chunks
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def _add_chunks_to_chroma(self, collection, chunks: List[Dict]) -> None:
        """
        Add chunks to Chroma collection with embeddings.
        
        Args:
            collection: Chroma collection object
            chunks: List of chunk dicts with 'text' and 'metadata'
        """
        # Prepare data for Chroma
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [f"{chunk['metadata']['source']}_{i}" for i, chunk in enumerate(chunks)]
        
        # Add to collection (Chroma will embed automatically)
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
    
    def delete_session_collection(self, session_id: str) -> bool:
        """
        Delete a session's Chroma collection (cleanup on logout).
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            collections = self.chroma_client.list_collections()
            for collection in collections:
                if collection.name.startswith(f"session_{session_id}"):
                    self.chroma_client.delete_collection(name=collection.name)
            
            return True
        except Exception as e:
            print(f"Error deleting collection {session_id}: {e}")
            return False
    
    def get_session_retriever(self, session_id: str, collection_name: str):
        """
        Get a retriever for a specific session's collection.
        
        This is used by the RAG pipeline to retrieve relevant chunks.
        
        Args:
            session_id: Session identifier
            collection_name: The collection name (includes timestamp)
            
        Returns:
            Chroma retriever object (or None if collection doesn't exist)
        """
        try:
            from langchain_community.vectorstores import Chroma
            
            # Get the collection using the provided name
            vector_store = Chroma(
                client=self.chroma_client,
                collection_name=collection_name,
                embedding_function=self.embeddings
            )
            
            # Return as retriever (similarity search)
            return vector_store.as_retriever(
                search_kwargs={"k": CONFIG.retrieval_k}
            )
        except Exception as e:
            print(f"Error getting retriever for session {session_id}: {e}")
            return None


# Singleton instance
ingestor = PDFIngestor()