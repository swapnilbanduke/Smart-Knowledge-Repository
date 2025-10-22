"""
Chat Service
Manages conversational AI interactions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db_path: str = "data/leadership.db"):
        self.db_path = db_path
        self.conversation_history = []
    
    def process_message(self, message: str, department: Optional[str] = None) -> str:
        from vector_db import generate_ai_answer, vector_search_profiles
        try:
            profiles = vector_search_profiles(message, limit=5, db_path=self.db_path)
            if department and profiles:
                profiles = [p for p in profiles if p.get('department') == department]
            if not profiles:
                response = "I couldn't find any team members matching your query."
            else:
                response = generate_ai_answer(message, profiles)
            self.add_message("assistant", response)
            return response
        except Exception as e:
            logger.error(f"Error: {e}")
            return "I encountered an error. Please try again."
    
    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
    
    def get_history(self) -> List[Dict]:
        return self.conversation_history
    
    def clear_history(self):
        self.conversation_history = []
