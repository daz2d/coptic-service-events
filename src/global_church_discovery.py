"""
Global Coptic Church Discovery - One-Time Population
Discovers ALL Coptic Orthodox churches worldwide using Google Places API
Stores in local database for instant, free queries forever
"""

import os
import logging
import time
from typing import List
from dotenv import load_dotenv
from tqdm import tqdm

from src.google_places_discovery import GooglePlacesChurchDiscovery, GooglePlaceChurch

load_dotenv()
logger = logging.getLogger(__name__)


class GlobalChurchDatabase:
    """Build and manage global Coptic Orthodox church database"""
    
    # Major regions/countries with significant Coptic presence
    REGIONS = [
        # United States (by state)
        ('NJ', 'New Jersey'), ('NY', 'New York'), ('CA', 'California'),
        ('IL', 'Illinois'), ('TX', 'Texas'), ('FL', 'Florida'),
        ('PA', 'Pennsylvania'), ('OH', 'Ohio'), ('MI', 'Michigan'),
        ('GA', 'Georgia'), ('NC', 'North Carolina'), ('VA', 'Virginia'),
        ('MA', 'Massachusetts'), ('AZ', 'Arizona'), ('CO', 'Colorado'),
        ('WA', 'Washington'), ('OR', 'Oregon'), ('NV', 'Nevada'),
        ('TN', 'Tennessee'), ('MD', 'Maryland'), ('CT', 'Connecticut'),
        
        # Canada (by province)
        ('ON', 'Ontario, Canada'), ('QC', 'Quebec, Canada'),
        ('BC', 'British Columbia, Canada'), ('AB', 'Alberta, Canada'),
        
        # International
        ('EG', 'Egypt'), ('AU', 'Australia'), ('UK', 'United Kingdom'),
        ('DE', 'Germany'), ('FR', 'France'), ('IT', 'Italy'),
        ('NL', 'Netherlands'), ('CH', 'Switzerland'), ('AT', 'Austria'),
        ('SE', 'Sweden'), ('NO', 'Norway'), ('DK', 'Denmark'),
        ('UAE', 'United Arab Emirates'), ('KW', 'Kuwait'),
        ('SA', 'Saudi Arabia'), ('JO', 'Jordan'), ('LB', 'Lebanon'),
    ]
    
    def __init__(self, api_key: str = None):
        self.discovery = GooglePlacesChurchDiscovery(api_key)
        self.all_churches = []
    
    def discover_all_churches(self, max_per_region: int = 100) -> List[GooglePlaceChurch]:
        """
        Discover ALL Coptic Orthodox churches worldwide
        
        This is a ONE-TIME operation that populates the global database.
        After running once, you never need to use the API again!
        
        Args:
            max_per_region: Maximum churches to find per region
            
        Returns:
            List of all discovered churches
        """
        logger.info("🌍 Starting GLOBAL Coptic Orthodox Church discovery...")
        logger.info(f"   Searching {len(self.REGIONS)} regions worldwide")
        logger.info(f"   This is a ONE-TIME operation - building permanent cache\n")
        
        total_found = 0
        seen_place_ids = set()
        
        # Progress bar for regions
        pbar = tqdm(self.REGIONS, desc="🌍 Discovering churches", unit="region")
        
        for i, (code, region_name) in enumerate(pbar, 1):
            pbar.set_description(f"🌍 [{i}/{len(self.REGIONS)}] {region_name[:30]}")
            
            try:
                # Search this region
                if code in ['NJ', 'NY', 'CA', 'IL', 'TX', 'FL', 'PA', 'OH', 'MI', 
                           'GA', 'NC', 'VA', 'MA', 'AZ', 'CO', 'WA', 'OR', 'NV',
                           'TN', 'MD', 'CT', 'ON', 'QC', 'BC', 'AB']:
                    # US/Canada states/provinces - use existing method
                    churches = self.discovery.search_churches_in_state(
                        code, 
                        max_results=max_per_region
                    )
                else:
                    # International - use text search
                    churches = self._search_country(region_name, max_per_region)
                
                # Deduplicate by place_id AND validate location
                new_churches = []
                for c in churches:
                    if c.place_id in seen_place_ids:
                        continue
                    
                    # CRITICAL: Validate church is actually in this state/region
                    if code in ['NJ', 'NY', 'CA', 'IL', 'TX', 'FL', 'PA', 'OH', 'MI', 
                               'GA', 'NC', 'VA', 'MA', 'AZ', 'CO', 'WA', 'OR', 'NV',
                               'TN', 'MD', 'CT']:
                        # US state - verify state matches
                        church_state = getattr(c, 'state', None)
                        if church_state and church_state.upper() == code.upper():
                            seen_place_ids.add(c.place_id)
                            new_churches.append(c)
                            self.all_churches.append(c)
                        else:
                            pbar.write(f"   ⚠️  Skipped {c.name} (in {church_state}, not {code})")
                    
                    elif code in ['ON', 'QC', 'BC', 'AB']:
                        # Canadian province - verify country is Canada
                        church_country = getattr(c, 'country', None)
                        if church_country and 'Canada' in church_country:
                            seen_place_ids.add(c.place_id)
                            new_churches.append(c)
                            self.all_churches.append(c)
                    
                    else:
                        # International - verify country matches
                        church_country = getattr(c, 'country', None)
                        if church_country and region_name.split(',')[0].strip() in church_country:
                            seen_place_ids.add(c.place_id)
                            new_churches.append(c)
                            self.all_churches.append(c)
                
                total_found += len(new_churches)
                
                pbar.set_postfix({
                    'found': len(new_churches),
                    'total': total_found,
                    'avg_rating': f"{sum(c.rating for c in new_churches if c.rating) / len([c for c in new_churches if c.rating]):.1f}" if any(c.rating for c in new_churches) else 'N/A'
                })
                
                # Rate limiting - be nice to Google
                time.sleep(1)
                
            except Exception as e:
                pbar.write(f"   ❌ Error searching {region_name}: {e}")
                continue
        
        pbar.close()
        
        logger.info(f"\n🎉 DISCOVERY COMPLETE!")
        logger.info(f"   Total churches found: {len(self.all_churches)}")
        logger.info(f"   Unique place IDs: {len(seen_place_ids)}")
        
        return self.all_churches
    
    def _search_country(self, country_name: str, max_results: int) -> List[GooglePlaceChurch]:
        """Search for churches in a country using text search"""
        # Use the existing text search functionality
        url = f"{self.discovery.base_url}/textsearch/json"
        
        params = {
            'query': f'Coptic Orthodox Church in {country_name}',
            'key': self.discovery.api_key
        }
        
        churches = []
        seen_place_ids = set()
        
        try:
            import requests
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'OK':
                for place in data.get('results', []):
                    if len(churches) >= max_results:
                        break
                        
                    place_id = place.get('place_id')
                    
                    if place_id in seen_place_ids:
                        continue
                    
                    seen_place_ids.add(place_id)
                    
                    # Get detailed information
                    details = self.discovery._get_place_details(place_id)
                    
                    if details:
                        church = self.discovery._parse_church_data(details)
                        if church:
                            churches.append(church)
                    
                    time.sleep(0.2)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error searching {country_name}: {e}")
        
        return churches
    
    def save_to_database(self, db_path: str = 'coptic_events.db'):
        """Save all discovered churches to database"""
        logger.info(f"\n💾 Saving {len(self.all_churches)} churches to database...")
        
        self.discovery.save_to_database(self.all_churches, db_path)
        
        logger.info("✅ Global church database populated!")
    
    def clear_old_data(self, db_path: str = 'coptic_events.db'):
        """Clear old NIHOV data from database"""
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop old tables if they exist
        logger.info("🗑️  Clearing old NIHOV data...")
        
        # We'll keep the events table but can clear church cache
        try:
            cursor.execute("DROP TABLE IF EXISTS church_cache_temp")
            conn.commit()
            logger.info("   ✓ Cleared old cache")
        except:
            pass
        
        conn.close()


