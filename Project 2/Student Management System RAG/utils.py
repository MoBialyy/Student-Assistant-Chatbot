"""
Utility functions for environment setup and initialization.
"""

import os
from dotenv import load_dotenv


def setup_environment():
    """
    Load environment variables from .env file.
    
    This should be called at the start of app.py
    
    Usage:
        from utils import setup_environment
        setup_environment()
    """
    load_dotenv()  # Load all variables from .env file
    
    # Make OpenAI API key available to LangChain
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    else:
        raise ValueError(
            "⚠️ OPENAI_API_KEY not found in .env file!\n"
            "Please create a .env file with:\n"
            "  OPENAI_API_KEY=your_key_here"
        )
    
    print("✅ Environment variables loaded successfully")


if __name__ == "__main__":
    setup_environment()
    print(f"API Key set: {bool(os.getenv('OPENAI_API_KEY'))}")