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
    
    # COMPREHENSIVE GLOBAL REGIONS - All Coptic Orthodox churches worldwide
    REGIONS = [
        # ========== UNITED STATES (All 50 States) ==========
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
        ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
        ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
        ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
        ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
        ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
        ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
        ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
        ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'), ('WY', 'Wyoming'),
        
        # ========== CANADA (All Provinces & Territories) ==========
        ('AB', 'Alberta, Canada'), ('BC', 'British Columbia, Canada'),
        ('MB', 'Manitoba, Canada'), ('NB', 'New Brunswick, Canada'),
        ('NL', 'Newfoundland and Labrador, Canada'), ('NS', 'Nova Scotia, Canada'),
        ('ON', 'Ontario, Canada'), ('PE', 'Prince Edward Island, Canada'),
        ('QC', 'Quebec, Canada'), ('SK', 'Saskatchewan, Canada'),
        
        # ========== MIDDLE EAST (Coptic heartland) ==========
        ('EG', 'Egypt'), ('JO', 'Jordan'), ('LB', 'Lebanon'), ('PS', 'Palestine'),
        ('IL', 'Israel'), ('UAE', 'United Arab Emirates'), ('KW', 'Kuwait'),
        ('SA', 'Saudi Arabia'), ('QA', 'Qatar'), ('BH', 'Bahrain'), ('OM', 'Oman'),
        ('IQ', 'Iraq'), ('SY', 'Syria'), ('YE', 'Yemen'),
        
        # ========== EUROPE ==========
        ('GB', 'United Kingdom'), ('IE', 'Ireland'), ('FR', 'France'), ('DE', 'Germany'),
        ('IT', 'Italy'), ('ES', 'Spain'), ('PT', 'Portugal'), ('NL', 'Netherlands'),
        ('BE', 'Belgium'), ('CH', 'Switzerland'), ('AT', 'Austria'), ('GR', 'Greece'),
        ('SE', 'Sweden'), ('NO', 'Norway'), ('DK', 'Denmark'), ('FI', 'Finland'),
        ('PL', 'Poland'), ('CZ', 'Czech Republic'), ('HU', 'Hungary'), ('RO', 'Romania'),
        ('BG', 'Bulgaria'), ('RS', 'Serbia'), ('HR', 'Croatia'), ('SI', 'Slovenia'),
        
        # ========== AFRICA ==========
        ('KE', 'Kenya'), ('UG', 'Uganda'), ('TZ', 'Tanzania'), ('ET', 'Ethiopia'),
        ('SD', 'Sudan'), ('SS', 'South Sudan'), ('ZA', 'South Africa'), ('ZW', 'Zimbabwe'),
        ('BW', 'Botswana'), ('NA', 'Namibia'), ('ZM', 'Zambia'), ('MW', 'Malawi'),
        ('GH', 'Ghana'), ('NG', 'Nigeria'), ('CI', 'Ivory Coast'), ('SN', 'Senegal'),
        
        # ========== OCEANIA ==========
        ('AU-NSW', 'New South Wales, Australia'), ('AU-VIC', 'Victoria, Australia'),
        ('AU-QLD', 'Queensland, Australia'), ('AU-WA', 'Western Australia'),
        ('AU-SA', 'South Australia'), ('NZ', 'New Zealand'),
        
        # ========== ASIA ==========
        ('JP', 'Japan'), ('KR', 'South Korea'), ('CN', 'China'), ('HK', 'Hong Kong'),
        ('SG', 'Singapore'), ('MY', 'Malaysia'), ('TH', 'Thailand'), ('PH', 'Philippines'),
        ('IN', 'India'), ('PK', 'Pakistan'), ('BD', 'Bangladesh'),
        
        # ========== SOUTH & CENTRAL AMERICA ==========
        ('BR', 'Brazil'), ('AR', 'Argentina'), ('CL', 'Chile'), ('CO', 'Colombia'),
        ('PE', 'Peru'), ('VE', 'Venezuela'), ('MX', 'Mexico'), ('PA', 'Panama'),
        ('CR', 'Costa Rica'), ('GT', 'Guatemala'),
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
                    
                    # Get church location data
                    church_state = getattr(c, 'state', None)
                    church_country = getattr(c, 'country', None)
                    
                    # CRITICAL: Validate church is actually in this state/region
                    valid = False
                    
                    # US States (50 states)
                    us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                                'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                                'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                                'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                                'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
                    
                    if code in us_states:
                        # US state - verify state matches
                        if church_state and church_state.upper() == code.upper():
                            valid = True
                    
                    # Canadian Provinces
                    elif code in ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'ON', 'PE', 'QC', 'SK']:
                        # Canada - verify country is Canada
                        if church_country and 'Canada' in church_country:
                            valid = True
                    
                    # Australian states
                    elif code.startswith('AU-'):
                        if church_country and 'Australia' in church_country:
                            valid = True
                    
                    # Country codes (2-letter ISO)
                    else:
                        # International - verify country matches
                        country_map = {
                            'EG': 'Egypt', 'JO': 'Jordan', 'LB': 'Lebanon', 'PS': 'Palestine',
                            'IL': 'Israel', 'UAE': 'United Arab Emirates', 'KW': 'Kuwait',
                            'SA': 'Saudi Arabia', 'QA': 'Qatar', 'BH': 'Bahrain', 'OM': 'Oman',
                            'IQ': 'Iraq', 'SY': 'Syria', 'YE': 'Yemen',
                            'GB': 'United Kingdom', 'IE': 'Ireland', 'FR': 'France', 'DE': 'Germany',
                            'IT': 'Italy', 'ES': 'Spain', 'PT': 'Portugal', 'NL': 'Netherlands',
                            'BE': 'Belgium', 'CH': 'Switzerland', 'AT': 'Austria', 'GR': 'Greece',
                            'SE': 'Sweden', 'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland',
                            'PL': 'Poland', 'CZ': 'Czech Republic', 'HU': 'Hungary', 'RO': 'Romania',
                            'BG': 'Bulgaria', 'RS': 'Serbia', 'HR': 'Croatia', 'SI': 'Slovenia',
                            'KE': 'Kenya', 'UG': 'Uganda', 'TZ': 'Tanzania', 'ET': 'Ethiopia',
                            'SD': 'Sudan', 'SS': 'South Sudan', 'ZA': 'South Africa', 'ZW': 'Zimbabwe',
                            'BW': 'Botswana', 'NA': 'Namibia', 'ZM': 'Zambia', 'MW': 'Malawi',
                            'GH': 'Ghana', 'NG': 'Nigeria', 'CI': 'Ivory Coast', 'SN': 'Senegal',
                            'NZ': 'New Zealand', 'JP': 'Japan', 'KR': 'South Korea', 'CN': 'China',
                            'HK': 'Hong Kong', 'SG': 'Singapore', 'MY': 'Malaysia', 'TH': 'Thailand',
                            'PH': 'Philippines', 'IN': 'India', 'PK': 'Pakistan', 'BD': 'Bangladesh',
                            'BR': 'Brazil', 'AR': 'Argentina', 'CL': 'Chile', 'CO': 'Colombia',
                            'PE': 'Peru', 'VE': 'Venezuela', 'MX': 'Mexico', 'PA': 'Panama',
                            'CR': 'Costa Rica', 'GT': 'Guatemala',
                        }
                        
                        expected_country = country_map.get(code)
                        if expected_country and church_country and expected_country in church_country:
                            valid = True
                    
                    if valid:
                        seen_place_ids.add(c.place_id)
                        new_churches.append(c)
                        self.all_churches.append(c)
                    else:
                        if church_state or church_country:
                            pbar.write(f"   ⚠️  Skipped {c.name[:40]} (in {church_state or church_country}, not {region_name})")
                
                total_found += len(new_churches)
                
                # Enhanced progress output
                if new_churches:
                    avg_rating = sum(c.rating for c in new_churches if c.rating) / len([c for c in new_churches if c.rating]) if any(c.rating for c in new_churches) else 0
                    pbar.write(f"   ✅ {region_name}: {len(new_churches)} churches (avg {avg_rating:.1f}★) | Total: {total_found}")
                else:
                    pbar.write(f"   ⚪ {region_name}: No churches found")
                
                pbar.set_postfix({
                    'found': len(new_churches),
                    'total': total_found,
                    'avg_rating': f"{avg_rating:.1f}" if new_churches and any(c.rating for c in new_churches) else 'N/A'
                })
                
                # Progress checkpoint every 10 regions
                if (i % 10) == 0:
                    pbar.write(f"\n📊 CHECKPOINT [{i}/{len(self.REGIONS)}]: {total_found} total churches discovered")
                    pbar.write(f"   Estimated completion: {int((len(self.REGIONS) - i) * 8 / 60)} minutes remaining\n")
                
                # Rate limiting - be nice to Google
                time.sleep(1)
                
            except Exception as e:
                pbar.write(f"   ❌ Error searching {region_name}: {e}")
                continue
        
        pbar.close()
        
        logger.info(f"\n" + "="*80)
        logger.info(f"🎉 DISCOVERY COMPLETE!")
        logger.info(f"="*80)
        logger.info(f"   Total churches found: {len(self.all_churches)}")
        logger.info(f"   Unique place IDs: {len(seen_place_ids)}")
        logger.info(f"   Regions searched: {len(self.REGIONS)}")
        logger.info(f"   Average per region: {len(self.all_churches) / len(self.REGIONS):.1f}")
        logger.info(f"="*80 + "\n")
        
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
