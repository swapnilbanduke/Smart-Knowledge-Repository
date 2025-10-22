"""
Scraping Service
Handles web scraping operations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import logging
from typing import Dict, Optional, Callable

logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self, db_path: str = "data/leadership.db"):
        self.db_path = db_path
    
    def scrape_and_save(self, website_url: str, deep_scrape: bool = True, replace_existing: bool = False, progress_callback: Optional[Callable] = None) -> Dict:
        from enhanced_scraper import scrape_with_discovery
        from database import insert_profiles, clear_database, get_departments
        from vector_db import update_vector_database
        try:
            logger.info(f"Starting scrape of {website_url}")
            if replace_existing:
                clear_database(db_path=self.db_path)
            profiles = scrape_with_discovery(website_url, deep_scrape=deep_scrape, progress_callback=progress_callback)
            if not profiles:
                return {"success": False, "error": "No profiles found"}
            insert_profiles(profiles, db_path=self.db_path)
            update_vector_database(db_path=self.db_path)
            departments = get_departments(db_path=self.db_path)
            return {"success": True, "profiles_count": len(profiles), "departments": departments}
        except Exception as e:
            logger.error(f"Error: {e}")
            return {"success": False, "error": str(e)}
    
    def refresh_data(self, website_url: str) -> Dict:
        return self.scrape_and_save(website_url, deep_scrape=True, replace_existing=True)
    
    def refresh_embeddings(self) -> Dict:
        try:
            from vector_db import update_vector_database
            from database import get_profile_count
            update_vector_database(db_path=self.db_path)
            count = get_profile_count(db_path=self.db_path)
            return {"success": True, "count": count}
        except Exception as e:
            return {"success": False, "error": str(e)}
