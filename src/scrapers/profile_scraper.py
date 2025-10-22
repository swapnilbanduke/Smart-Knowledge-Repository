"""
Enhanced Scraper with Dynamic URL Support
Scrapes leadership/team pages from any website
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import time
import logging
import re
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_team_page(base_url: str) -> Optional[str]:
    """
    Automatically find the team/leadership page from a website.
    
    Args:
        base_url: Base URL of the website
        
    Returns:
        URL of team/leadership page or None
    """
    logger.info(f"Searching for team page on: {base_url}")
    
    # Common team page patterns
    team_patterns = [
        '/team', '/about-us/team', '/leadership', '/leadership-team',
        '/about/team', '/about/leadership', '/our-team', '/meet-the-team',
        '/people', '/about/people', '/company/team', '/company/leadership',
        '/about-us', '/about', '/executives', '/management'
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    # Try direct patterns first
    for pattern in team_patterns:
        test_url = base_url.rstrip('/') + pattern
        try:
            response = requests.head(test_url, headers=headers, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                logger.info(f"✅ Found team page: {test_url}")
                return test_url
        except:
            continue
    
    # Try to find links on homepage
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for links containing team/leadership keywords
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text(strip=True).lower()
            
            keywords = ['team', 'leadership', 'people', 'about us', 'executives', 'management']
            if any(keyword in href or keyword in text for keyword in keywords):
                full_url = urljoin(base_url, link['href'])
                logger.info(f"✅ Found potential team page: {full_url}")
                return full_url
    except Exception as e:
        logger.error(f"Error finding team page: {e}")
    
    return None


def extract_from_person_links(person_links: List, base_url: str) -> List[Dict[str, Any]]:
    """
    Extract profiles from person profile links with enhanced data extraction.
    Uses multi-template approach to handle various website layouts.
    """
    profiles = []
    seen_names = set()
    
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
        
        # Get profile URL
        profile_url = urljoin(base_url, link.get('href', ''))
        
        # Try to find role and photo near the link (Multi-template approach)
        role = ""
        photo_url = ""
        bio = ""
        contact_info = {'email': '', 'phone': '', 'linkedin': '', 'twitter': ''}
        
        parent = link.parent
        if parent:
            # Template 1: Role in next siblings
            for sibling in parent.find_next_siblings(['p', 'span', 'div'], limit=3):
                potential_role = sibling.get_text(strip=True)
                if potential_role and len(potential_role) < 100 and not role:
                    role = potential_role
                    break
            
            # Template 2: Role in child elements
            if not role:
                role_elem = parent.find(class_=re.compile(r'title|position|role|designation', re.I))
                if role_elem:
                    role = role_elem.get_text(strip=True)
            
            # Photo extraction with multiple fallbacks
            img_tag = (parent.find('img') or 
                      parent.find_previous('img') or 
                      parent.find_next('img'))
            if img_tag:
                # Try multiple image attributes
                photo_url = (img_tag.get('src') or 
                           img_tag.get('data-src') or 
                           img_tag.get('data-lazy-src') or
                           img_tag.get('srcset', '').split(',')[0].split()[0] if img_tag.get('srcset') else '')
                
                if photo_url and not photo_url.startswith('http'):
                    photo_url = urljoin(base_url, photo_url)
            
            # Extract bio if available
            bio_elem = parent.find(class_=re.compile(r'bio|description|excerpt', re.I))
            if bio_elem:
                bio = bio_elem.get_text(strip=True)[:500]
            
            # Extract contact information
            contact_info = extract_contact_info(parent.get_text(), parent)
        
        department = categorize_role(role) if role else 'Executive'
        
        profile = {
            'name': name,
            'role': role,
            'bio': bio,
            'photo_url': photo_url,
            'contact': contact_info.get('email', ''),
            'phone': contact_info.get('phone', ''),
            'linkedin': contact_info.get('linkedin', ''),
            'twitter': contact_info.get('twitter', ''),
            'department': department,
            'profile_url': profile_url
        }
        
        profiles.append(profile)
        logger.info(f"Found: {name} - {role}")
    
    return profiles


def scrape_team_page(url: str) -> List[Dict[str, Any]]:
    """
    Scrape team/leadership profiles from any website.
    
    Args:
        url: URL of the team page
        
    Returns:
        List of dictionaries containing profile data
    """
    logger.info(f"Scraping team page: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        profiles = []
        
        # Strategy 1: Look for person profile links (most reliable)
        person_links = soup.find_all('a', href=re.compile(r'/(leadership|team-member|profile|people)/', re.I))
        if person_links:
            logger.info(f"Found {len(person_links)} person profile links")
            profiles = extract_from_person_links(person_links, url)
        
        # Strategy 2: Look for team member containers (only if strategy 1 fails)
        if not profiles:
            team_containers = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'team|member|profile|person|employee|leader|executive', re.I))
            
            if team_containers:
                logger.info(f"Found {len(team_containers)} potential team member containers")
                profiles = extract_from_containers(team_containers, url)
        
        # Strategy 3: Look for name headings (h2, h3, h4)
        if not profiles:
            name_headings = soup.find_all(['h2', 'h3', 'h4'])
            profiles = extract_from_headings(name_headings, url)
        
        # Strategy 4: Look for structured data (JSON-LD)
        if not profiles:
            profiles = extract_from_structured_data(soup)
        
        logger.info(f"Total profiles extracted: {len(profiles)}")
        return profiles
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching page: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing page: {e}")
        return []


def extract_from_containers(containers: List, base_url: str) -> List[Dict[str, Any]]:
    """Extract profiles from team member containers."""
    profiles = []
    
    for container in containers:
        # Extract name
        name = ""
        name_tag = container.find(['h2', 'h3', 'h4', 'h5'])
        if name_tag:
            name = name_tag.get_text(strip=True)
        
        if not name or len(name) > 100:  # Skip if no name or too long
            continue
        
        # Skip if it looks like a service/department name (not a person)
        non_person_keywords = ['ai', 'ml', 'automation', 'strategy', 'consulting', 'services', 
                               'solutions', 'development', 'engineering', 'design', 'testing',
                               'cloud', 'data', 'analytics', 'software', 'platform', 'infrastructure']
        if any(keyword in name.lower() for keyword in non_person_keywords) and len(name.split()) < 3:
            continue
        
        # Check if it looks like a person's name (has at least 2 words, first letter capitalized)
        name_parts = name.split()
        if len(name_parts) < 2 or not name_parts[0][0].isupper():
            continue
        
        # Extract role
        role = ""
        role_tag = container.find(['p', 'span', 'div'], class_=re.compile(r'title|role|position|job', re.I))
        if role_tag:
            role = role_tag.get_text(strip=True)
        elif container.find('p'):
            # First paragraph might be role
            first_p = container.find('p')
            potential_role = first_p.get_text(strip=True)
            if len(potential_role) < 100:
                role = potential_role
        
        # Extract photo with multiple fallbacks
        photo_url = ""
        img_tag = container.find('img')
        if img_tag:
            photo_url = (img_tag.get('src') or 
                        img_tag.get('data-src') or 
                        img_tag.get('data-lazy-src') or
                        img_tag.get('srcset', '').split(',')[0].split()[0] if img_tag.get('srcset') else '')
            
            if photo_url and not photo_url.startswith('http'):
                photo_url = urljoin(base_url, photo_url)
        
        # Extract bio
        bio = ""
        bio_tag = container.find(['p', 'div'], class_=re.compile(r'bio|description|about', re.I))
        if bio_tag:
            bio = bio_tag.get_text(strip=True)
        else:
            # Get all paragraphs
            paragraphs = container.find_all('p')
            if len(paragraphs) > 1:
                bio = ' '.join([p.get_text(strip=True) for p in paragraphs[1:]])
        
        # Extract profile URL
        profile_url = ""
        link_tag = container.find('a', href=True)
        if link_tag:
            profile_url = urljoin(base_url, link_tag['href'])
        
        # Extract contact information (email, phone, social links)
        container_text = container.get_text()
        contact_info = extract_contact_info(container_text, container)
        
        # Categorize department
        department = categorize_role(role)
        
        profile = {
            'name': name,
            'role': role,
            'bio': bio[:500] if bio else '',  # Limit bio length
            'photo_url': photo_url,
            'contact': contact_info.get('email', ''),
            'phone': contact_info.get('phone', ''),
            'linkedin': contact_info.get('linkedin', ''),
            'twitter': contact_info.get('twitter', ''),
            'department': department,
            'profile_url': profile_url
        }
        
        profiles.append(profile)
        logger.info(f"Found: {name} - {role}")
    
    return profiles


def extract_from_headings(headings: List, base_url: str) -> List[Dict[str, Any]]:
    """Extract profiles from heading tags."""
    profiles = []
    
    for heading in headings:
        name = heading.get_text(strip=True)
        
        # Skip if doesn't look like a person's name
        if len(name) > 100 or len(name.split()) > 5:
            continue
        
        # Skip service/department names
        non_person_keywords = ['ai', 'ml', 'automation', 'strategy', 'consulting', 'services',
                               'solutions', 'development', 'engineering', 'design', 'testing',
                               'cloud', 'data', 'analytics', 'software', 'platform', 'infrastructure']
        if any(keyword in name.lower() for keyword in non_person_keywords) and len(name.split()) < 3:
            continue
        
        # Must have at least 2 words (first and last name)
        if len(name.split()) < 2:
            continue
        
        # Get parent container
        parent = heading.parent
        
        # Extract role
        role = ""
        next_elem = heading.find_next(['p', 'span', 'div'])
        if next_elem:
            potential_role = next_elem.get_text(strip=True)
            if len(potential_role) < 100:
                role = potential_role
        
        # Extract photo
        photo_url = ""
        img_tag = parent.find('img') if parent else None
        if img_tag:
            photo_url = img_tag.get('src', '') or img_tag.get('data-src', '')
            if photo_url and not photo_url.startswith('http'):
                photo_url = urljoin(base_url, photo_url)
        
        department = categorize_role(role)
        
        profile = {
            'name': name,
            'role': role,
            'bio': '',
            'photo_url': photo_url,
            'contact': '',
            'department': department,
            'profile_url': ''
        }
        
        profiles.append(profile)
    
    return profiles


def extract_from_structured_data(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract profiles from JSON-LD structured data."""
    profiles = []
    
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            import json
            data = json.loads(script.string)
            
            # Look for Person schema
            if isinstance(data, dict) and data.get('@type') == 'Person':
                profile = {
                    'name': data.get('name', ''),
                    'role': data.get('jobTitle', ''),
                    'bio': data.get('description', ''),
                    'photo_url': data.get('image', ''),
                    'contact': data.get('email', ''),
                    'department': categorize_role(data.get('jobTitle', '')),
                    'profile_url': data.get('url', '')
                }
                profiles.append(profile)
        except:
            continue
    
    return profiles


