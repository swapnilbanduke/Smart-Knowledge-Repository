"""
Intelligent Profile Extractor
Multi-template content extraction with automatic pattern detection
"""

import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup, Tag
import logging

logger = logging.getLogger(__name__)


class ProfileExtractor:
    """Intelligent profile data extractor with multiple extraction strategies."""
    
    # Contact patterns
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
    LINKEDIN_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+/?')
    TWITTER_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?(?:twitter|x)\.com/[\w]+/?')
    
    def __init__(self):
        self.extraction_stats = {
            'total_profiles': 0,
            'emails_found': 0,
            'phones_found': 0,
            'photos_found': 0,
            'bios_found': 0
        }
    
    def extract_profile(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """
        Extract profile using multiple strategies.
        Tries various selectors and patterns to handle different website layouts.
        """
        profile = {
            'name': self._extract_name(soup),
            'role': self._extract_role(soup),
            'bio': self._extract_bio(soup),
            'contact': self._extract_email(soup),
            'phone': self._extract_phone(soup),
            'linkedin': self._extract_linkedin(soup),
            'twitter': self._extract_twitter(soup),
            'photo_url': self._extract_photo(soup, base_url),
            'department': self._extract_department(soup)
        }
        
        self._update_stats(profile)
        return profile
    
    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract name using multiple strategies."""
        # Strategy 1: Common name selectors
        selectors = [
            'h1.name', 'h1.profile-name', 'h1.person-name',
            '.name h1', '.profile-name h1', 
            'h1[class*="name"]', 'h1[class*="person"]',
            'h1', 'h2.name', '.name', '.profile-header h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text(strip=True)
                if self._is_valid_name(name):
                    return name
        
        # Strategy 2: Schema.org markup
        schema_name = soup.find(attrs={'itemprop': 'name'})
        if schema_name:
            return schema_name.get_text(strip=True)
        
        # Strategy 3: Meta tags
        meta_name = soup.find('meta', attrs={'name': 'author'}) or \
                    soup.find('meta', attrs={'property': 'profile:username'})
        if meta_name:
            return meta_name.get('content', '').strip()
        
        return None
    
    def _extract_role(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract job title/role using multiple strategies."""
        # Strategy 1: Common role selectors
        selectors = [
            '.title', '.job-title', '.position', '.role',
            'h2.title', 'h3.title', '.profile-title',
            '[class*="title"]', '[class*="position"]', '[class*="role"]',
            'p.title', 'span.title', 'div.title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                role = element.get_text(strip=True)
                if self._is_valid_role(role):
                    return role
        
        # Strategy 2: Schema.org
        schema_role = soup.find(attrs={'itemprop': 'jobTitle'})
        if schema_role:
            return schema_role.get_text(strip=True)
        
        # Strategy 3: Look for common role keywords after name
        role_keywords = ['CEO', 'CTO', 'CFO', 'Director', 'Manager', 'Engineer', 
                        'Developer', 'Designer', 'Analyst', 'Lead', 'Head', 'VP']
        for keyword in role_keywords:
            pattern = re.compile(rf'\b{keyword}\b', re.IGNORECASE)
            match = soup.find(string=pattern)
            if match:
                return match.strip()
        
        return None
    
    def _extract_bio(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract biography/description using multiple strategies."""
        # Strategy 1: Common bio selectors
        selectors = [
            '.bio', '.biography', '.description', '.about',
            'p.bio', 'div.bio', '.profile-bio', '.profile-description',
            '[class*="bio"]', '[class*="description"]', '[class*="about"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                bio = element.get_text(strip=True)
                if len(bio) > 20:  # Minimum bio length
                    return self._clean_bio(bio)
        
        # Strategy 2: Schema.org
        schema_bio = soup.find(attrs={'itemprop': 'description'})
        if schema_bio:
            bio = schema_bio.get_text(strip=True)
            if len(bio) > 20:
                return self._clean_bio(bio)
        
        # Strategy 3: Find longest paragraph
        paragraphs = soup.find_all('p')
        longest_p = max(paragraphs, key=lambda p: len(p.get_text(strip=True)), default=None)
        if longest_p:
            bio = longest_p.get_text(strip=True)
            if len(bio) > 50:
                return self._clean_bio(bio)
        
        return None
    
    def _extract_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract email with validation."""
        # Strategy 1: Mailto links
        mailto = soup.find('a', href=re.compile(r'^mailto:'))
        if mailto:
            email = mailto.get('href', '').replace('mailto:', '').strip()
            if self._is_valid_email(email):
                return email
        
        # Strategy 2: Email pattern in text
        text = soup.get_text()
        emails = self.EMAIL_PATTERN.findall(text)
        for email in emails:
            if self._is_valid_email(email):
                return email
        
        # Strategy 3: Schema.org
        schema_email = soup.find(attrs={'itemprop': 'email'})
        if schema_email:
            email = schema_email.get_text(strip=True)
            if self._is_valid_email(email):
                return email
        
        return None
    
    def _extract_phone(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract phone number with formatting."""
        # Strategy 1: Tel links
        tel_link = soup.find('a', href=re.compile(r'^tel:'))
        if tel_link:
            phone = tel_link.get('href', '').replace('tel:', '').strip()
            return self._format_phone(phone)
        
        # Strategy 2: Phone pattern in text
        text = soup.get_text()
        phones = self.PHONE_PATTERN.findall(text)
        if phones:
            # Format as (XXX) XXX-XXXX
            return f"({phones[0][0]}) {phones[0][1]}-{phones[0][2]}"
        
        # Strategy 3: Schema.org
        schema_phone = soup.find(attrs={'itemprop': 'telephone'})
        if schema_phone:
            return self._format_phone(schema_phone.get_text(strip=True))
        
        return None
    
    def _extract_linkedin(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract LinkedIn profile URL."""
        # Look for LinkedIn links
        linkedin_link = soup.find('a', href=self.LINKEDIN_PATTERN)
        if linkedin_link:
            return linkedin_link.get('href', '').strip()
        
        # Search in text
        text = soup.get_text()
        match = self.LINKEDIN_PATTERN.search(text)
        if match:
            return match.group(0)
        
        return None
    
    def _extract_twitter(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract Twitter/X profile URL."""
        # Look for Twitter links
        twitter_link = soup.find('a', href=self.TWITTER_PATTERN)
        if twitter_link:
            return twitter_link.get('href', '').strip()
        
        # Search in text
        text = soup.get_text()
        match = self.TWITTER_PATTERN.search(text)
        if match:
            return match.group(0)
        
        return None
    
    def _extract_photo(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract profile photo with quality scoring."""
        from urllib.parse import urljoin
        
        photo_candidates = []
        
        # Strategy 1: Common photo selectors
        selectors = [
            'img.profile-photo', 'img.profile-image', 'img.headshot',
            'img.avatar', '.profile-photo img', '.profile-image img',
            '[class*="photo"] img', '[class*="image"] img', '[class*="avatar"] img'
        ]
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                url = urljoin(base_url, img['src'])
                photo_candidates.append({'url': url, 'score': 10})
        
        # Strategy 2: Schema.org
        schema_img = soup.find('img', attrs={'itemprop': 'image'})
        if schema_img and schema_img.get('src'):
            url = urljoin(base_url, schema_img['src'])
            photo_candidates.append({'url': url, 'score': 9})
        
        # Strategy 3: Largest image
        all_images = soup.find_all('img')
        for img in all_images:
            if not img.get('src'):
                continue
            
            url = urljoin(base_url, img['src'])
            
            # Skip icons, logos, and small images
            if any(skip in url.lower() for skip in ['icon', 'logo', 'sprite', 'banner']):
                continue
            
            # Score based on attributes
            score = 0
            alt = img.get('alt', '').lower()
            if any(kw in alt for kw in ['photo', 'profile', 'headshot', 'avatar']):
                score += 5
            
            width = img.get('width', '0')
            if width.isdigit() and int(width) > 100:
                score += 3
            
            if score > 0:
                photo_candidates.append({'url': url, 'score': score})
        
        # Return highest scoring photo
        if photo_candidates:
            best_photo = max(photo_candidates, key=lambda x: x['score'])
            return best_photo['url']
        
        return None
    
    def _extract_department(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract department/team information."""
        selectors = [
            '.department', '.team', '.division',
            '[class*="department"]', '[class*="team"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                dept = element.get_text(strip=True)
                if dept:
                    return dept
        
        # Look for department keywords
        dept_keywords = ['Engineering', 'Sales', 'Marketing', 'Product', 'Design', 
                        'Operations', 'Finance', 'HR', 'Legal', 'Executive']
        text = soup.get_text()
        for keyword in dept_keywords:
            if keyword in text:
                return keyword
        
        return None
    
    # Validation helpers
    def _is_valid_name(self, name: str) -> bool:
        """Check if string is a valid person name."""
        if not name or len(name) < 3:
            return False
        
        # Must have at least 2 words
        words = name.split()
        if len(words) < 2:
            return False
        
        # Skip if contains numbers or special chars
        if re.search(r'[0-9@#$%]', name):
            return False
        
        return True
    
    def _is_valid_role(self, role: str) -> bool:
        """Check if string is a valid job title."""
        if not role or len(role) < 3:
            return False
        
        # Skip if it's a URL or email
        if '@' in role or 'http' in role:
            return False
        
        return True
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email address."""
        if not email:
            return False
        
        # Check against pattern
        if not self.EMAIL_PATTERN.match(email):
            return False
        
        # Skip common non-email patterns
        skip_patterns = ['example.com', 'test.com', 'domain.com']
        if any(pattern in email.lower() for pattern in skip_patterns):
            return False
        
        return True
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number consistently."""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Format as (XXX) XXX-XXXX for 10-digit US numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        
        return phone
    
    def _clean_bio(self, bio: str) -> str:
        """Clean and normalize biography text."""
        # Remove extra whitespace
        bio = ' '.join(bio.split())
        
        # Truncate if too long
        if len(bio) > 1000:
            bio = bio[:997] + '...'
        
        return bio
    
    def _update_stats(self, profile: Dict[str, Any]):
        """Update extraction statistics."""
        self.extraction_stats['total_profiles'] += 1
        if profile.get('contact'):
            self.extraction_stats['emails_found'] += 1
        if profile.get('phone'):
            self.extraction_stats['phones_found'] += 1
        if profile.get('photo_url'):
            self.extraction_stats['photos_found'] += 1
        if profile.get('bio'):
            self.extraction_stats['bios_found'] += 1
    
    def get_stats(self) -> Dict[str, int]:
        """Get extraction statistics."""
        return self.extraction_stats.copy()
