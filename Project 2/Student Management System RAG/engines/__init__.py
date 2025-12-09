"""
Engine implementations for different chatbot strategies.

Engines define HOW the chatbot responds:
- SimpleFAQEngine: Looks up answers in a predefined FAQ dictionary
- RagEngine: Retrieves relevant documents and generates answers

All engines implement the ChatEngine protocol from base.py
"""

from engines.base import ChatEngine

__all__ = ["ChatEngine"]