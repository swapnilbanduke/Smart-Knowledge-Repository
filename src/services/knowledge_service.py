"""
Knowledge Service
Business logic for knowledge queries
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class KnowledgeService:
    def __init__(self, db_path: str = "data/leadership.db"):
        self.db_path = db_path
    
    def search(self, query: str, use_vector_search: bool = True, department: Optional[str] = None, limit: int = 5) -> List[Dict]:
        from vector_db import vector_search_profiles
        from database import search_profiles
        if use_vector_search:
            results = vector_search_profiles(query, limit=limit, db_path=self.db_path)
            if department:
                results = [r for r in results if r.get('department') == department]
            return results[:limit]
        else:
            return search_profiles(query, department=department, db_path=self.db_path)
    
    def get_all(self, department: Optional[str] = None) -> List[Dict]:
        from database import get_all_profiles, get_profiles_by_department
        if department:
            return get_profiles_by_department(department, db_path=self.db_path)
        else:
            return get_all_profiles(db_path=self.db_path)
    
    def answer_question(self, query: str, department: Optional[str] = None) -> str:
        from vector_db import generate_ai_answer
        profiles = self.search(query, use_vector_search=True, department=department)
        if not profiles:
            return "I couldn't find any team members matching your query."
        return generate_ai_answer(query, profiles)
    
    def get_departments(self) -> List[str]:
        from database import get_departments
        return get_departments(db_path=self.db_path)
    
    def get_profile_count(self, department: Optional[str] = None) -> int:
        from database import get_profile_count
        if department:
            return len(self.get_all(department=department))
        else:
            return get_profile_count(db_path=self.db_path)
    
    def clear_database(self) -> Dict:
        try:
            from database import clear_database
            clear_database(db_path=self.db_path)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
