"""
Chatbot Facade - Simple interface that delegates to a chat engine.

This is the stable interface that the UI talks to.
The actual logic is handled by different engines:
- SimpleFAQEngine: Student management (Project 1 logic)
- RagEngine: PDF-based RAG system (Project 2 new feature)
"""

from typing import List, Tuple


class Chatbot:
    """
    Facade that delegates to different chat engines.
    
    The UI never needs to know about engines - it just uses this class.
    """
    
    def __init__(self, engine):
        """
        Initialize Chatbot with a specific engine.
        
        Args:
            engine: Any object implementing the ChatEngine protocol
                   (has answer() and get_history() methods)
        """
        self.engine = engine
        print("🤖 Chatbot ready! Type 'help' to see available commands.\n")
    
    def ask(self, session_id: str, question: str) -> str:
        """
        Ask the chatbot a question.
        
        Args:
            session_id: Unique identifier for this conversation session
            question: The user's question or command
            
        Returns:
            The chatbot's response as a string
        """
        return self.engine.answer(session_id, question)
    
    def get_history(self, session_id: str) -> List[Tuple[str, str]]:
        """
        Get chat history for a session.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            List of (role, message) tuples: [("user", "q"), ("assistant", "a"), ...]
        """
        return self.engine.get_history(session_id)
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear chat history for a session.
        
        Args:
            session_id: Unique identifier for the conversation session
        """
        if hasattr(self.engine, 'clear_session'):
            self.engine.clear_session(session_id)