from typing import Protocol, List, Tuple


class ChatEngine(Protocol):
    """
    Protocol (interface) that all chat engines must implement.
    This allows us to swap engines without changing the UI.
    
    Both SimpleFAQEngine and RagEngine must implement these methods.
    """
    
    def answer(self, session_id: str, question: str) -> str:
        """
        Answer a question in the context of a session.
        
        Args:
            session_id: Unique identifier for the conversation session
            question: The user's question/input
            
        Returns:
            The chatbot's response as a string
        """
        ...
    
    def get_history(self, session_id: str) -> List[Tuple[str, str]]:
        """
        Retrieve chat history for a session.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            List of tuples: [("user", "question"), ("assistant", "answer"), ...]
        """
        ...
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear chat history for a session (optional but useful).
        
        Args:
            session_id: Unique identifier for the conversation session
        """
        ...