def categorize_role(role: str) -> str:
    """
    Categorize role into departments.
    
    Args:
        role: Job title/role
        
    Returns:
        Department name
    """
    if not role:
        return 'Leadership'
    
    role_lower = role.lower()
    
    # Technology
    if any(kw in role_lower for kw in ['cto', 'chief technology', 'vp technology', 'engineering', 
                                         'software', 'technical', 'architect', 'developer']):
        return 'Technology'
    
    # Finance
    elif any(kw in role_lower for kw in ['cfo', 'chief financial', 'vp finance', 'treasurer',
                                           'accounting', 'controller']):
        return 'Finance'
    
    # Operations
    elif any(kw in role_lower for kw in ['coo', 'chief operating', 'vp operations', 'operations',
                                           'logistics', 'supply chain']):
        return 'Operations'
    
    # Marketing
    elif any(kw in role_lower for kw in ['cmo', 'chief marketing', 'vp marketing', 'marketing',
                                           'brand', 'communications']):
        return 'Marketing'
    
    # Human Resources
    elif any(kw in role_lower for kw in ['chro', 'chief human', 'vp hr', 'vp people', 'hr',
                                           'human resources', 'talent']):
        return 'Human Resources'
    
    # Sales
    elif any(kw in role_lower for kw in ['sales', 'revenue', 'business development', 'cro']):
        return 'Sales'
    
    # Legal
    elif any(kw in role_lower for kw in ['legal', 'general counsel', 'attorney', 'compliance']):
        return 'Legal'
    
    # Product
    elif any(kw in role_lower for kw in ['product', 'cpo', 'chief product']):
        return 'Product'
    
    # Executive/Leadership
    elif any(kw in role_lower for kw in ['ceo', 'president', 'founder', 'chairman', 'chief executive',
                                           'managing director', 'executive director']):
        return 'Executive'
    
    else:
        return 'Other'


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate if URL is accessible.
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format. Please include http:// or https://"
        
        # Check if accessible
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        
        if response.status_code >= 400:
            return False, f"Website returned error code: {response.status_code}"
        
        return True, ""
        
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to website. Please check the URL."
    except requests.exceptions.Timeout:
        return False, "Website took too long to respond. Please try again."
    except Exception as e:
        return False, f"Error: {str(e)}"


