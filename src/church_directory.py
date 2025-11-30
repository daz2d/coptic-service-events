"""
Church Directory Scraper
Scrapes global Coptic Orthodox church directories to discover churches
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from src.church_cache import ChurchCache

logger = logging.getLogger(__name__)


class ChurchDirectoryScraper:
    """Scrapes Coptic Orthodox church directories"""
    
    DIRECTORIES = {
        'nihov': {
            'name': 'NIHOV Directory',
            'base_url': 'https://directory.nihov.org',
            'churches_url': 'https://directory.nihov.org/church/all',
            'enabled': True
        },
        'copticchurch_net': {
            'name': 'CopticChurch.net Directory',
            'base_url': 'https://www.copticchurch.net',
            'churches_url': 'https://www.copticchurch.net/directory',
            'enabled': True
        }
    }
    
    def __init__(self, session=None, use_cache=True):
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'CopticServiceEventsBot/1.0'
        })
        self.use_cache = use_cache
        self.cache = ChurchCache() if use_cache else None
    
    def discover_all_churches(self) -> List[Dict]:
        """Discover churches from all enabled directories"""
        all_churches = []
        
        for dir_key, dir_config in self.DIRECTORIES.items():
            if not dir_config.get('enabled', True):
                continue
                
            logger.info(f"Scraping {dir_config['name']}...")
            
            try:
                churches = self._scrape_directory(dir_key, dir_config)
                logger.info(f"Found {len(churches)} churches from {dir_config['name']}")
                all_churches.extend(churches)
            except Exception as e:
                logger.error(f"Error scraping {dir_config['name']}: {e}")
        
        # Deduplicate by name
        unique_churches = self._deduplicate_churches(all_churches)
        logger.info(f"Total unique churches discovered: {len(unique_churches)}")
        
        return unique_churches
    
    def discover_churches_by_radius(self, user_lat: float, user_lon: float, 
                                   radius_miles: float, state: str = None) -> List[Dict]:
        """
        ULTRA OPTIMIZED: Cache church coordinates directly, skip all geocoding on subsequent runs
        """
        from geopy.geocoders import Nominatim
        from geopy.distance import geodesic
        import re
        
        geolocator = Nominatim(user_agent="coptic-events-bot")
        
        # Try to get from cache first
        churches_basic = None
        if self.use_cache and state:
            churches_basic = self.cache.get_churches_for_state(state, max_age_hours=720)  # 30 days
        
        # If not in cache, fetch lightweight list
        if not churches_basic:
            churches_basic = self._scrape_nihov_by_state_lightweight(state) if state else []
        
        # OPTIMIZATION: Only process churches that HAVE websites
        churches_with_websites = [c for c in churches_basic if c.get('url')]
        logger.info(f"🌐 {len(churches_with_websites)}/{len(churches_basic)} churches have websites")
        
        # Extract city from church name for those without it
        for church in churches_with_websites:
            if not church.get('city'):
                city_match = re.search(r'[-\[]([^-\]]+)[\]]?$', church.get('name', ''))
                if city_match:
                    church['city'] = city_match.group(1).strip()
        
        # ULTRA OPTIMIZATION: Check which churches already have coordinates in cache
        churches_needing_geocode = []
        churches_already_geocoded = []
        
        for church in churches_with_websites:
            # Use church name + city as unique key
            church_key = f"{church.get('name', '')}, {church.get('state', '')}"
            
            if church.get('latitude') and church.get('longitude'):
                # Already has coords from cache
                churches_already_geocoded.append(church)
            elif self.use_cache:
                # Check if we've geocoded this church before
                coords = self.cache.get_geocode(church_key)
                if coords:
                    church['latitude'] = coords[0]
                    church['longitude'] = coords[1]
                    churches_already_geocoded.append(church)
                else:
                    churches_needing_geocode.append(church)
            else:
                churches_needing_geocode.append(church)
        
        logger.info(f"📍 {len(churches_already_geocoded)} churches already have coordinates, {len(churches_needing_geocode)} need geocoding")
        
        # Geocode churches that need it (by city to minimize API calls)
        if churches_needing_geocode:
            logger.info(f"🔍 Geocoding {len(churches_needing_geocode)} churches...")
            
            # Group by city for efficient geocoding
            cities_to_geocode = {}
            for church in churches_needing_geocode:
                if church.get('city') and church.get('state'):
                    city_key = f"{church['city']}, {church['state']}"
                    if city_key not in cities_to_geocode:
                        cities_to_geocode[city_key] = []
                    cities_to_geocode[city_key].append(church)
            
            logger.info(f"   Geocoding {len(cities_to_geocode)} unique cities...")
            
            processed = 0
            for city_key, city_churches in cities_to_geocode.items():
                processed += 1
                if processed % 20 == 0:
                    logger.info(f"   Geocoded {processed}/{len(cities_to_geocode)} cities...")
                
                # Check city cache first
                coords = None
                if self.use_cache:
                    coords = self.cache.get_geocode(city_key)
                
                # If not cached, geocode it
                if not coords:
                    try:
                        location = geolocator.geocode(city_key, timeout=10)
                        if location:
                            # Verify this is actually in the correct state
                            address_lower = location.address.lower()
                            state_code = church['state'].upper() if 'state' in church else ''
                            
                            # State validation mapping
                            state_names = {
                                'NJ': ['new jersey', ', nj'],
                                'NY': ['new york', ', ny'],
                                'CT': ['connecticut', ', ct'],
                                'PA': ['pennsylvania', ', pa']
                            }
                            
                            state_found = False
                            if state_code in state_names:
                                for state_variant in state_names[state_code]:
                                    if state_variant in address_lower:
                                        state_found = True
                                        break
                            
                            if state_found:
                                coords = (location.latitude, location.longitude)
                                if self.use_cache:
                                    self.cache.set_geocode(city_key, coords[0], coords[1])
                            else:
                                logger.debug(f"Skipping {city_key} - geocoded to {location.address}, not {state_code}")
                                continue
                    except Exception as e:
                        logger.debug(f"Could not geocode {city_key}: {e}")
                        continue
                
                # Apply coords to all churches in this city AND cache each church
                if coords:
                    for church in city_churches:
                        church['latitude'] = coords[0]
                        church['longitude'] = coords[1]
                        churches_already_geocoded.append(church)
                        
                        # Cache this specific church's coordinates
                        if self.use_cache:
                            church_key = f"{church.get('name', '')}, {church.get('state', '')}"
                            self.cache.set_geocode(church_key, coords[0], coords[1])
        
        # Save cache AND update the state cache with coordinates
        if self.use_cache:
            self.cache._save_cache()
            # Update state cache so next time churches already have coordinates
            self.cache.set_churches_for_state(state, churches_already_geocoded)
        
        # Now filter by distance using ALL geocoded churches
        logger.info(f"📏 Filtering {len(churches_already_geocoded)} geocoded churches by {radius_miles} mile radius...")
        
        churches_in_radius = []
        user_coords = (user_lat, user_lon)
        
        for church in churches_already_geocoded:
            if church.get('latitude') and church.get('longitude'):
                church_coords = (church['latitude'], church['longitude'])
                distance = geodesic(user_coords, church_coords).miles
                
                if distance <= radius_miles:
                    church['distance_miles'] = round(distance, 1)
                    churches_in_radius.append(church)
        
        logger.info(f"✅ Found {len(churches_in_radius)} churches within {radius_miles} miles")
        
        return churches_in_radius
    
    def discover_churches_by_location(self, state: str = None, city: str = None, 
                                      country: str = 'USA') -> List[Dict]:
        """Discover churches filtered by location"""
        
        # If state is provided and country is USA, scrape state-specific page directly
        if state and country == 'USA':
            # Check cache first
            if self.use_cache:
                cached_churches = self.cache.get_churches_for_state(state)
                if cached_churches is not None:
                    logger.info(f"📦 Using cached data for {state}")
                    filtered = cached_churches
                    
                    # Filter by city if provided
                    if city:
                        filtered = [c for c in filtered if city.lower() in (c.get('city') or '').lower()]
                    
                    logger.info(f"Filtered to {len(filtered)} churches in {state}, {country}" + (f" (city: {city})" if city else ""))
                    return filtered
            
            # Not in cache, fetch from directory
            churches = self._scrape_nihov_by_state(state)
            
            # Also check copticchurch.net
            coptic_net_churches = self._scrape_copticchurch_net(self.DIRECTORIES['copticchurch_net'])
            churches.extend(coptic_net_churches)
            
            # Deduplicate
            churches = self._deduplicate_churches(churches)
            
            # Filter by state
            filtered = [c for c in churches if (c.get('state') or '').upper() == state.upper()]
            
            # Cache the results
            if self.use_cache:
                self.cache.set_churches_for_state(state, filtered)
            
            # Filter by city if provided
            if city:
                filtered = [c for c in filtered if city.lower() in (c.get('city') or '').lower()]
            
            logger.info(f"Filtered to {len(filtered)} churches in {state}, {country}" + (f" (city: {city})" if city else ""))
            return filtered
        
        # Otherwise, discover all and filter
        all_churches = self.discover_all_churches()
        
        filtered = []
        for church in all_churches:
            # Filter by country
            if country and (church.get('country') or '').upper() != country.upper():
                continue
            
            # Filter by state
            if state and (church.get('state') or '').upper() != state.upper():
                continue
            
            # Filter by city
            if city and city.lower() not in (church.get('city') or '').lower():
                continue
            
            filtered.append(church)
        
        logger.info(f"Filtered to {len(filtered)} churches for location: {state or 'any state'}, {country}" + (f" (city: {city})" if city else ""))
        return filtered
    
    def _scrape_nihov_by_state(self, state: str) -> List[Dict]:
        """Scrape NIHOV directory for a specific US state"""
        churches = []
        
        try:
            # NIHOV has state-specific URLs: /church/usa/[state_name]
            state_name = self._get_state_name(state)
            
            if not state_name:
                logger.warning(f"Unknown state code: {state}")
                return churches
            
            url = f"https://directory.nihov.org/church/usa/{state_name.lower()}"
            logger.info(f"Scraping NIHOV state page: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all church links
            links = soup.find_all('a', href=re.compile(r'/church/\d+'))
            
            logger.info(f"Found {len(links)} churches in {state_name}")
            logger.info(f"Extracting contact details from church pages (this may take a moment)...")
            
            # Process churches in batches for progress updates
            batch_size = 50
            for i in range(0, len(links), batch_size):
                batch = links[i:i+batch_size]
                
                for link in batch:
                    church_name = link.get_text().strip()
                    
                    if not church_name or len(church_name) < 3:
                        continue
                    
                    # Extract city from name (format: "Church Name - City" or "Church Name [City]")
                    city_match = re.search(r'[-\[]([^-\]]+)[\]]?$', church_name)
                    city = city_match.group(1).strip() if city_match else None
                    
                    # Get detail page for website URL and social media
                    detail_url = 'https://directory.nihov.org' + link['href']
                    contact_info = self._get_church_contact_from_detail(detail_url)
                    
                    church = {
                        'name': church_name,
                        'url': contact_info.get('website'),
                        'facebook': contact_info.get('facebook'),
                        'instagram': contact_info.get('instagram'),
                        'email': contact_info.get('email'),
                        'phone': contact_info.get('phone'),
                        'directory_url': detail_url,
                        'source': 'NIHOV Directory',
                        'city': city,
                        'state': state.upper(),
                        'country': 'USA'
                    }
                    churches.append(church)
                
                if i + batch_size < len(links):
                    logger.info(f"Processed {i + batch_size}/{len(links)} churches...")
                    
        except Exception as e:
            logger.error(f"Error scraping NIHOV state page for {state}: {e}")
        
        return churches
    
    def _scrape_nihov_by_state_lightweight(self, state: str) -> List[Dict]:
        """
        OPTIMIZED: Scrape NIHOV for church names and cities ONLY (no website URLs yet)
        This is much faster - we'll fetch URLs only for churches within radius
        """
        churches = []
        
        try:
            state_name = self._get_state_name(state)
            
            if not state_name:
                logger.warning(f"Unknown state code: {state}")
                return churches
            
            url = f"https://directory.nihov.org/church/usa/{state_name.lower()}"
            logger.info(f"📋 Fetching church list for {state_name}...")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=re.compile(r'/church/\d+'))
            
            # Deduplicate by href
            seen_hrefs = set()
            unique_links = []
            for link in links:
                href = link['href']
                if href not in seen_hrefs:
                    seen_hrefs.add(href)
                    unique_links.append(link)
            
            logger.info(f"Found {len(unique_links)} unique churches in {state_name}")
            
            for link in unique_links:
                church_name = link.get_text().strip()
                
                if not church_name or len(church_name) < 3:
                    continue
                
                # Extract city from name (format: "Church Name - City" or "Church Name [City]")
                city_match = re.search(r'[-\[]([^-\]]+)[\]]?$', church_name)
                city = city_match.group(1).strip() if city_match else None
                
                detail_url = 'https://directory.nihov.org' + link['href']
                
                church = {
                    'name': church_name,
                    'directory_url': detail_url,
                    'source': 'NIHOV Directory',
                    'city': city,
                    'state': state.upper(),
                    'country': 'USA'
                }
                churches.append(church)
                    
        except Exception as e:
            logger.error(f"Error scraping NIHOV state page for {state}: {e}")
        
        return churches
    
    def _get_church_contact_from_detail(self, detail_url: str) -> Dict[str, Optional[str]]:
        """Visit church detail page XML API to extract all contact information"""
        contact_info = {
            'website': None,
            'facebook': None,
            'instagram': None,
            'email': None,
            'phone': None
        }
        
        try:
            # Extract church ID from URL: /church/267 -> 267
            church_id_match = re.search(r'/church/(\d+)', detail_url)
            if not church_id_match:
                return contact_info
            
            church_id = church_id_match.group(1)
            
            # Check cache first
            if self.use_cache:
                cached_contact = self.cache.get_church_contact(church_id)
                if cached_contact is not None:
                    return cached_contact
            
            # Fetch XML data for this church
            xml_url = f"https://directory.nihov.org/report/map_xml.php?church_id={church_id}"
            response = self.session.get(xml_url, timeout=10)
            
            # Parse XML
            soup = BeautifulSoup(response.content, 'xml')
            marker = soup.find('marker')
            
            if marker:
                # Get website
                website = marker.get('website')
                if website and website.strip():
                    contact_info['website'] = website.strip()
                
                # Get phone
                phone = marker.get('phone')
                if phone and phone.strip():
                    contact_info['phone'] = phone.strip()
            
            # Cache the result
            if self.use_cache:
                self.cache.set_church_contact(church_id, contact_info)
                
        except Exception as e:
            logger.debug(f"Could not get contact info from XML for {detail_url}: {e}")
        
        return contact_info
    
    def _get_state_name(self, state_code: str) -> Optional[str]:
        """Convert state code to full name for URL"""
        state_names = {
            'AL': 'alabama', 'AK': 'alaska', 'AZ': 'arizona', 'AR': 'arkansas',
            'CA': 'california', 'CO': 'colorado', 'CT': 'connecticut', 'DE': 'delaware',
            'FL': 'florida', 'GA': 'georgia', 'HI': 'hawaii', 'ID': 'idaho',
            'IL': 'illinois', 'IN': 'indiana', 'IA': 'iowa', 'KS': 'kansas',
            'KY': 'kentucky', 'LA': 'louisiana', 'ME': 'maine', 'MD': 'maryland',
            'MA': 'massachusetts', 'MI': 'michigan', 'MN': 'minnesota', 'MS': 'mississippi',
            'MO': 'missouri', 'MT': 'montana', 'NE': 'nebraska', 'NV': 'nevada',
            'NH': 'new-hampshire', 'NJ': 'new-jersey', 'NM': 'new-mexico', 'NY': 'new-york',
            'NC': 'north-carolina', 'ND': 'north-dakota', 'OH': 'ohio', 'OK': 'oklahoma',
            'OR': 'oregon', 'PA': 'pennsylvania', 'RI': 'rhode-island', 'SC': 'south-carolina',
            'SD': 'south-dakota', 'TN': 'tennessee', 'TX': 'texas', 'UT': 'utah',
            'VT': 'vermont', 'VA': 'virginia', 'WA': 'washington', 'WV': 'west-virginia',
            'WI': 'wisconsin', 'WY': 'wyoming'
        }
        return state_names.get(state_code.upper())
    
    def _scrape_directory(self, dir_key: str, dir_config: Dict) -> List[Dict]:
        """Scrape a specific directory"""
        if dir_key == 'nihov':
            return self._scrape_nihov(dir_config)
        elif dir_key == 'copticchurch_net':
            return self._scrape_copticchurch_net(dir_config)
        else:
            return []
    
    def _scrape_nihov(self, config: Dict) -> List[Dict]:
        """Scrape directory.nihov.org"""
        churches = []
        
        try:
            # The directory has state-specific pages at /church/usa/[state]
            # For now, scrape the main page which lists all churches
            url = config['churches_url']
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all church links - they follow pattern /church/[number]
            links = soup.find_all('a', href=re.compile(r'/church/\d+'))
            
            logger.info(f"Found {len(links)} church links")
            
            for link in links:
                church_name = link.get_text().strip()
                church_detail_url = config['base_url'] + link['href']
                
                if not church_name or len(church_name) < 3:
                    continue
                
                # Extract state and city from the text if present
                # Format is often: "Church Name, City, ST"
                location_match = re.search(r',\s*([^,]+),\s*([A-Z]{2})', church_name)
                
                if location_match:
                    city = location_match.group(1).strip()
                    state = location_match.group(2)
                    # Remove location from name
                    church_name_clean = church_name[:location_match.start()].strip()
                else:
                    city = None
                    state = None
                    church_name_clean = church_name
                
                church = {
                    'name': church_name,
                    'url': None,  # Will need to visit detail page to get URL
                    'directory_url': church_detail_url,
                    'source': 'NIHOV Directory',
                    'city': city,
                    'state': state,
                    'country': 'USA' if state else None
                }
                churches.append(church)
                
        except Exception as e:
            logger.error(f"Error scraping NIHOV: {e}")
        
        return churches
    
    def _scrape_copticchurch_net(self, config: Dict) -> List[Dict]:
        """Scrape www.copticchurch.net/directory"""
        churches = []
        
        try:
            url = config['churches_url']
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find church links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Skip if not a church link
                if not text or len(text) < 5:
                    continue
                
                # Look for church indicators
                if any(word in text.lower() for word in ['st.', 'saint', 'church', 'coptic']):
                    # Extract location from text if present
                    location_match = re.search(r',\s*([A-Z]{2})', text)
                    state = location_match.group(1) if location_match else None
                    
                    city_match = re.search(r',\s*([^,]+),\s*[A-Z]{2}', text)
                    city = city_match.group(1).strip() if city_match else None
                    
                    # Check if href is an external URL (church website)
                    church_url = None
                    if href.startswith('http'):
                        church_url = href
                    
                    church = {
                        'name': text,
                        'url': church_url,
                        'source': 'CopticChurch.net Directory',
                        'city': city,
                        'state': state,
                        'country': 'USA' if state else None
                    }
                    churches.append(church)
                    
        except Exception as e:
            logger.error(f"Error scraping CopticChurch.net: {e}")
        
        return churches
    
    def _parse_nihov_church(self, element, base_url: str) -> Optional[Dict]:
        """Parse church info from NIHOV element"""
        try:
            # Extract church name
            name_elem = element.find(['h3', 'h4', 'a']) or element
            name = name_elem.get_text().strip()
            
            # Extract location if present
            location_text = element.get_text()
            
            # Try to find state (2-letter code)
            state_match = re.search(r'\b([A-Z]{2})\b', location_text)
            state = state_match.group(1) if state_match else None
            
            # Try to find city
            city_match = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})', location_text)
            city = city_match.group(1).strip() if city_match else None
            
            # Try to find website URL
            url_link = element.find('a', href=re.compile(r'^http'))
            church_url = url_link['href'] if url_link else None
            
            return {
                'name': name,
                'url': church_url,
                'source': 'NIHOV Directory',
                'city': city,
                'state': state,
                'country': 'USA' if state else None
            }
            
        except Exception as e:
            logger.debug(f"Error parsing NIHOV element: {e}")
            return None
    
    def _deduplicate_churches(self, churches: List[Dict]) -> List[Dict]:
        """Remove duplicate churches based on name"""
        seen = set()
        unique = []
        
        for church in churches:
            # Create a normalized key for comparison
            key = church['name'].lower().strip()
            key = re.sub(r'\s+', ' ', key)  # Normalize whitespace
            
            if key not in seen:
                seen.add(key)
                unique.append(church)
        
        return unique
    
    def get_churches_with_websites(self, churches: List[Dict]) -> List[Dict]:
        """Filter to churches that have website URLs or social media"""
        return [c for c in churches if c.get('url') or c.get('facebook') or c.get('instagram')]


if __name__ == '__main__':
    # Test the scraper
    logging.basicConfig(level=logging.INFO)
    
    scraper = ChurchDirectoryScraper()
    
    print("\n" + "="*60)
    print("DISCOVERING ALL COPTIC ORTHODOX CHURCHES")
    print("="*60 + "\n")
    
    # Discover all churches
    churches = scraper.discover_all_churches()
    
    print(f"\nTotal churches found: {len(churches)}")
    
    # Show churches with websites
    with_websites = scraper.get_churches_with_websites(churches)
    print(f"Churches with websites: {len(with_websites)}")
    
    # Show first 10
    print("\nFirst 10 churches with websites:")
    for i, church in enumerate(with_websites[:10], 1):
        print(f"\n{i}. {church['name']}")
        print(f"   URL: {church['url']}")
        print(f"   Location: {church.get('city', 'N/A')}, {church.get('state', 'N/A')}")
    
    # Test location filtering
    print("\n" + "="*60)
    print("CHURCHES IN NEW JERSEY")
    print("="*60 + "\n")
    
    nj_churches = scraper.discover_churches_by_location(state='NJ')
    print(f"Found {len(nj_churches)} churches in NJ")
    
    for i, church in enumerate(nj_churches[:5], 1):
        print(f"\n{i}. {church['name']}")
        if church.get('url'):
            print(f"   Website: {church['url']}")
        print(f"   City: {church.get('city', 'N/A')}")
