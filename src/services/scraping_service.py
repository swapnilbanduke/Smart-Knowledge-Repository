"""
Intelligent Scraping Service
Uses advanced profile discovery, extraction, and deduplication
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import logging
from typing import Dict, Optional, Callable, List
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self, db_path: str = "data/leadership.db"):
        self.db_path = db_path
        self.stats = {
            'profiles_discovered': 0,
            'profiles_extracted': 0,
            'duplicates_removed': 0,
            'emails_found': 0,
            'photos_found': 0
        }
    
    def scrape_and_save(self, website_url: str, deep_scrape: bool = True, replace_existing: bool = False, progress_callback: Optional[Callable] = None) -> Dict:
        """Intelligent scraping with discovery, extraction, and deduplication."""
        from database import insert_profiles, clear_database, get_departments
        from vector_db import update_vector_database
        from src.scrapers.profile_discovery import ProfileDiscovery
        from src.scrapers.intelligent_extractor import ProfileExtractor
        from src.scrapers.deduplicator import ProfileDeduplicator
        
        try:
            logger.info(f"🚀 Starting intelligent scrape of {website_url}")
            
            if replace_existing:
                clear_database(db_path=self.db_path)
            
            # Step 1: Discover team page
            if progress_callback:
                progress_callback(1, 5, "🔍 Discovering team page...")
            
            discovery = ProfileDiscovery()
            team_page = discovery.discover_team_page(website_url)
            
            if not team_page:
                logger.warning("Using base URL as team page")
                team_page = website_url
            
            # Step 2: Discover profile links
            if progress_callback:
                progress_callback(2, 5, "📋 Finding profile links...")
            
            profile_links = discovery.discover_profile_links(team_page, deep=deep_scrape)
            self.stats['profiles_discovered'] = len(profile_links)
            logger.info(f"Found {len(profile_links)} potential profiles")
            
            if not profile_links:
                return {"success": False, "error": "No profiles found"}
            
            # Step 3: Extract profile data
            if progress_callback:
                progress_callback(3, 5, f"⚙️ Extracting {len(profile_links)} profiles...")
            
            extractor = ProfileExtractor()
            profiles = []
            
            for idx, link_info in enumerate(profile_links):
                try:
                    # Scrape individual profile page
                    response = requests.get(link_info['url'], timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract profile data
                    profile = extractor.extract_profile(soup, link_info['url'])
                    
                    # Use discovered name if extraction didn't find one
                    if not profile.get('name'):
                        profile['name'] = link_info['name']
                    
                    profile['profile_url'] = link_info['url']
                    
                    if profile.get('name'):
                        profiles.append(profile)
                    
                    if progress_callback and idx % 5 == 0:
                        progress_callback(3, 5, f"⚙️ Extracted {idx+1}/{len(profile_links)} profiles...")
                
                except Exception as e:
                    logger.warning(f"Failed to extract {link_info.get('name', 'Unknown')}: {e}")
                    continue
            
            self.stats['profiles_extracted'] = len(profiles)
            logger.info(f"Extracted {len(profiles)} profiles")
            
            # Step 4: Deduplicate
            if progress_callback:
                progress_callback(4, 5, "🔄 Removing duplicates...")
            
            deduplicator = ProfileDeduplicator(name_threshold=0.85)
            unique_profiles = deduplicator.deduplicate(profiles)
            self.stats['duplicates_removed'] = len(profiles) - len(unique_profiles)
            
            # Update stats from extractor
            extractor_stats = extractor.get_stats()
            self.stats['emails_found'] = extractor_stats['emails_found']
            self.stats['photos_found'] = extractor_stats['photos_found']
            
            # Step 5: Save to database
            if progress_callback:
                progress_callback(5, 5, "💾 Saving to database...")
            
            insert_profiles(unique_profiles, db_path=self.db_path)
            update_vector_database(db_path=self.db_path)
            departments = get_departments(db_path=self.db_path)
            
            logger.info(f"✅ Scraping complete: {len(unique_profiles)} profiles saved")
            
            return {
                "success": True,
                "profiles_count": len(unique_profiles),
                "departments": departments,
                "stats": self.stats
            }
            
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