def extract_contact_info(text: str, soup_element=None) -> Dict[str, str]:
    """
    Extract contact information (email, phone, social links) from text or HTML element.
    
    Args:
        text: Text to search for contact info
        soup_element: BeautifulSoup element to search for links
        
    Returns:
        Dictionary with contact information
    """
    contact = {
        'email': '',
        'phone': '',
        'linkedin': '',
        'twitter': '',
        'website': ''
    }
    
    if not text and not soup_element:
        return contact
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if text:
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group(0)
    
    # Extract phone
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    if text:
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group(0)
    
    # Extract social links from HTML
    if soup_element:
        links = soup_element.find_all('a', href=True)
        for link in links:
            href = link.get('href', '').lower()
            if 'linkedin.com' in href:
                contact['linkedin'] = link['href']
            elif 'twitter.com' in href or 'x.com' in href:
                contact['twitter'] = link['href']
            elif 'mailto:' in href:
                contact['email'] = href.replace('mailto:', '')
            elif 'tel:' in href:
                contact['phone'] = href.replace('tel:', '')
    
    return contact


def scrape_individual_profile(profile_url: str, base_url: str) -> Dict[str, Any]:
    """
    Scrape detailed information from an individual profile page.
    
    Args:
        profile_url: URL of the individual profile page
        base_url: Base URL for resolving relative URLs
        
    Returns:
        Dictionary with detailed profile information
    """
    logger.info(f"Scraping individual profile: {profile_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    # Retry logic for transient errors (503, timeouts, etc.)
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(profile_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            break  # Success, exit retry loop
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503 and attempt < max_retries - 1:
                logger.warning(f"503 error on attempt {attempt + 1}/{max_retries}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                raise  # Re-raise if not 503 or last attempt
        except requests.exceptions.Timeout as e:
            if attempt < max_retries - 1:
                logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                raise
    
    try:
        import re as regex
        
        # Extract name (usually in h1 or title)
        name = ''
        name_tag = soup.find('h1')
        if name_tag:
            name = name_tag.get_text(strip=True)
        
        # Extract role/title (actual position, not department)
        role = ''
        
        # ROBUST STRATEGY: Search ALL elementor-widget-container divs for role
        # This is specific to Amzur's Elementor-based pages
        all_widgets = soup.find_all('div', class_='elementor-widget-container')
        
        # Prepare name variations for cleaning
        name_variations = [name] if name else []
        if name and ' ' in name:
            name_parts = name.split()
            name_variations.extend(name_parts)  # Add individual name parts
        
        # Job title keywords
        job_keywords_pattern = r'(CEO|CTO|CFO|COO|President|Vice President|VP|Director|Manager|Head of|Head|Chief|Lead|Senior|Executive|Architect|Practice Head)'
        
        # Noise patterns to skip - these are standalone phrases, not parts of job titles
        noise_patterns = [
            'Keep yourself up to date',  # Exact match first
            'Keep yourself',
            'Learn more', 'Read more', 'Click here',
            'HOME', 'LEADERSHIP', 'Contact', 'Resources',
            'Engagement Models', 'About Us', 'About',
            'Transforming', 'Containers', 'How to',
            'AI-Powered', 'Transform Your',
            'Invoice', 'Connector', 'Blog',
            'Case Study', 'Subscribe', 'Follow',
            'NetSuite', 'Shopify', 'Digital', 'Cloud',
            'AI / ML', 'ERP'
        ]
        
        # Don't filter these if they appear WITH a job title keyword
        # (e.g., "Head of Managed Testing Services" should NOT be filtered)
        
        for widget in all_widgets:
            text = widget.get_text(strip=True)
            
            # Skip if empty, too long, too short, or same as name
            if not text or text == name or len(text) > 300 or len(text) < 5:
                continue
            
            # Check for job keywords FIRST
            has_job_keyword = regex.search(job_keywords_pattern, text, regex.IGNORECASE)
            
            # Only apply noise filter if it's an EXACT match or doesn't have job keywords
            # This prevents filtering out valid titles like "Head of Managed Testing Services"
            is_noise = any(noise in text for noise in noise_patterns)
            
            if has_job_keyword and not is_noise and len(text) < 150:
                # Clean the role: remove the name if it's concatenated
                cleaned_role = text
                for name_var in name_variations:
                    # Remove name from end
                    if cleaned_role.endswith(name_var):
                        cleaned_role = cleaned_role[:-len(name_var)].strip()
                    # Remove name from beginning
                    if cleaned_role.startswith(name_var):
                        cleaned_role = cleaned_role[len(name_var):].strip()
                
                # Validate the cleaned role
                if cleaned_role and len(cleaned_role) > 5:
                    # Skip if it's just generic words like "Leadership"
                    if cleaned_role.lower() not in ['leadership', 'executive', 'team']:
                        role = cleaned_role
                        logger.info(f"Found role: {role}")
                        break
        
        # Fallback Strategy 1: Look for text containing job-related keywords with word boundaries
        if not role:
            job_keywords = [
                r'\bceo\b', r'\bcto\b', r'\bcfo\b', r'\bcoo\b', r'\bcio\b',
                r'\bpresident\b', r'\bvp\b', r'\bvice president\b',
                r'\bdirector\b', r'\bchief\b', r'\bfounder\b', r'\bpartner\b',
                r'\bhead of\b', r'\bhead\b', r'\bmanager\b', r'\blead\b', r'\bsenior\b'
            ]
            
            # Search all divs and paragraphs for role text
            for div in soup.find_all(['div', 'p', 'span']):
                text = div.get_text(strip=True)
                # Check if text contains job keywords and is short enough to be a title
                if text and 5 < len(text) < 150:
                    text_lower = text.lower()
                    # Use word boundaries to avoid partial matches
                    if any(regex.search(keyword, text_lower) for keyword in job_keywords):
                        # Make sure it's not part of navigation, links, or long text
                        skip_terms = ['consulting', 'services', 'digital solutions', 'engagement model', 'click', 'learn more', 'invoice', 'connector', 'keep yourself up to date']
                        if not any(skip in text_lower for skip in skip_terms):
                            # Clean the role: remove the person's name if it's appended
                            role = text
                            # If name is at the end, remove it
                            if name and role.endswith(name):
                                role = role[:-len(name)].strip()
                            # Also try removing just first/last name
                            if name:
                                name_parts = name.split()
                                for part in name_parts:
                                    if role.endswith(part):
                                        role = role[:-len(part)].strip()
                            logger.info(f"Found role: {role}")
                            break
        
        # Fallback Strategy 2: Look for specific role/title elements
        if not role:
            role_selectors = [
                soup.find(class_=re.compile(r'^(title|position|role|designation|job-title)$', re.I)),
                soup.find('h2', class_=re.compile(r'title|position', re.I)),
                soup.find('p', class_=re.compile(r'title|position|role', re.I)),
                soup.find('span', class_=re.compile(r'title|position|role', re.I)),
            ]
            
            for selector in role_selectors:
                if selector:
                    potential_role = selector.get_text(strip=True)
                    # Skip generic/wrong text
                    if potential_role and 5 < len(potential_role) < 150:
                        skip_phrases = ['keep yourself up to date', 'subscribe', 'follow us']
                        if not any(skip in potential_role.lower() for skip in skip_phrases):
                            role = potential_role
                            logger.info(f"Found role from selector: {role}")
                            break
                    if potential_role and 5 < len(potential_role) < 100:
                        role = potential_role
                        logger.info(f"Found role from selector: {role}")
                        break
        
        # Strategy 3: Look in structured data or meta tags
        if not role:
            meta_job = soup.find('meta', property='og:job_title') or soup.find('meta', {'name': 'job-title'})
            if meta_job and meta_job.get('content'):
                role = meta_job.get('content')
                logger.info(f"Found role from meta: {role}")
        
        # Extract bio (get full bio, not limited)
        bio = ''
        bio_selectors = [
            soup.find(class_=re.compile(r'bio|about|description|summary|content', re.I)),
            soup.find('div', class_=re.compile(r'content|text|body|main', re.I)),
            soup.find('p')  # Fallback to first paragraph
        ]
        for selector in bio_selectors:
            if selector:
                bio_text = selector.get_text(strip=True)
                if bio_text and len(bio_text) > 50:
                    bio = bio_text  # Keep full bio, no truncation
                    break
        
        # Extract photo with enhanced quality selection - ROBUST VERSION
        photo_url = ''
        
        # Strategy 1: Look for images with person's name in the filename (highest priority)
        # This is the most reliable way to find profile photos
        if name:
            # Get name parts for matching (handle multiple name formats)
            name_parts = []
            name_words = name.split()
            
            # Common Indian name nicknames/short forms
            nickname_map = {
                'balasubramanyam': ['balu', 'bala'],
                'gururaj': ['guru'],
                'muralidhar': ['murali'],
                'venkata': ['venkat'],
                'srinivas': ['srini'],
                'subrahmanyam': ['subbu'],
                'ramakrishna': ['rama', 'krishna'],
                'venkateswara': ['venkat', 'venky'],
                'rajasekhar': ['raja', 'sekhar'],
                'balasubramaniam': ['balu', 'bala']
            }
            
            # Add individual name parts
            for part in name_words:
                if len(part) > 2:
                    name_parts.append(part.lower())
                    # Add nicknames if this name has common short forms
                    part_lower = part.lower()
                    if part_lower in nickname_map:
                        name_parts.extend(nickname_map[part_lower])
            
            # Add combined formats (for "Bala Nemani" -> "bala-nemani", "balanemani", "nemani-bala")
            if len(name_words) >= 2:
                name_parts.append('-'.join([w.lower() for w in name_words]))
                name_parts.append(''.join([w.lower() for w in name_words]))
                name_parts.append(f"{name_words[-1].lower()}-{name_words[0].lower()}")  # Last-First
            
            all_images = soup.find_all('img')
            
            for img in all_images:
                # Try multiple image source attributes
                url = (img.get('src') or img.get('data-src') or img.get('data-lazy-src') or 
                       img.get('data-original') or img.get('data-full-src'))
                
                if url:
                    url_lower = url.lower()
                    # Check if any name part is in the URL
                    if any(part in url_lower for part in name_parts):
                        # Enhanced skip patterns for blog/non-profile images
                        skip_patterns = [
                            'logo', 'icon', 'transforming', 'containers', 'ai-in', 'ai-powered', 
                            'netsuite', 'blog', 'post', 'banner', 'header', 'footer', 
                            'e-commerce', 'kubernetes', 'security', 'retail', 'healthcare',
                            'promotion', 'infrastructure', 'optimization', 'testing'
                        ]
                        if not any(skip in url_lower for skip in skip_patterns):
                            photo_url = url
                            if not photo_url.startswith('http'):
                                photo_url = urljoin(base_url, photo_url)
                            logger.info(f"Found photo with name match: {photo_url}")
                            break
        
        # Strategy 2: Look for images in profile/photo containers
        if not photo_url:
            photo_containers = soup.find_all(['div', 'figure', 'section'], class_=re.compile(r'profile|photo|image|avatar|headshot|portrait|picture', re.I))
            for container in photo_containers[:3]:  # Check first 3 containers
                img = container.find('img')
                if img:
                    # Try multiple image attributes
                    potential_urls = [
                        img.get('src'),
                        img.get('data-src'),
                        img.get('data-lazy-src'),
                        img.get('data-original'),
                        img.get('data-full-src'),
                        img.get('data-bg')
                    ]
                    
                    # Check srcset for highest resolution
                    if img.get('srcset'):
                        srcset = img.get('srcset', '')
                        sources = [s.strip().split() for s in srcset.split(',')]
                        if sources:
                            try:
                                sorted_sources = sorted(sources, key=lambda x: int(x[1].replace('w', '')) if len(x) > 1 and x[1].endswith('w') else 0, reverse=True)
                                potential_urls.insert(0, sorted_sources[0][0])
                            except:
                                potential_urls.insert(0, sources[0][0])
                    
                    # Use first valid URL that's not a logo or blog image
                    for url in potential_urls:
                        if url and url.strip() and not url.startswith('data:'):
                            url_lower = url.lower()
                            skip_patterns = ['logo', 'icon', 'transforming', 'containers', 'ai-in', 'ai-powered', 'netsuite', 'blog', 'post']
                            if not any(skip in url_lower for skip in skip_patterns):
                                photo_url = url
                                if not photo_url.startswith('http'):
                                    photo_url = urljoin(base_url, photo_url)
                                logger.info(f"Found photo in container: {photo_url[:50]}...")
                                break
                    
                    if photo_url:
                        break
        
        # Strategy 3: If no photo found, look for larger square images (likely profile photos)
        if not photo_url:
            all_images = soup.find_all('img')
            candidates = []
            
            for img in all_images:
                # Get dimensions
                width = img.get('width', '0')
                height = img.get('height', '0')
                
                # Get image URL from multiple sources
                url = (img.get('src') or img.get('data-src') or img.get('data-lazy-src') or
                       img.get('data-original') or img.get('data-full-src'))
                       
                if not url or not url.strip() or url.startswith('data:'):
                    continue
                
                # Enhanced skip patterns for non-profile images
                url_lower = url.lower()
                skip_patterns = [
                    'logo', 'icon', 'banner', 'bg-', 'background',
                    'transforming', 'containers', 'ai-in', 'ai-powered', 
                    'netsuite', 'blog', 'post', 'header', 'footer',
                    'e-commerce', 'kubernetes', 'security', 'retail', 'healthcare',
                    'promotion', 'infrastructure', 'optimization', 'testing', 'certs'
                ]
                if any(skip in url_lower for skip in skip_patterns):
                    continue
                
                # Try to get size score (prefer square images around 300-500px)
                size_score = 0
                w = 0
                h = 0
                
                try:
                    if width and width.isdigit():
                        w = int(width)
                    if height and height.isdigit():
                        h = int(height)
                    
                    # Prefer images >= 200px and <= 1000px (profile photo range)
                    if 200 <= w <= 1000 and 200 <= h <= 1000:
                        size_score = w + h
                        
                        # Bonus for square images (profile photos are usually square)
                        if w > 0 and h > 0:
                            ratio = min(w, h) / max(w, h)
                            if ratio > 0.8:  # Nearly square
                                size_score += 500  # Big bonus
                        
                        # Bonus for common profile photo sizes
                        if (w, h) in [(500, 500), (300, 300), (340, 340), (400, 400)]:
                            size_score += 1000
                            
                except:
                    pass
                
                if size_score > 0:
                    candidates.append((url, size_score, w, h))
            
            # Sort by size score and pick the best one
            if candidates:
                candidates.sort(key=lambda x: x[1], reverse=True)
                photo_url = candidates[0][0]
                if not photo_url.startswith('http'):
                    photo_url = urljoin(base_url, photo_url)
                logger.info(f"Found photo from size ranking: {photo_url[:50]}... (score: {candidates[0][1]}, size: {candidates[0][2]}x{candidates[0][3]})")
        
        # Strategy 4: Last resort - look in page metadata
        if not photo_url:
            # Check Open Graph image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                potential_url = og_image.get('content')
                url_lower = potential_url.lower()
                # Only use if it looks like a person photo (has name parts or 'team'/'profile' in URL)
                if name:
                    name_parts = [part.lower() for part in name.split() if len(part) > 2]
                    if any(part in url_lower for part in name_parts) or 'team' in url_lower or 'profile' in url_lower:
                        photo_url = potential_url
                        if not photo_url.startswith('http'):
                            photo_url = urljoin(base_url, photo_url)
                        logger.info(f"Found photo from OG meta: {photo_url[:50]}...")
        
        # Extract contact info
        page_text = soup.get_text()
        contact_info = extract_contact_info(page_text, soup)
        
        profile = {
            'name': name,
            'role': role,
            'bio': bio,
            'photo_url': photo_url,
            'contact': contact_info.get('email', ''),
            'phone': contact_info.get('phone', ''),
            'linkedin': contact_info.get('linkedin', ''),
            'twitter': contact_info.get('twitter', ''),
            'department': categorize_role(role) if role else 'Other',
            'profile_url': profile_url
        }
        
        return profile
        
    except Exception as e:
        logger.error(f"Error scraping profile {profile_url}: {e}")
        return {}


def detect_profile_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """
    Automatically detect profile page links using multiple strategies.
    
    Args:
        soup: BeautifulSoup object of the page
        base_url: Base URL for resolving relative links
        
    Returns:
        List of profile URLs
    """
    profile_urls = []
    seen_urls = set()
    
    # Strategy 1: Look for links with profile-related patterns in href
    patterns = [
        r'/(team|leadership|people|staff|employee|member|profile|person)/',
        r'/team-member/',
        r'/our-team/',
        r'/about/.*/(team|people)',
    ]
    
    for pattern in patterns:
        links = soup.find_all('a', href=re.compile(pattern, re.I))
        for link in links:
            url = urljoin(base_url, link.get('href', ''))
            if url not in seen_urls and url != base_url:
                profile_urls.append(url)
                seen_urls.add(url)
    
    # Strategy 2: Look for cards/containers with links
    containers = soup.find_all(['div', 'article'], class_=re.compile(r'card|member|profile|team', re.I))
    for container in containers:
        link = container.find('a', href=True)
        if link:
            url = urljoin(base_url, link['href'])
            if url not in seen_urls and url != base_url:
                # Check if link text looks like a name
                text = link.get_text(strip=True)
                if text and len(text.split()) >= 2:
                    profile_urls.append(url)
                    seen_urls.add(url)
    
    logger.info(f"Detected {len(profile_urls)} profile links")
    return profile_urls


def merge_duplicate_profiles(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect and merge duplicate profiles based on name similarity.
    
    Args:
        profiles: List of profile dictionaries
        
    Returns:
        List of merged profiles without duplicates
    """
    if not profiles:
        return []
    
    merged = []
    seen_names = {}
    
    for profile in profiles:
        name = profile.get('name', '').strip().lower()
        if not name:
            continue
        
        # Normalize name (remove extra spaces, punctuation)
        normalized_name = re.sub(r'[^\w\s]', '', name)
        normalized_name = re.sub(r'\s+', ' ', normalized_name)
        
        # Check for duplicates
        is_duplicate = False
        for existing_name, existing_profile in seen_names.items():
            # Check if names are very similar (fuzzy match)
            if normalized_name == existing_name:
                is_duplicate = True
                # Merge data (prefer non-empty values)
                for key, value in profile.items():
                    if value and not existing_profile.get(key):
                        existing_profile[key] = value
                break
            
            # Check for partial matches (e.g., "John Smith" vs "John A. Smith")
            name_parts = normalized_name.split()
            existing_parts = existing_name.split()
            if len(name_parts) >= 2 and len(existing_parts) >= 2:
                if name_parts[0] == existing_parts[0] and name_parts[-1] == existing_parts[-1]:
                    is_duplicate = True
                    # Merge data
                    for key, value in profile.items():
                        if value and not existing_profile.get(key):
                            existing_profile[key] = value
                    break
        
        if not is_duplicate:
            seen_names[normalized_name] = profile
            merged.append(profile)
    
    logger.info(f"Merged {len(profiles) - len(merged)} duplicate profiles")
    return merged


def scrape_with_discovery(base_url: str, deep_scrape: bool = False, progress_callback=None) -> List[Dict[str, Any]]:
    """
    Intelligent scraping with automatic profile discovery.
    
    Args:
        base_url: Base URL of the website
        deep_scrape: If True, scrape individual profile pages for more details
        progress_callback: Optional callback function(current, total, message) to report progress
        
    Returns:
        List of profile dictionaries
    """
    logger.info(f"Starting intelligent scrape of: {base_url}")
    
    # Step 1: Find team page
    if progress_callback:
        progress_callback(0, 100, "🔍 Finding team page...")
    
    team_page_url = find_team_page(base_url)
    if not team_page_url:
        logger.warning("Could not find team page, using base URL")
        team_page_url = base_url
    
    # Step 2: Scrape team page
    if progress_callback:
        progress_callback(20, 100, "📋 Scraping team page...")
    
    profiles = scrape_team_page(team_page_url)
    
    # Step 3: If deep scrape enabled, visit individual profile pages
    if deep_scrape and profiles:
        logger.info(f"Deep scraping {len(profiles)} individual profiles...")
        enhanced_profiles = []
        
        for i, profile in enumerate(profiles, 1):
            if progress_callback:
                progress_pct = 20 + int((i / len(profiles)) * 70)  # 20-90%
                progress_callback(progress_pct, 100, f"🕷️ Scraping profile {i}/{len(profiles)}: {profile['name']}")
            
            profile_url = profile.get('profile_url', '')
            if profile_url and profile_url != team_page_url:
                logger.info(f"Scraping profile {i}/{len(profiles)}: {profile['name']}")
                detailed_profile = scrape_individual_profile(profile_url, base_url)
                
                # Merge with existing data
                if detailed_profile:
                    for key, value in detailed_profile.items():
                        if value and not profile.get(key):
                            profile[key] = value
                
                # Rate limiting
                time.sleep(0.5)
            
            enhanced_profiles.append(profile)
        
        profiles = enhanced_profiles
    
    # Step 4: Merge duplicates
    if progress_callback:
        progress_callback(95, 100, "🔄 Merging duplicates...")
    
    profiles = merge_duplicate_profiles(profiles)
    
    if progress_callback:
        progress_callback(100, 100, f"✅ Completed! Found {len(profiles)} profiles")
    
    logger.info(f"✅ Final count: {len(profiles)} unique profiles")
    return profiles


if __name__ == "__main__":
    # Test with Amzur
    url = "https://amzur.com/leadership-team/"
    
    # Basic scrape
    print("\n=== Basic Scrape ===")
    profiles = scrape_team_page(url)
    print(f"Found {len(profiles)} profiles")
    for profile in profiles[:3]:
        print(f"- {profile['name']}: {profile['role']}")
    
    # Intelligent scrape with discovery
    print("\n=== Intelligent Scrape with Discovery ===")
    profiles = scrape_with_discovery("https://amzur.com", deep_scrape=True)
    print(f"Found {len(profiles)} profiles")
    for profile in profiles[:3]:
        print(f"- {profile['name']}: {profile['role']}")
        if profile.get('contact'):
            print(f"  Email: {profile['contact']}")
        if profile.get('linkedin'):
            print(f"  LinkedIn: {profile['linkedin']}")
