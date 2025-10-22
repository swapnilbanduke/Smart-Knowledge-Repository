"""
Duplicate Detection and Profile Merging
Handles duplicate profiles and merges information intelligently
"""

from typing import List, Dict, Any, Optional
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class ProfileDeduplicator:
    """Intelligent duplicate detection and profile merging."""
    
    def __init__(self, name_threshold: float = 0.85, merge_strategy: str = 'prefer_complete'):
        """
        Initialize deduplicator.
        
        Args:
            name_threshold: Similarity threshold for name matching (0-1)
            merge_strategy: 'prefer_complete' or 'prefer_recent' or 'manual'
        """
        self.name_threshold = name_threshold
        self.merge_strategy = merge_strategy
        self.duplicate_count = 0
        self.merge_count = 0
    
    def deduplicate(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find and merge duplicate profiles.
        
        Args:
            profiles: List of profile dictionaries
            
        Returns:
            Deduplicated list of profiles
        """
        if not profiles:
            return []
        
        logger.info(f"Deduplicating {len(profiles)} profiles...")
        
        unique_profiles = []
        duplicate_groups = []
        
        for profile in profiles:
            # Check if this profile is a duplicate
            duplicate_of = self._find_duplicate(profile, unique_profiles)
            
            if duplicate_of is not None:
                # Found a duplicate - merge them
                self.duplicate_count += 1
                merged = self._merge_profiles(unique_profiles[duplicate_of], profile)
                unique_profiles[duplicate_of] = merged
                self.merge_count += 1
                
                logger.info(f"Merged duplicate: {profile.get('name', 'Unknown')}")
            else:
                # New unique profile
                unique_profiles.append(profile)
        
        logger.info(f"✅ Deduplication complete: {len(profiles)} → {len(unique_profiles)} profiles")
        logger.info(f"   Found {self.duplicate_count} duplicates, performed {self.merge_count} merges")
        
        return unique_profiles
    
    def _find_duplicate(self, profile: Dict[str, Any], existing: List[Dict[str, Any]]) -> Optional[int]:
        """
        Find if profile is a duplicate of any existing profile.
        
        Returns:
            Index of duplicate profile in existing list, or None
        """
        profile_name = profile.get('name', '').strip().lower()
        if not profile_name:
            return None
        
        for idx, existing_profile in enumerate(existing):
            existing_name = existing_profile.get('name', '').strip().lower()
            
            # Check name similarity
            similarity = self._calculate_similarity(profile_name, existing_name)
            
            if similarity >= self.name_threshold:
                return idx
            
            # Also check exact email match
            profile_email = profile.get('contact', '').strip().lower()
            existing_email = existing_profile.get('contact', '').strip().lower()
            if profile_email and existing_email and profile_email == existing_email:
                return idx
        
        return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate string similarity using Levenshtein-based ratio.
        
        Returns:
            Similarity score between 0 and 1
        """
        if not str1 or not str2:
            return 0.0
        
        # Normalize strings
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        # Exact match
        if str1 == str2:
            return 1.0
        
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, str1, str2).ratio()
    
    def _merge_profiles(self, profile1: Dict[str, Any], profile2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two profiles intelligently.
        
        Strategies:
        - prefer_complete: Choose non-empty values
        - prefer_recent: Prefer profile2 (newer scrape)
        - manual: Return both for manual review
        """
        if self.merge_strategy == 'prefer_recent':
            # Start with newer profile, fill in gaps from older
            merged = profile2.copy()
            for key, value in profile1.items():
                if key not in merged or not merged[key]:
                    merged[key] = value
        
        elif self.merge_strategy == 'prefer_complete':
            # Start with profile1, override with more complete data from profile2
            merged = profile1.copy()
            for key, value in profile2.items():
                # Skip if value is empty
                if not value:
                    continue
                
                # Always take if profile1 doesn't have it
                if key not in merged or not merged[key]:
                    merged[key] = value
                    continue
                
                # For text fields, prefer longer/more detailed
                if key in ['bio', 'role']:
                    if len(str(value)) > len(str(merged[key])):
                        merged[key] = value
                
                # For URLs, prefer HTTPS
                if key in ['photo_url', 'profile_url', 'linkedin', 'twitter']:
                    if value.startswith('https://') and merged[key].startswith('http://'):
                        merged[key] = value
        
        else:  # manual or default
            # Prefer most complete profile
            merged = profile1.copy()
            for key, value in profile2.items():
                if value and (key not in merged or not merged[key]):
                    merged[key] = value
        
        # Add merge metadata
        merged['_merged'] = True
        merged['_merge_count'] = merged.get('_merge_count', 1) + 1
        
        return merged
    
    def get_stats(self) -> Dict[str, int]:
        """Get deduplication statistics."""
        return {
            'duplicates_found': self.duplicate_count,
            'merges_performed': self.merge_count
        }
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize name for comparison."""
        if not name:
            return ''
        
        # Remove titles
        titles = ['Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Dr', 'Mr', 'Mrs', 'Ms', 'Prof']
        for title in titles:
            name = name.replace(title, '').strip()
        
        # Remove middle initials
        import re
        name = re.sub(r'\b[A-Z]\.\s*', '', name)
        
        # Normalize whitespace
        name = ' '.join(name.split())
        
        return name.lower()
    
    @staticmethod
    def extract_first_last(name: str) -> tuple:
        """Extract first and last name from full name."""
        parts = name.strip().split()
        if len(parts) == 0:
            return ('', '')
        elif len(parts) == 1:
            return (parts[0], '')
        else:
            return (parts[0], parts[-1])
