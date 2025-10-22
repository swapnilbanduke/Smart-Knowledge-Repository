""""""

Content Discovery - Find team pages and extract profile linksContent Discovery - Auto-discovers and categorizes content

""""""



import requestsimport logging

from bs4 import BeautifulSoupfrom typing import List, Dict, Set

from typing import List, Dict, Any, Optionalfrom urllib.parse import urljoin, urlparse

import loggingimport yaml

from urllib.parse import urljoin

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class ContentDiscovery:

    """Automatically discovers and categorizes content from websites"""

def find_team_page(base_url: str) -> Optional[str]:    

    """    def __init__(self, targets_file: str = None):

    Automatically find the team/leadership page from a website.        self.targets_file = targets_file

            self.visited_urls: Set[str] = set()

    Args:        self.discovered_content: List[Dict] = []

        base_url: Base URL of the website    

            def load_targets(self) -> List[Dict]:

    Returns:        """Load scraping targets from YAML configuration"""

        URL of team/leadership page or None        if not self.targets_file:

    """            return []

    logger.info(f"Searching for team page on: {base_url}")        

            try:

    # Common team page patterns            with open(self.targets_file, 'r') as f:

    team_patterns = [                config = yaml.safe_load(f)

        '/team', '/about-us/team', '/leadership', '/leadership-team',                return config.get('targets', [])

        '/about/team', '/about/leadership', '/our-team', '/meet-the-team',        except Exception as e:

        '/people', '/about/people', '/company/team', '/company/leadership',            logger.error(f"Error loading targets: {str(e)}")

        '/about-us', '/about', '/executives', '/management'            return []

    ]    

        def discover_content(self, seed_urls: List[str], max_depth: int = 2) -> List[Dict]:

    headers = {        """

        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',        Discover content starting from seed URLs

    }        

            Args:

    # Try direct patterns first            seed_urls: Initial URLs to start discovery

    for pattern in team_patterns:            max_depth: Maximum depth for crawling

        test_url = base_url.rstrip('/') + pattern            

        try:        Returns:

            response = requests.head(test_url, headers=headers, timeout=10, allow_redirects=True)            List of discovered content items

            if response.status_code == 200:        """

                logger.info(f"✅ Found team page: {test_url}")        self.discovered_content = []

                return test_url        

        except:        for url in seed_urls:

            continue            self._crawl_url(url, depth=0, max_depth=max_depth)

            

    # Try to find links on homepage        logger.info(f"Discovered {len(self.discovered_content)} content items")

    try:        return self.discovered_content

        response = requests.get(base_url, headers=headers, timeout=10)    

        soup = BeautifulSoup(response.content, 'html.parser')    def _crawl_url(self, url: str, depth: int, max_depth: int):

                """Recursively crawl URLs"""

        # Look for links containing team/leadership keywords        if depth > max_depth or url in self.visited_urls:

        for link in soup.find_all('a', href=True):            return

            href = link.get('href', '').lower()        

            text = link.get_text(strip=True).lower()        self.visited_urls.add(url)

                    logger.info(f"Crawling: {url} (depth: {depth})")

            keywords = ['team', 'leadership', 'people', 'about us', 'executives', 'management']        

            if any(keyword in href or keyword in text for keyword in keywords):        # Implementation would use ProfileScraper here

                full_url = urljoin(base_url, link['href'])        # For now, just structure the logic

                logger.info(f"✅ Found potential team page: {full_url}")        

                return full_url    def categorize_content(self, content: Dict) -> str:

    except Exception as e:        """

        logger.error(f"Error finding team page: {e}")        Categorize discovered content

            

    return None        Args:

            content: Content dictionary

            

def extract_profile_links(soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:        Returns:

    """            Category name

    Extract profile links from team page.        """

            # Simple categorization logic

    Args:        url = content.get('url', '')

        soup: BeautifulSoup object of team page        title = content.get('title', '').lower()

        base_url: Base URL for resolving relative links        

                if 'blog' in url or 'article' in url:

    Returns:            return 'articles'

        List of profile data dictionaries        elif 'doc' in url or 'documentation' in url:

    """            return 'documentation'

    profiles = []        elif 'tutorial' in title or 'guide' in title:

    seen_names = set()            return 'tutorials'

            else:

    # Try multiple selectors for person links            return 'general'

    person_selectors = [    

        'a[href*="/team/"]',    def filter_by_scope(self, content: List[Dict], scope: str) -> List[Dict]:

        'a[href*="/leadership/"]',        """Filter content by scope/category"""

        'a[href*="/people/"]',        return [c for c in content if c.get('category') == scope]

        '.team-member a',
        '.leadership-member a',
        '.person a',
        '.profile a'
    ]
    
    for selector in person_selectors:
        person_links = soup.select(selector)
        if person_links:
            logger.info(f"Found {len(person_links)} person profile links using: {selector}")
            break
    else:
        person_links = []
    
    for link in person_links:
        name = link.get_text(strip=True)
        
        # Skip empty names or duplicates
        if not name or name in seen_names:
            continue
        
        # Skip if name is too short (likely not a full name)
        if len(name.split()) < 2:
            continue
        
        # Skip service/department names
        non_person_keywords = ['services', 'solutions', 'about', 'contact', 'read more', 
                               'learn more', 'view profile', 'see more', 'click here']
        if any(keyword in name.lower() for keyword in non_person_keywords):
            continue
        
        seen_names.add(name)
        
        profile = {
            'name': name,
            'profile_url': urljoin(base_url, link.get('href', ''))
        }
        profiles.append(profile)
        logger.info(f"Found: {name} - ")
    
    return profiles
