"""Diocese manager - discovers and manages diocese and church data"""

import logging
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DioceseScraper:
    """Discovers churches from diocese directory and coordinates scraping"""
    
    # Diocese URL patterns and their configurations
    DIOCESE_CONFIGS = {
        'southern_usa': {
            'url': 'https://suscopts.org',
            'churches_page': '/churches',
            'name': 'Southern USA Diocese',
            'states': ['GA', 'AL', 'FL', 'SC', 'NC', 'TN', 'KY', 'LA', 'MS', 'AR']
        },
        'los_angeles': {
            'url': 'https://lacopts.org',
            'churches_page': '/churches',
            'name': 'Diocese of Los Angeles',
            'states': ['CA']
        },
        'new_york_new_jersey': {
            'url': 'https://dioceseofnynj.org',
            'churches_page': '/churches',
            'name': 'Diocese of New York & New Jersey',
            'states': ['NY', 'NJ', 'PA', 'CT']
        }
    }
    
    def __init__(self, config, location_service):
        self.config = config
        self.location_service = location_service
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('scraping.user_agent', 'CopticServiceEventsBot/1.0')
        })
    
    def detect_diocese_for_location(self, lat: float, lon: float, state: str = None) -> Optional[str]:
        """Detect which diocese covers the user's location"""
        # If state is provided, use it to determine diocese
        if state:
            for diocese_key, diocese_config in self.DIOCESE_CONFIGS.items():
                if state in diocese_config.get('states', []):
                    logger.info(f"Detected diocese: {diocese_config['name']} for state {state}")
                    return diocese_key
        
        # TODO: More sophisticated location-based diocese detection
        # For now, return the first configured diocese
        diocese_urls = self.config.get('data_sources.diocese_websites', {})
        if diocese_urls:
            return list(diocese_urls.keys())[0]
        
        return None
    
    def discover_churches_from_diocese(self, diocese_key: str) -> List[Dict[str, str]]:
        """
        Scrape diocese directory to get list of churches
        Returns: List of church info dicts with name, url, location, etc.
        """
        churches = []
        
        if diocese_key not in self.DIOCESE_CONFIGS:
            logger.warning(f"Unknown diocese: {diocese_key}")
            return churches
        
        diocese_config = self.DIOCESE_CONFIGS[diocese_key]
        diocese_url = diocese_config['url']
        churches_page = diocese_config.get('churches_page', '/churches')
        
        try:
            url = f"{diocese_url}{churches_page}"
            logger.info(f"Discovering churches from {diocese_config['name']}: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse church listings - these patterns may vary by diocese
            churches = self._parse_church_directory(soup, diocese_url, diocese_config['name'])
            
            logger.info(f"Found {len(churches)} churches in {diocese_config['name']}")
            
        except Exception as e:
            logger.error(f"Error discovering churches from {diocese_key}: {e}")
        
        return churches
    
    def _parse_church_directory(self, soup: BeautifulSoup, base_url: str, diocese_name: str) -> List[Dict[str, str]]:
        """Parse church directory HTML - customize based on diocese website structure"""
        churches = []
        
        # Common patterns for church listings
        patterns = [
            # Pattern 1: Churches in a list/table
            {'container': 'div', 'class': 'church-listing'},
            {'container': 'article', 'class': 'church'},
            {'container': 'li', 'class': 'church-item'},
            # Pattern 2: WordPress-style posts
            {'container': 'article', 'class': 'post'},
            # Pattern 3: Generic divs with church data
            {'container': 'div', 'class': lambda x: x and 'church' in str(x).lower()}
        ]
        
        # Try each pattern
        for pattern in patterns:
            containers = soup.find_all(pattern['container'], class_=pattern.get('class'))
            
            if containers:
                logger.info(f"Found {len(containers)} church containers using pattern: {pattern}")
                
                for container in containers:
                    church = self._extract_church_info(container, base_url, diocese_name)
                    if church:
                        churches.append(church)
                
                if churches:
                    break  # Found churches, stop trying patterns
        
        # Fallback: Look for links with "church" or location names
        if not churches:
            churches = self._fallback_church_extraction(soup, base_url, diocese_name)
        
        return churches
    
    def _extract_church_info(self, container, base_url: str, diocese_name: str) -> Optional[Dict[str, str]]:
        """Extract church information from HTML container"""
        try:
            # Try to find church name
            name_elem = container.find(['h1', 'h2', 'h3', 'h4', 'a'])
            if not name_elem:
                return None
            
            church_name = name_elem.get_text().strip()
            
            # Skip if doesn't look like a church
            if not any(word in church_name.lower() for word in ['st.', 'saint', 'church', 'coptic', 'orthodox']):
                return None
            
            # Try to find URL
            link = container.find('a', href=True)
            church_url = None
            if link:
                href = link['href']
                if href.startswith('http'):
                    church_url = href
                elif href.startswith('/'):
                    church_url = f"{base_url}{href}"
                else:
                    church_url = f"{base_url}/{href}"
            
            # Try to find location/address
            location = None
            address_elem = container.find(['address', 'span', 'div'], class_=lambda x: x and any(
                word in str(x).lower() for word in ['address', 'location', 'city']
            ))
            if address_elem:
                location = address_elem.get_text().strip()
            
            # Try to extract city/state from text
            text = container.get_text()
            city, state, zip_code = self._extract_location_from_text(text)
            
            church = {
                'name': church_name,
                'url': church_url,
                'diocese': diocese_name,
                'address': location,
                'city': city,
                'state': state,
                'zip_code': zip_code
            }
            
            logger.debug(f"Extracted church: {church_name}")
            return church
            
        except Exception as e:
            logger.debug(f"Error extracting church info: {e}")
            return None
    
    def _fallback_church_extraction(self, soup: BeautifulSoup, base_url: str, diocese_name: str) -> List[Dict[str, str]]:
        """Fallback method to find churches by looking for links with church names"""
        churches = []
        
        links = soup.find_all('a', href=True)
        for link in links:
            text = link.get_text().strip()
            
            # Check if link text looks like a church name
            if any(word in text.lower() for word in ['st.', 'saint', 'church', 'coptic']):
                href = link['href']
                if href.startswith('http'):
                    church_url = href
                elif href.startswith('/'):
                    church_url = f"{base_url}{href}"
                else:
                    continue
                
                church = {
                    'name': text,
                    'url': church_url,
                    'diocese': diocese_name,
                    'address': None,
                    'city': None,
                    'state': None,
                    'zip_code': None
                }
                churches.append(church)
        
        return churches
    
    def _extract_location_from_text(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract city, state, zip from text using patterns"""
        import re
        
        # Pattern: City, ST ZIP
        pattern = r'([A-Z][a-zA-Z\s]+),\s*([A-Z]{2})\s*(\d{5})'
        match = re.search(pattern, text)
        
        if match:
            return match.group(1).strip(), match.group(2), match.group(3)
        
        # Pattern: Just state
        state_pattern = r'\b([A-Z]{2})\b'
        state_match = re.search(state_pattern, text)
        
        if state_match:
            return None, state_match.group(1), None
        
        return None, None, None
    
    def filter_churches_by_distance(self, churches: List[Dict], user_lat: float, 
                                    user_lon: float, radius_miles: float) -> List[Dict]:
        """Filter churches within radius of user location"""
        filtered = []
        
        for church in churches:
            # Try to geocode church if no coordinates
            if 'latitude' not in church or not church['latitude']:
                # Try to geocode from address or city
                address_parts = []
                if church.get('address'):
                    address_parts.append(church['address'])
                if church.get('city') and church.get('state'):
                    address_parts.append(f"{church['city']}, {church['state']}")
                
                if address_parts:
                    address = ', '.join(address_parts)
                    coords = self.location_service.geocode_address(address)
                    if coords:
                        church['latitude'], church['longitude'] = coords
            
            # Check distance
            if church.get('latitude') and church.get('longitude'):
                distance = self.location_service.calculate_distance(
                    user_lat, user_lon, 
                    church['latitude'], church['longitude']
                )
                church['distance_miles'] = round(distance, 1)
                
                if distance <= radius_miles:
                    filtered.append(church)
            else:
                # Include churches without coordinates (will try to geocode later)
                filtered.append(church)
        
        # Sort by distance
        filtered.sort(key=lambda x: x.get('distance_miles', float('inf')))
        
        return filtered