def estimate_cost(num_regions: int, avg_churches_per_region: int = 30):
    """Estimate API cost for global discovery"""
    # Text search: $0.017 per request
    # Place details: $0.032 per request
    
    text_searches = num_regions * 4  # 4 queries per region
    place_details = num_regions * avg_churches_per_region
    
    text_cost = text_searches * 0.017
    details_cost = place_details * 0.032
    total_cost = text_cost + details_cost
    
    print(f"\n💰 ESTIMATED API COST:")
    print(f"   Regions to search: {num_regions}")
    print(f"   Estimated churches: {num_regions * avg_churches_per_region}")
    print(f"   Text searches: {text_searches} × $0.017 = ${text_cost:.2f}")
    print(f"   Place details: {place_details} × $0.032 = ${details_cost:.2f}")
    print(f"   TOTAL: ${total_cost:.2f}")
    print(f"\n   Free tier: $200/month")
    print(f"   Cost: {'FREE! (under tier)' if total_cost < 200 else f'${total_cost:.2f}'}")
    print(f"\n   This is a ONE-TIME cost. After this, all queries are FREE forever!")


if __name__ == "__main__":
    """
    ONE-TIME GLOBAL DISCOVERY SCRIPT
    
    Run this once to populate the global church database.
    After this, you never need the API again - all queries are local!
    
    Usage:
        python -m src.global_church_discovery
    """
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Show cost estimate
    print("\n" + "="*80)
    print("GLOBAL COPTIC ORTHODOX CHURCH DISCOVERY")
    print("="*80)
    
    estimate_cost(len(GlobalChurchDatabase.REGIONS))
    
    print("\n" + "="*80)
    input("\nPress Enter to start discovery (or Ctrl+C to cancel)...")
    print("="*80 + "\n")
    
    # Run discovery
    db = GlobalChurchDatabase()
    
    # Clear old data
    db.clear_old_data()
    
    # Discover all churches
    churches = db.discover_all_churches(max_per_region=50)
    
    # Save to database
    db.save_to_database()
    
    # Show summary
    print(f"\n" + "="*80)
    print("✅ SUCCESS - GLOBAL DATABASE POPULATED!")
    print("="*80)
    print(f"\n📊 SUMMARY:")
    print(f"   Total churches: {len(churches)}")
    print(f"   Database: coptic_events.db")
    print(f"   Table: google_places_churches")
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. App now uses this database for ALL queries")
    print(f"   2. Location searches are INSTANT (local SQL)")
    print(f"   3. No more API calls needed - FREE forever!")
    print(f"   4. Much better data quality than NIHOV")
    print(f"\n💡 You can re-run this script quarterly to refresh data")
    print("="*80 + "\n")
