"""
Advanced Profile Discovery
Intelligent discovery of profile pages across different website structures
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ProfileDiscovery:
    """Intelligent profile page discovery system."""
    
    # Common team page patterns
    TEAM_PAGE_PATTERNS = [
        '/team', '/about-us/team', '/leadership', '/leadership-team',
        '/about/team', '/about/leadership', '/our-team', '/meet-the-team',
        '/people', '/about/people', '/company/team', '/company/leadership',
        '/about-us', '/about', '/executives', '/management', '/staff',
        '/team-members', '/our-people', '/employees', '/board'
    ]
    
    # Keywords to identify team pages
    TEAM_PAGE_KEYWORDS = [
        'team', 'leadership', 'people', 'about us', 'executives', 
        'management', 'staff', 'our people', 'meet the team', 'board'
    ]
    
    # Profile link indicators
    PROFILE_INDICATORS = [
        'profile', 'person', 'team-member', 'employee', 'staff',
        'bio', 'about', 'people/', '/team/', '/staff/', '/people/'
    ]
    
    def __init__(self, max_workers: int = 3, timeout: int = 10):
        """
        Initialize discovery system.
        
        Args:
            max_workers: Max concurrent requests
            timeout: Request timeout in seconds
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.visited_urls: Set[str] = set()
    
    def discover_team_page(self, base_url: str) -> Optional[str]:
        """
        Discover team/leadership page using multiple strategies.
        
        Args:
            base_url: Base website URL
            
        Returns:
            URL of team page or None
        """
        logger.info(f"🔍 Discovering team page on: {base_url}")
        
        # Strategy 1: Try direct URL patterns
        team_url = self._try_direct_patterns(base_url)
        if team_url:
            logger.info(f"✅ Found via direct pattern: {team_url}")
            return team_url
        
        # Strategy 2: Search homepage for team links
        team_url = self._search_homepage(base_url)
        if team_url:
            logger.info(f"✅ Found via homepage search: {team_url}")
            return team_url
        
        # Strategy 3: Check sitemap
        team_url = self._check_sitemap(base_url)
        if team_url:
            logger.info(f"✅ Found via sitemap: {team_url}")
            return team_url
        
        logger.warning(f"⚠️ Could not find team page on {base_url}")
        return None
    
    def discover_profile_links(self, team_page_url: str, deep: bool = True) -> List[Dict[str, str]]:
        """
        Discover individual profile links on a team page.
        
        Args:
            team_page_url: URL of team/leadership page
            deep: Whether to follow links to individual profile pages
            
        Returns:
            List of profile link dictionaries with 'name', 'url', 'type'
        """
        logger.info(f"🔍 Discovering profiles on: {team_page_url}")
        
        try:
            response = requests.get(team_page_url, headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            profile_links = []
            
            # Strategy 1: Look for profile cards/containers
            profile_links.extend(self._find_profile_containers(soup, team_page_url))
            
            # Strategy 2: Look for individual profile links
            profile_links.extend(self._find_profile_links(soup, team_page_url))
            
            # Strategy 3: Look for people in structured data
            profile_links.extend(self._find_structured_profiles(soup, team_page_url))
            
            # Remove duplicates
            unique_links = self._deduplicate_links(profile_links)
            
            logger.info(f"✅ Found {len(unique_links)} profile links")
            
            return unique_links
            
        except Exception as e:
            logger.error(f"Error discovering profiles: {e}")
            return []
    
    def _try_direct_patterns(self, base_url: str) -> Optional[str]:
        """Try common team page URL patterns."""
        base = base_url.rstrip('/')
        
        for pattern in self.TEAM_PAGE_PATTERNS:
            test_url = base + pattern
            try:
                response = requests.head(
                    test_url, 
                    headers=self.headers, 
                    timeout=self.timeout, 
                    allow_redirects=True
                )
                if response.status_code == 200:
                    return test_url
            except:
                continue
        
        return None
    
    def _search_homepage(self, base_url: str) -> Optional[str]:
        """Search homepage for links to team page."""
        try:
            response = requests.get(base_url, headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for navigation links
            nav_links = soup.find_all(['nav', 'header', 'footer'])
            for nav in nav_links:
                links = nav.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '').lower()
                    text = link.get_text(strip=True).lower()
                    
                    # Check if link text or URL contains team keywords
                    if any(keyword in href or keyword in text for keyword in self.TEAM_PAGE_KEYWORDS):
                        full_url = urljoin(base_url, link['href'])
                        
                        # Verify it's a valid page
                        if self._verify_team_page(full_url):
                            return full_url
            
            # Look in all links if not found in nav
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()
                
                if any(keyword in href or keyword in text for keyword in self.TEAM_PAGE_KEYWORDS):
                    full_url = urljoin(base_url, link['href'])
                    if self._verify_team_page(full_url):
                        return full_url
        
        except Exception as e:
            logger.error(f"Error searching homepage: {e}")
        
        return None
    
    def _check_sitemap(self, base_url: str) -> Optional[str]:
        """Check sitemap for team page URL."""
        sitemap_urls = [
            urljoin(base_url, '/sitemap.xml'),
            urljoin(base_url, '/sitemap_index.xml'),
            urljoin(base_url, '/sitemap/'),
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = requests.get(sitemap_url, headers=self.headers, timeout=self.timeout)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    urls = soup.find_all('loc')
                    
                    for url_tag in urls:
                        url = url_tag.get_text().lower()
                        if any(keyword in url for keyword in self.TEAM_PAGE_KEYWORDS):
                            return url_tag.get_text()
            except:
                continue
        
        return None
    
    def _verify_team_page(self, url: str) -> bool:
        """Verify that URL is actually a team page."""
        try:
            response = requests.head(url, headers=self.headers, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def _find_profile_containers(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Find profile cards or containers."""
        profiles = []
        
        # Common container selectors
        container_selectors = [
            '.team-member', '.profile', '.person', '.employee', '.staff-member',
            '[class*="team-member"]', '[class*="profile"]', '[class*="person"]',
            '[class*="employee"]', '[data-type="person"]'
        ]
        
        for selector in container_selectors:
            containers = soup.select(selector)
            for container in containers:
                # Extract name
                name_elem = container.find(['h2', 'h3', 'h4', '.name', '[class*="name"]'])
                if not name_elem:
                    continue
                
                name = name_elem.get_text(strip=True)
                
                # Extract link if exists
                link = container.find('a', href=True)
                url = urljoin(base_url, link['href']) if link else base_url
                
                profiles.append({
                    'name': name,
                    'url': url,
                    'type': 'container'
                })
        
        return profiles
    
    def _find_profile_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Find individual profile page links."""
        profiles = []
        
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if link looks like a profile
            is_profile = any(indicator in href.lower() for indicator in self.PROFILE_INDICATORS)
            
            if is_profile and text and len(text.split()) >= 2:
                full_url = urljoin(base_url, href)
                
                profiles.append({
                    'name': text,
                    'url': full_url,
                    'type': 'link'
                })
        
        return profiles
    
    def _find_structured_profiles(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Find profiles in structured data (Schema.org, JSON-LD)."""
        profiles = []
        
        # Look for Schema.org Person markup
        person_elements = soup.find_all(attrs={'itemtype': 'http://schema.org/Person'})
        
        for person in person_elements:
            name_elem = person.find(attrs={'itemprop': 'name'})
            if name_elem:
                name = name_elem.get_text(strip=True)
                url_elem = person.find(attrs={'itemprop': 'url'})
                url = urljoin(base_url, url_elem.get('href', '')) if url_elem else base_url
                
                profiles.append({
                    'name': name,
                    'url': url,
                    'type': 'structured'
                })
        
        return profiles
    
    def _deduplicate_links(self, links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove duplicate profile links."""
        seen_urls = set()
        seen_names = set()
        unique = []
        
        for link in links:
            url = link['url']
            name = link['name'].lower()
            
            if url not in seen_urls and name not in seen_names:
                seen_urls.add(url)
                seen_names.add(name)
                unique.append(link)
        
        return unique
