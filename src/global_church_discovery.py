"""
Global Coptic Church Discovery - One-Time Population
Discovers ALL Coptic Orthodox churches worldwide using Google Places API
Stores in local database for instant, free queries forever
"""

import os
import logging
import time
import hashlib
from typing import List, Set, Tuple
from dotenv import load_dotenv
from tqdm import tqdm
from difflib import SequenceMatcher

from src.google_places_discovery import GooglePlacesChurchDiscovery, GooglePlaceChurch

load_dotenv()
logger = logging.getLogger(__name__)


class GlobalChurchDatabase:
    """Build and manage global Coptic Orthodox church database"""
    
    # US-ONLY REGIONS - All 50 States + DC
    # Focused scope for accuracy and manageable API costs
    REGIONS = [
        # ========== UNITED STATES (All 50 States + DC) ==========
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
        ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('DC', 'Washington DC'),
    ]
    
    def __init__(self, api_key: str = None):
        self.discovery = GooglePlacesChurchDiscovery(api_key)
        self.all_churches = []
        self.seen_signatures = {}  # (name, city, state) -> church for smart dedup
        self.seen_hashes = set()  # Hash-based deduplication for ultimate accuracy
    
    def _compute_church_hash(self, church: GooglePlaceChurch) -> str:
        """
        Compute unique hash for a church based on immutable characteristics
        
        Uses: normalized name + coordinates + address
        This catches duplicates even if place_id somehow differs
        """
        # Normalize name
        norm_name = self._normalize_church_name(church.name)
        
        # Get coordinates (rounded to 5 decimal places = ~1 meter accuracy)
        lat = round(church.latitude, 5) if church.latitude else 0.0
        lon = round(church.longitude, 5) if church.longitude else 0.0
        
        # Get street address (first part before comma)
        address = getattr(church, 'address', '')
        street = address.split(',')[0].lower().strip() if address else ''
        
        # Create hash string
        hash_string = f"{norm_name}|{lat}|{lon}|{street}"
        
        # Compute SHA256 hash
        hash_obj = hashlib.sha256(hash_string.encode('utf-8'))
        return hash_obj.hexdigest()[:16]  # First 16 chars is plenty
    
    def _normalize_church_name(self, name: str) -> str:
        """Normalize church name for comparison"""
        name = name.lower()
        # Remove common variations
        replacements = {
            'saint': 'st',
            'st.': 'st',
            '&': 'and',
            'coptic orthodox church': '',
            'coptic orthodox': '',
            'coptic church': '',
            'church': '',
        }
        for old, new in replacements.items():
            name = name.replace(old, new)
        # Remove extra spaces
        name = ' '.join(name.split())
        return name.strip()
    
    def _is_duplicate(self, church: GooglePlaceChurch, seen_place_ids: Set[str]) -> Tuple[bool, str]:
        """
        Smart duplicate detection using multiple factors
        
        Returns:
            (is_duplicate, reason)
        """
        # 0. Hash-based check (ULTIMATE TRUTH)
        # This catches duplicates even if place_id differs (rare but possible)
        church_hash = self._compute_church_hash(church)
        if church_hash in self.seen_hashes:
            return True, "same location hash"
        
        # 1. Exact place_id match (Google's unique identifier)
        if church.place_id in seen_place_ids:
            return True, "same place_id"
        
        # 2. Create unique signature: normalized name + city + state
        # This allows "St Mary" in NY and "St Mary" in CA to coexist
        norm_name = self._normalize_church_name(church.name)
        city = getattr(church, 'city', '').lower().strip()
        state = getattr(church, 'state', '').upper().strip()
        
        signature = (norm_name, city, state)
        
        # Check if we've seen this exact church (name+city+state)
        if signature in self.seen_signatures:
            existing = self.seen_signatures[signature]
            # Same church, just found in another search
            # Verify it's really a duplicate by comparing addresses
            existing_addr = getattr(existing, 'address', '').lower()
            new_addr = getattr(church, 'address', '').lower()
            
            # If addresses are very similar, it's definitely a duplicate
            if existing_addr and new_addr:
                # Compare street addresses (ignore zip codes)
                existing_street = existing_addr.split(',')[0] if ',' in existing_addr else existing_addr
                new_street = new_addr.split(',')[0] if ',' in new_addr else new_addr
                
                if existing_street == new_street:
                    return True, f"duplicate in {city}, {state}"
        
        return False, ""
    
    def _record_church(self, church: GooglePlaceChurch, seen_place_ids: Set[str]):
        """Record church in tracking structures"""
        # Record place_id
        seen_place_ids.add(church.place_id)
        
        # Record hash
        church_hash = self._compute_church_hash(church)
        self.seen_hashes.add(church_hash)
        
        # Record signature
        norm_name = self._normalize_church_name(church.name)
        city = getattr(church, 'city', '').lower().strip()
        state = getattr(church, 'state', '').upper().strip()
        signature = (norm_name, city, state)
        
        self.seen_signatures[signature] = church
    
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
                
                # Smart deduplication with validation
                new_churches = []
                skipped_wrong_state = 0
                skipped_no_state = 0
                skipped_duplicate = 0
                skipped_not_coptic = 0
                
                for c in churches:
                    # SMART DUPLICATE CHECK
                    is_dup, dup_reason = self._is_duplicate(c, seen_place_ids)
                    if is_dup:
                        skipped_duplicate += 1
                        if skipped_duplicate <= 3:  # Only show first few
                            pbar.write(f"   🔄 Skipped duplicate: {c.name[:40]} ({dup_reason})")
                        continue
                    
                    # Get church location data
                    church_state = getattr(c, 'state', None)
                    church_country = getattr(c, 'country', None)
                    
                    # STRICT US-ONLY VALIDATION
                    # 1. Must have a state
                    if not church_state:
                        skipped_no_state += 1
                        pbar.write(f"   ⚠️  Skipped {c.name[:50]} - No state info")
                        continue
                    
                    # 2. Must be in USA (not Canada, Mexico, etc)
                    country_lower = (church_country or '').lower()
                    if church_country and 'united states' not in country_lower and 'usa' not in country_lower:
                        skipped_wrong_state += 1
                        pbar.write(f"   ⚠️  Skipped {c.name[:50]} - In {church_country}, not USA")
                        continue
                    
                    # 3. State code must match expected state
                    if church_state and church_state.upper() != code.upper():
                        skipped_wrong_state += 1
                        pbar.write(f"   ⚠️  Skipped {c.name[:50]} - In {church_state}, expected {code}")
                        continue
                    
                    # 4. Verify it's actually Coptic Orthodox (not other Orthodox)
                    name_lower = c.name.lower()
                    if 'coptic' not in name_lower:
                        # If 'coptic' not in name, it might be Greek/Russian/Antiochian Orthodox
                        if 'greek' in name_lower or 'russian' in name_lower or 'antioch' in name_lower or 'serbian' in name_lower:
                            skipped_not_coptic += 1
                            pbar.write(f"   ⚠️  Skipped {c.name[:50]} - Not Coptic Orthodox")
                            continue
                    
                    # PASSED ALL VALIDATIONS - Record this church
                    self._record_church(c, seen_place_ids)
                    new_churches.append(c)
                    self.all_churches.append(c)
                
                total_found += len(new_churches)
                total_skipped = skipped_duplicate + skipped_wrong_state + skipped_no_state + skipped_not_coptic
                
                # Enhanced progress output with validation stats
                if new_churches:
                    avg_rating = sum(c.rating for c in new_churches if c.rating) / len([c for c in new_churches if c.rating]) if any(c.rating for c in new_churches) else 0
                    pbar.write(f"   ✅ {region_name}: {len(new_churches)} churches (avg {avg_rating:.1f}★) | Total: {total_found}")
                    if total_skipped > 0:
                        skip_details = []
                        if skipped_duplicate > 0:
                            skip_details.append(f"{skipped_duplicate} dupes")
                        if skipped_wrong_state > 0:
                            skip_details.append(f"{skipped_wrong_state} wrong state")
                        if skipped_no_state > 0:
                            skip_details.append(f"{skipped_no_state} no state")
                        if skipped_not_coptic > 0:
                            skip_details.append(f"{skipped_not_coptic} not Coptic")
                        pbar.write(f"      (Skipped: {', '.join(skip_details)})")
                else:
                    pbar.write(f"   ⚪ {region_name}: No churches found")
                    if total_skipped > 0:
                        skip_details = []
                        if skipped_duplicate > 0:
                            skip_details.append(f"{skipped_duplicate} dupes")
                        if skipped_wrong_state > 0:
                            skip_details.append(f"{skipped_wrong_state} wrong state")
                        if skipped_no_state > 0:
                            skip_details.append(f"{skipped_no_state} no state")
                        if skipped_not_coptic > 0:
                            skip_details.append(f"{skipped_not_coptic} not Coptic")
                        pbar.write(f"      (Found {len(churches)} but all invalid: {', '.join(skip_details)})")
                
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
        
        # POST-PROCESSING: Final cleanup
        logger.info(f"\n🔍 Running post-processing cleanup...")
        cleaned_churches = self._post_process_cleanup(self.all_churches)
        
        logger.info(f"\n" + "="*80)
        logger.info(f"🎉 DISCOVERY COMPLETE!")
        logger.info(f"="*80)
        logger.info(f"   Total churches found: {len(cleaned_churches)}")
        logger.info(f"   Unique place IDs: {len(seen_place_ids)}")
        logger.info(f"   Unique location hashes: {len(self.seen_hashes)}")
        logger.info(f"   Unique signatures: {len(self.seen_signatures)}")
        logger.info(f"   Regions searched: {len(self.REGIONS)}")
        logger.info(f"   Average per region: {len(cleaned_churches) / len(self.REGIONS):.1f}")
        logger.info(f"="*80 + "\n")
        
        return cleaned_churches
    
    def _post_process_cleanup(self, churches: List[GooglePlaceChurch]) -> List[GooglePlaceChurch]:
        """
        Final cleanup pass to ensure data quality
        - Remove any remaining duplicates (by hash AND place_id)
        - Validate all required fields
        - Sort by state and city
        """
        logger.info(f"   Pre-cleanup count: {len(churches)}")
        
        # Track by BOTH hash and place_id for maximum deduplication
        unique_by_place_id = {}
        unique_by_hash = {}
        duplicates_by_place_id = 0
        duplicates_by_hash = 0
        
        for church in churches:
            # Check place_id
            if church.place_id in unique_by_place_id:
                duplicates_by_place_id += 1
                continue
            
            # Check hash
            church_hash = self._compute_church_hash(church)
            if church_hash in unique_by_hash:
                duplicates_by_hash += 1
                logger.debug(f"   Hash collision: {church.name} in {getattr(church, 'city', 'Unknown')}")
                continue
            
            # Keep this church
            unique_by_place_id[church.place_id] = church
            unique_by_hash[church_hash] = church
        
        cleaned = list(unique_by_place_id.values())
        
        # Sort by state, then city, then name
        cleaned.sort(key=lambda c: (
            getattr(c, 'state', 'ZZ'),
            getattr(c, 'city', 'Unknown'),
            c.name
        ))
        
        logger.info(f"   Post-cleanup count: {len(cleaned)}")
        total_removed = duplicates_by_place_id + duplicates_by_hash
        if total_removed > 0:
            logger.info(f"   Removed {total_removed} duplicates ({duplicates_by_place_id} by place_id, {duplicates_by_hash} by hash)")
        
        return cleaned
    
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
