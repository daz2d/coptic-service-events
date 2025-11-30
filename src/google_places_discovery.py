"""
Google Places API Church Discovery
One-time population of high-quality church data from Google Maps
"""

import os
import logging
import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if using system env vars

logger = logging.getLogger(__name__)


@dataclass
class GooglePlaceChurch:
    """Church data from Google Places"""
    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    opening_hours: Optional[Dict] = None
    photos: Optional[List[str]] = None
    vicinity: Optional[str] = None


class GooglePlacesChurchDiscovery:
    """Discover Coptic Orthodox churches using Google Places API"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize with Google Places API key
        
        Get your API key from:
        https://console.cloud.google.com/google/maps-apis/credentials
        
        Enable: Places API (New)
        """
        # Try multiple environment variable names
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY') or os.getenv('GOOGLE_MAPS_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Google Places API key required. Set GOOGLE_PLACES_API_KEY or GOOGLE_MAPS_API_KEY "
                "environment variable or pass api_key parameter. Get one at: "
                "https://console.cloud.google.com/google/maps-apis/credentials"
            )
        
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def search_churches_in_state(self, state: str, max_results: int = 60) -> List[GooglePlaceChurch]:
        """
        Search for all Coptic Orthodox churches in a state
        
        Args:
            state: State abbreviation (e.g., 'NJ', 'NY')
            max_results: Maximum churches to return (default 60)
            
        Returns:
            List of GooglePlaceChurch objects with verified data
        """
        state_names = {
            'NJ': 'New Jersey',
            'NY': 'New York',
            'CT': 'Connecticut',
            'PA': 'Pennsylvania'
        }
        
        state_full = state_names.get(state.upper(), state)
        
        logger.info(f"🔍 Searching Google Places for Coptic Orthodox churches in {state_full}...")
        
        # Use Text Search API
        churches = []
        
        # Multiple search queries to catch all churches
        queries = [
            f"Coptic Orthodox Church in {state_full}",
            f"Coptic Church {state_full}",
            f"St. Mary Coptic Church {state_full}",
            f"St. Mark Coptic Church {state_full}",
        ]
        
        seen_place_ids = set()
        
        for query in queries:
            results = self._text_search(query)
            
            for place in results:
                place_id = place.get('place_id')
                
                if place_id in seen_place_ids:
                    continue
                    
                seen_place_ids.add(place_id)
                
                # Get detailed information
                details = self._get_place_details(place_id)
                
                if details:
                    church = self._parse_church_data(details)
                    if church:
                        churches.append(church)
                        logger.info(f"   ✓ Found: {church.name}")
                        
                        if len(churches) >= max_results:
                            break
                
                # Rate limiting - be nice to Google
                time.sleep(0.2)
            
            if len(churches) >= max_results:
                break
        
        logger.info(f"✅ Found {len(churches)} Coptic Orthodox churches in {state_full}")
        
        return churches
    
    def search_churches_near_location(self, lat: float, lon: float, 
                                     radius_miles: int = 15) -> List[GooglePlaceChurch]:
        """
        Search for Coptic Orthodox churches near a location
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_miles: Search radius in miles
            
        Returns:
            List of GooglePlaceChurch objects
        """
        radius_meters = int(radius_miles * 1609.34)  # Convert miles to meters
        
        logger.info(f"🔍 Searching Google Places within {radius_miles} miles of ({lat}, {lon})...")
        
        url = f"{self.base_url}/nearbysearch/json"
        
        params = {
            'location': f"{lat},{lon}",
            'radius': radius_meters,
            'keyword': 'Coptic Orthodox Church',
            'key': self.api_key
        }
        
        churches = []
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'OK':
                for place in data.get('results', []):
                    place_id = place.get('place_id')
                    
                    # Get detailed information
                    details = self._get_place_details(place_id)
                    
                    if details:
                        church = self._parse_church_data(details)
                        if church:
                            churches.append(church)
                            logger.info(f"   ✓ Found: {church.name}")
                    
                    time.sleep(0.2)  # Rate limiting
            
            logger.info(f"✅ Found {len(churches)} churches")
            
        except Exception as e:
            logger.error(f"Error searching nearby: {e}")
        
        return churches
    
    def _text_search(self, query: str) -> List[Dict]:
        """Perform a text search"""
        url = f"{self.base_url}/textsearch/json"
        
        params = {
            'query': query,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'OK':
                return data.get('results', [])
            elif data.get('status') == 'ZERO_RESULTS':
                logger.debug(f"No results for: {query}")
                return []
            else:
                logger.warning(f"Search returned status: {data.get('status')}")
                return []
                
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return []
    
    def _get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a place"""
        url = f"{self.base_url}/details/json"
        
        fields = [
            'place_id', 'name', 'formatted_address', 'geometry',
            'formatted_phone_number', 'website', 'rating',
            'user_ratings_total', 'opening_hours', 'photos', 'vicinity',
            'address_components', 'types', 'business_status', 'url',
            'international_phone_number'
        ]
        
        params = {
            'place_id': place_id,
            'fields': ','.join(fields),
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'OK':
                return data.get('result')
            else:
                logger.warning(f"Place details returned status: {data.get('status')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting place details: {e}")
            return None
    
    def _parse_church_data(self, details: Dict) -> Optional[GooglePlaceChurch]:
        """Parse Google Place details into GooglePlaceChurch object"""
        try:
            location = details.get('geometry', {}).get('location', {})
            
            # Extract address components
            address_components = details.get('address_components', [])
            city = None
            state = None
            country = None
            postal_code = None
            
            for component in address_components:
                types = component.get('types', [])
                if 'locality' in types:
                    city = component.get('long_name')
                elif 'administrative_area_level_1' in types:
                    state = component.get('short_name')
                elif 'country' in types:
                    country = component.get('long_name')
                elif 'postal_code' in types:
                    postal_code = component.get('long_name')
            
            church = GooglePlaceChurch(
                place_id=details.get('place_id'),
                name=details.get('name'),
                address=details.get('formatted_address'),
                latitude=location.get('lat'),
                longitude=location.get('lng'),
                phone=details.get('formatted_phone_number') or details.get('international_phone_number'),
                website=details.get('website'),
                rating=details.get('rating'),
                user_ratings_total=details.get('user_ratings_total'),
                opening_hours=details.get('opening_hours'),
                photos=details.get('photos'),
                vicinity=details.get('vicinity')
            )
            
            # Add parsed address components as attributes
            church.city = city
            church.state = state
            church.country = country
            church.postal_code = postal_code
            church.types = ','.join(details.get('types', []))
            church.business_status = details.get('business_status')
            church.google_maps_url = details.get('url')
            
            return church
            
        except Exception as e:
            logger.error(f"Error parsing church data: {e}")
            return None
    
    def save_to_database(self, churches: List[GooglePlaceChurch], db_path: str = 'coptic_events.db'):
        """
        Save discovered churches to SQLite database
        
        Creates a new table: google_places_churches
        """
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table with enhanced fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS google_places_churches (
                place_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT,
                latitude REAL,
                longitude REAL,
                phone TEXT,
                website TEXT,
                email TEXT,
                rating REAL,
                user_ratings_total INTEGER,
                opening_hours TEXT,
                vicinity TEXT,
                city TEXT,
                state TEXT,
                country TEXT,
                postal_code TEXT,
                types TEXT,
                business_status TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert churches with enhanced data
        for church in churches:
            cursor.execute("""
                INSERT OR REPLACE INTO google_places_churches
                (place_id, name, address, latitude, longitude, phone, website, 
                 rating, user_ratings_total, vicinity, city, state, country, 
                 postal_code, types, business_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                church.place_id,
                church.name,
                church.address,
                church.latitude,
                church.longitude,
                church.phone,
                church.website,
                church.rating,
                church.user_ratings_total,
                church.vicinity,
                getattr(church, 'city', None),
                getattr(church, 'state', None),
                getattr(church, 'country', None),
                getattr(church, 'postal_code', None),
                getattr(church, 'types', None),
                getattr(church, 'business_status', None)
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"💾 Saved {len(churches)} churches to database")


if __name__ == "__main__":
    """
    One-time script to populate church database from Google Places
    
    Usage:
        1. Get API key from: https://console.cloud.google.com/google/maps-apis/credentials
        2. Set environment variable: export GOOGLE_PLACES_API_KEY="your-key"
        3. Run: python -m src.google_places_discovery
    """
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Check for API key (try multiple names)
    api_key = os.getenv('GOOGLE_PLACES_API_KEY') or os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        print("\n❌ ERROR: Google Maps API key not found in environment")
        print("\n📝 To get your API key:")
        print("1. Go to: https://console.cloud.google.com/google/maps-apis/credentials")
        print("2. Create a new API key")
        print("3. Enable 'Places API (New)'")
        print("4. Add to .env file: GOOGLE_MAPS_API_KEY='your-key'")
        print("\n💰 Pricing: $200 free credit/month (6,000 searches)")
        print("   For NJ churches: ~60 searches = FREE\n")
        exit(1)
    
    # Discover churches
    discovery = GooglePlacesChurchDiscovery(api_key)
    
    # Search NJ
    nj_churches = discovery.search_churches_in_state('NJ', max_results=100)
    
    # Save to database
    discovery.save_to_database(nj_churches)
    
    print(f"\n✅ SUCCESS! Discovered {len(nj_churches)} Coptic Orthodox churches in NJ")
    print(f"💾 Saved to database: coptic_events.db (table: google_places_churches)")
    print(f"\n📊 Sample churches:")
    
    for i, church in enumerate(nj_churches[:5], 1):
        print(f"\n{i}. {church.name}")
        print(f"   📍 {church.address}")
        print(f"   📞 {church.phone or 'No phone'}")
        print(f"   🌐 {church.website or 'No website'}")
        if church.rating:
            print(f"   ⭐ {church.rating}/5 ({church.user_ratings_total} reviews)")
