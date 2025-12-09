"""
RAG Pipeline Module - LangChain LCEL Chain for RAG Q&A
UPDATED: Added multi-factor relevance filtering

This module builds the LangChain chain that:
1. Contextualizes questions using chat history
2. Retrieves relevant PDF chunks from Chroma with similarity filtering
3. Validates relevance using similarity scores + document count + context length
4. Generates answers using GPT-5
5. Formats output with source citations
"""

import os
import sys
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage


class RAGPipeline:
    """
    RAG Pipeline that combines retrieval and generation with relevance filtering.
    
    Workflow:
    1. Contextualize question using chat history
    2. Retrieve relevant chunks from vector store
    3. Validate relevance using multiple criteria:
       - Similarity scores (semantic relevance)
       - Number of relevant documents
       - Context length (quality threshold)
    4. Generate answer with GPT-5 or fall back to general chat
    5. Format with source citations
    """
    
    def __init__(self, retriever):
        """
        Initialize RAG pipeline.
        
        Args:
            retriever: Chroma retriever from ingest.py (retrieves top-k chunks)
                      Can be None for general chat mode (no documents)
        """
        self.retriever = retriever
        self.llm = ChatOpenAI(
            model=CONFIG.model_name,
            temperature=CONFIG.temperature,
            model_kwargs={"max_completion_tokens": CONFIG.max_tokens}
        )
        
        # Relevance filtering thresholds (from config)
        self.similarity_threshold = CONFIG.similarity_threshold
        self.min_relevant_docs = CONFIG.min_relevant_docs
        self.min_context_length = CONFIG.min_context_length
        
        # Build the pipeline chains
        self.contextualize_q_chain = self._build_contextualize_chain()
        
        # Only build RAG chain if we have a retriever
        if self.retriever:
            self.rag_chain = self._build_rag_chain()
        else:
            self.rag_chain = None
        
        self.general_chat_chain = self._build_general_chat_chain()
    
    def _build_contextualize_chain(self):
        """
        Build chain to contextualize questions using chat history.
        
        Handles follow-up questions by rewriting them with context.
        Example: "How does it work?" → "How does RAG work?"
        """
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question which might reference "
            "context in the chat history, formulate a standalone question which can be "
            "understood without the chat history. Do NOT answer the question, just "
            "reformulate it if needed and otherwise return it as is."
        )
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        return contextualize_q_prompt | self.llm | StrOutputParser()
    
    def _is_relevant(self, docs: List, context: str, question: str) -> Tuple[bool, str]:
        """
        Multi-factor relevance check for retrieved documents.
        
        Evaluates:
        1. Number of retrieved documents
        2. Similarity scores (if available)
        3. Context length (quality gate)
        
        Args:
            docs: List of retrieved documents from Chroma
            context: Formatted context string
            question: Original question (for debugging)
            
        Returns:
            Tuple of (is_relevant: bool, reason: str)
        """
        # Check 1: Do we have any documents?
        if not docs or len(docs) == 0:
            return False, "No documents retrieved"
        
        # Check 2: Similarity scores
        relevant_docs = 0
        total_score = 0
        
        for doc in docs:
            # Try to get similarity score from metadata or doc
            # LangChain's retriever doesn't always return scores directly
            # If using similarity_search_with_scores, scores would be in metadata
            similarity_score = getattr(doc, 'metadata', {}).get('similarity_score', None)
            
            if similarity_score is not None:
                total_score += similarity_score
                if similarity_score >= self.similarity_threshold:
                    relevant_docs += 1
            else:
                # If no score available, count document as potentially relevant
                relevant_docs += 1
        
        # Calculate average similarity (if we have scores)
        avg_similarity = (total_score / len(docs)) if total_score > 0 else None
        
        if avg_similarity is not None:
            if avg_similarity < self.similarity_threshold:
                return False, f"Low relevance score ({avg_similarity:.2f} < {self.similarity_threshold})"
        
        # Check 3: Do we have enough relevant documents?
        if relevant_docs < self.min_relevant_docs:
            return False, f"Too few relevant documents ({relevant_docs} < {self.min_relevant_docs})"
        
        # Check 4: Context length (quality gate)
        context_length = len(context.strip())
        if context_length < self.min_context_length:
            return False, f"Insufficient context ({context_length} < {self.min_context_length} chars)"
        
        score_str = f"{avg_similarity:.2f}" if avg_similarity is not None else "N/A"
        return True, f"Relevant (score: {score_str}, docs: {relevant_docs}, length: {context_length})"
    
    def _build_rag_chain(self):
        """
        Build the main RAG chain: retrieve -> validate -> generate -> format with sources.
        """
        # System prompt for RAG
        rag_system_prompt = (
            "You are Lilo, a helpful and knowledgeable AI assistant. "
            "Answer questions based on the provided document context when relevant. IF THEY ARE RELEVANT. "
            "If the question is unrelated to the documents, avoid using the documents. "
            "But don't be restricted by the documents - use your general knowledge freely too. "
            "Be confident, direct, and helpful. Answer the user's question as best you can."
            "Context:\n{context}"
        )
        
        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", rag_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        # Simple function to format docs
        def format_docs(docs):
            if not docs:
                return "No documents found"
            text = ""
            for doc in docs:
                text += str(doc.page_content) + "\n\n"
            return text

        # Build RAG chain with relevance checking
        def rag_invoke(inputs):
            question = inputs["question"]
            
            # Step 1: Retrieve documents
            context_docs = self.retriever.invoke(question)
            context = format_docs(context_docs)
            
            # Step 2: Validate relevance
            is_relevant, reason = self._is_relevant(context_docs, context, question)
            print(f"Relevance check: {reason}")
            
            if not is_relevant:
                print(f"Low relevance detected - falling back to general chat")
                return None  # Signal to use general chat
            
            # Step 3: Generate answer with relevant context
            prompt_value = rag_prompt.invoke({
                "context": context,
                "question": question,
                "chat_history": inputs.get("chat_history", [])
            })
            
            response = self.llm.invoke(prompt_value)
            return response.content
        
        return RunnableLambda(rag_invoke)
    
    def _build_general_chat_chain(self):
        """
        Build a general chat chain for when no documents are uploaded or not relevant.
        Uses GPT-5 directly without retrieval.
        """
        general_system_prompt = (
            "You are Lilo, a helpful and friendly AI assistant. "
            "Answer questions directly and confidently. "
            "Be conversational, clear, and helpful. "
            "Don't overthink it - just answer what the user asks."
            "If you don't know something, say so honestly but try to be useful anyway."
        )
        
        general_prompt = ChatPromptTemplate.from_messages([
            ("system", general_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        general_chain = (
            general_prompt
            | self.llm
            | StrOutputParser()
        )
        
        return general_chain
    
    def _extract_sources(self, docs: List) -> str:
        """
        Extract source citations from retrieved documents.
        
        Args:
            docs: List of Document objects from retriever
            
        Returns:
            Formatted source string like "document.pdf (page 5), document.pdf (page 8)"
        """
        sources = set()
        for doc in docs:
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'Unknown')
            sources.add(f"{source} (page {page})")
        
        return ", ".join(sorted(sources))
    
    def answer_question(
        self,
        question: str,
        chat_history: List[Tuple[str, str]]
    ) -> str:
        """
        Answer a question using RAG pipeline or general chat.
        
        Args:
            question: The user's question
            chat_history: List of (role, message) tuples from RagEngine
            
        Returns:
            Formatted answer with sources (if documents are relevant) or general response
        """
        # If no retriever/rag_chain, use general chat
        if not self.retriever or not self.rag_chain:
            messages = []
            for role, content in chat_history:
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
            
            return self.general_chat_chain.invoke({
                "question": question,
                "chat_history": messages
            })
        
        # Convert chat history to LangChain format
        messages = []
        for role, content in chat_history:
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        
        # Try to retrieve and answer with RAG
        try:
            retrieved_docs = self.retriever.invoke(question)
            
            if retrieved_docs and len(retrieved_docs) > 0:
                # We have documents - try RAG chain
                final_question = question
                
                print(f"Question to RAG: {final_question}")
                print(f"Retrieved {len(retrieved_docs)} documents")
                
                answer = self.rag_chain.invoke({
                    "question": final_question,
                    "chat_history": messages
                })

                # If RAG returned None (low relevance), use general chat instead
                if answer is None:
                    print("RAG deemed documents not relevant - using general chat")
                    return self.general_chat_chain.invoke({
                        "question": question,
                        "chat_history": messages
                    })
                
                # We have a valid answer - add sources
                sources = self._extract_sources(retrieved_docs)
                
                if sources:
                    final_answer = f"{answer}\n\n📄 **Sources:** {sources}"
                else:
                    final_answer = answer
                
                return final_answer
            else:
                # No documents retrieved - use general chat
                print("No documents retrieved - using general chat")
                return self.general_chat_chain.invoke({
                    "question": question,
                    "chat_history": messages
                })
        except Exception as e:
            # If retrieval fails, fall back to general chat
            print(f"Retrieval failed, using general chat: {e}")
            return self.general_chat_chain.invoke({
                "question": question,
                "chat_history": messages
            })


def build_rag_pipeline(retriever):
    """
    Factory function to build RAG pipeline.
    
    Args:
        retriever: Chroma retriever from ingest.py
        
    Returns:
        RAGPipeline instance
    """
    return RAGPipeline(retriever)