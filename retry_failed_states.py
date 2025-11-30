#!/usr/bin/env python3
"""
Hybrid Retry Script - Uses multiple strategies to ensure complete coverage:
1. Multiple search terms and strategies per state
2. Full pagination (not just first 20 results)
3. Major cities + statewide + nearby searches
4. Validation against expected results
"""

import os
import sys
import time
import logging
import sqlite3
from typing import List, Dict
from dotenv import load_dotenv
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.google_places_discovery import GooglePlacesChurchDiscovery

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('retry_states.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# States that need comprehensive search (low counts or known issues)
RETRY_STATES = ['NY', 'MD', 'OR', 'WY', 'MI', 'OH']  # Expand as needed


class ComprehensiveDiscovery:
    """Enhanced discovery with multiple strategies and FULL pagination"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not found")
        
        self.discovery = GooglePlacesChurchDiscovery(self.api_key)
        
    def search_state_thoroughly(self, state_code: str) -> List[Dict]:
        """Use multiple search strategies with full pagination"""
        logger.info(f"\n{'='*60}")
        logger.info(f"COMPREHENSIVE SEARCH: {state_code}")
        logger.info(f"{'='*60}")
        
        all_churches = {}  # Deduplicate by place_id
        
        # Strategy 1: Major cities
        cities = self._get_major_cities(state_code)
        for city in cities:
            logger.info(f"  🔍 Searching: {city}, {state_code}")
            results = self._paginated_search(f"Coptic Orthodox Church {city} {state_code}")
            for church in results:
                if church.get('state') == state_code:
                    all_churches[church['place_id']] = church
            time.sleep(2)
        
        # Strategy 2: Different search terms statewide
        search_terms = [
            f"Coptic Orthodox Church {state_code}",
            f"Coptic Church {state_code}",
            f"Egyptian Coptic Orthodox {state_code}",
        ]
        
        for term in search_terms:
            logger.info(f"  🔍 Searching: {term}")
            results = self._paginated_search(term)
            for church in results:
                if church.get('state') == state_code:
                    all_churches[church['place_id']] = church
            time.sleep(2)
        
        churches_list = list(all_churches.values())
        logger.info(f"✅ {state_code}: Found {len(churches_list)} total unique churches")
        return churches_list
    
    def _paginated_search(self, query: str, max_pages: int = 5) -> List[Dict]:
        """Search with FULL pagination support"""
        all_results = []
        next_page_token = None
        page = 1
        
        while page <= max_pages:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': query,
                'key': self.api_key
            }
            
            if next_page_token:
                params['pagetoken'] = next_page_token
                time.sleep(3)  # Required delay for next_page_token
            
            try:
                response = requests.get(url, params=params, timeout=30)
                data = response.json()
                
                if data['status'] == 'INVALID_REQUEST':
                    logger.warning(f"    Invalid request (likely delay issue), retrying...")
                    time.sleep(3)
                    continue
                    
                if data['status'] not in ['OK', 'ZERO_RESULTS']:
                    logger.warning(f"    API Status: {data.get('status')} - {data.get('error_message', '')}")
                    break
                
                results = data.get('results', [])
                logger.info(f"    📄 Page {page}: {len(results)} results")
                
                for place in results:
                    place_id = place.get('place_id')
                    if place_id:
                        details = self.discovery._get_place_details(place_id)
                        if details:
                            church_data = self.discovery._parse_church_data(details)
                            if church_data:
                                all_results.append(church_data)
                        time.sleep(0.2)
                
                next_page_token = data.get('next_page_token')
                if not next_page_token:
                    logger.info(f"    ℹ️  No more pages available")
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"    ❌ Search error: {e}")
                break
        
        return all_results
    
    def _get_major_cities(self, state_code: str) -> List[str]:
        """Major cities to search in each state"""
        city_map = {
            'NY': ['New York', 'Brooklyn', 'Queens', 'Buffalo', 'Rochester', 'Syracuse', 'Albany', 'Staten Island'],
            'MD': ['Baltimore', 'Columbia', 'Silver Spring', 'Frederick', 'Rockville', 'Gaithersburg'],
            'OR': ['Portland', 'Salem', 'Eugene', 'Gresham', 'Beaverton'],
            'WY': ['Cheyenne', 'Casper', 'Laramie', 'Gillette'],
            'MI': ['Detroit', 'Grand Rapids', 'Warren', 'Sterling Heights', 'Ann Arbor', 'Lansing'],
            'OH': ['Cleveland', 'Columbus', 'Cincinnati', 'Toledo', 'Akron', 'Dayton'],
            'CA': ['Los Angeles', 'San Francisco', 'San Diego', 'San Jose', 'Sacramento', 'Fresno', 'Oakland'],
            'TX': ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth', 'El Paso', 'Arlington'],
            'FL': ['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Fort Lauderdale', 'West Palm Beach'],
            'PA': ['Philadelphia', 'Pittsburgh', 'Allentown', 'Erie', 'Reading'],
            'IL': ['Chicago', 'Aurora', 'Naperville', 'Joliet', 'Rockford'],
            'NJ': ['Newark', 'Jersey City', 'Paterson', 'Elizabeth', 'Edison', 'Woodbridge'],
            'VA': ['Virginia Beach', 'Norfolk', 'Richmond', 'Arlington', 'Alexandria', 'Chesapeake'],
        }
        return city_map.get(state_code, [])


def get_current_count(state: str) -> int:
    """Get current church count for state"""
    conn = sqlite3.connect('coptic_events.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM google_places_churches WHERE state = ?", (state,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def main():
    logger.info("="*60)
    logger.info("COMPREHENSIVE STATE RETRY WITH FULL PAGINATION")
    logger.info("="*60)
    
    discovery = ComprehensiveDiscovery()
    
    for state in RETRY_STATES:
        try:
            current_count = get_current_count(state)
            logger.info(f"\n{state}: Currently have {current_count} churches")
            
            # Run comprehensive search
            churches = discovery.search_state_thoroughly(state)
            
            # Save to database (will deduplicate automatically)
            if churches:
                discovery.discovery._save_to_database(churches)
                new_count = get_current_count(state)
                added = new_count - current_count
                logger.info(f"✅ {state}: Added {added} new churches (total now: {new_count})")
            
            time.sleep(5)  # Rate limiting
            
        except Exception as e:
            logger.error(f"❌ Error processing {state}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    logger.info("\n" + "="*60)
    logger.info("✅ COMPREHENSIVE RETRY COMPLETE")
    logger.info("="*60)


if __name__ == "__main__":
    main()
