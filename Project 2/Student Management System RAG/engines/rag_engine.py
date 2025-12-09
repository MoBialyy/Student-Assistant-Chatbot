"""
RAG Engine - Implements ChatEngine protocol for RAG-based Q&A

This engine handles PDF-based question answering using:
- Document retrieval from Chroma vector store
- LangChain RAG pipeline with GPT-5
- Per-session document isolation
- Chat history management
"""

import os
import sys
from typing import List, Tuple, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.ingest import PDFIngestor
from rag.pipeline import build_rag_pipeline
from config import CONFIG


class RagEngine:
    """
    RAG-powered chat engine that answers questions about uploaded PDFs.
    
    Implements the ChatEngine protocol:
    - answer(session_id, question) -> str
    - get_history(session_id) -> List[Tuple[str, str]]
    - clear_session(session_id) -> None
    
    Also adds RAG-specific methods:
    - ingest_pdfs(session_id, pdf_files) -> dict
    - delete_session(session_id) -> bool
    """
    
    def __init__(self):
        """Initialize RAG engine with ingestor and pipeline components."""
        self.ingestor = PDFIngestor()
        
        # Store pipelines per session (created when PDFs are ingested)
        self.pipelines: Dict[str, object] = {}
        
        # Store collection names per session (needed for retriever)
        self.collection_names: Dict[str, str] = {}
        
        # Store chat history per session
        self.histories: Dict[str, List[Tuple[str, str]]] = {}
    
    def answer(self, session_id: str, question: str) -> str:
        """
        Answer a question using RAG pipeline.
        
        Implements ChatEngine.answer() protocol.
        
        Args:
            session_id: Unique identifier for this conversation session
            question: The user's question
            
        Returns:
            Answer grounded in uploaded PDFs with source citations (if available)
            or general response if no documents uploaded
        """
        try:
            # Check if PDFs have been ingested for this session
            if session_id not in self.pipelines:
                # No documents yet - create empty pipeline for general chat
                collection_name = self.collection_names.get(session_id)
                if collection_name:
                    retriever = self.ingestor.get_session_retriever(session_id, collection_name)
                else:
                    retriever = None
                if retriever is None:
                    # Create empty session with no documents
                    pipeline = build_rag_pipeline(None)
                else:
                    pipeline = build_rag_pipeline(retriever)
                self.pipelines[session_id] = pipeline
                self.histories[session_id] = []
            
            # Get pipeline for this session
            pipeline = self.pipelines[session_id]
            
            # Get chat history for this session
            chat_history = self.histories.get(session_id, [])
            
            # Generate answer using RAG pipeline (or general chat if no docs)
            answer = pipeline.answer_question(question, chat_history)
            
            # Store in history
            self.histories.setdefault(session_id, [])
            self.histories[session_id].append(("user", question))
            self.histories[session_id].append(("assistant", answer))
            
            return answer
            
        except Exception as e:
            error_msg = f"⚠️ Error generating answer: {str(e)}"
            print(f"RAG Engine Error: {e}")
            return error_msg
    
    def get_history(self, session_id: str) -> List[Tuple[str, str]]:
        """
        Get chat history for a session.
        
        Implements ChatEngine.get_history() protocol.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            List of (role, message) tuples: [("user", "q"), ("assistant", "a"), ...]
        """
        return self.histories.get(session_id, [])
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear chat history for a session (but keep documents).
        
        Implements ChatEngine.clear_session() protocol.
        
        Args:
            session_id: Unique identifier for the conversation session
        """
        if session_id in self.histories:
            del self.histories[session_id]
    
    def ingest_pdfs(self, session_id: str, pdf_files: List) -> Dict:
        """
        Ingest PDF files and create RAG pipeline for this session.
        """
        try:
            # Ingest PDFs into Chroma (returns collection_name)
            ingest_result = self.ingestor.ingest_pdfs(pdf_files, session_id)
            
            if not ingest_result["success"]:
                return ingest_result
            
            # Get the collection name that was created
            collection_name = ingest_result.get("collection_name")
            if not collection_name:
                return {
                    "success": False,
                    "chunks_created": 0,
                    "files_processed": 0,
                    "message": "",
                    "error": "Failed to get collection name from ingest."
                }
            
            self.collection_names[session_id] = collection_name
            
            # Create retriever for this session
            retriever = self.ingestor.get_session_retriever(session_id, collection_name)
            
            if retriever is None:
                return {
                    "success": False,
                    "chunks_created": 0,
                    "files_processed": 0,
                    "message": "",
                    "error": "Failed to create retriever for session."
                }
            
            # Build RAG pipeline for this session
            pipeline = build_rag_pipeline(retriever)
            self.pipelines[session_id] = pipeline
            
            # Initialize empty history for this session
            self.histories[session_id] = []
            
            return ingest_result
            
        except Exception as e:
            error_msg = f"Error during PDF ingestion: {str(e)}"
            print(f"RAG Engine Ingest Error: {e}")
            return {
                "success": False,
                "chunks_created": 0,
                "files_processed": 0,
                "message": "",
                "error": error_msg
            }
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete all data for a session (cleanup on logout).
        
        Deletes:
        - Chat history
        - RAG pipeline
        - Chroma collection from vector store
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Remove pipeline
            if session_id in self.pipelines:
                del self.pipelines[session_id]
            
            # Remove history
            if session_id in self.histories:
                del self.histories[session_id]
            
            # Delete Chroma collection
            deleted = self.ingestor.delete_session_collection(session_id)
            
            return deleted
            
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def session_has_documents(self, session_id: str) -> bool:
        """
        Check if a session has documents ingested.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if documents are ingested, False otherwise
        """
        return session_id in self.pipelines