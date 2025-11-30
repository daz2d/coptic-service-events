"""
Church Directory - Google Places Edition
Uses cached Google Places data instead of scraping NIHOV
"""

import logging
import sqlite3
from typing import List, Dict, Optional
from geopy.distance import geodesic

logger = logging.getLogger(__name__)


class GooglePlacesChurchDirectory:
    """Access churches from Google Places database"""
    
    def __init__(self, db_path: str = 'coptic_events.db'):
        self.db_path = db_path
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Make sure google_places_churches table exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS google_places_churches (
                place_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT,
                latitude REAL,
                longitude REAL,
                phone TEXT,
                website TEXT,
                rating REAL,
                user_ratings_total INTEGER,
                opening_hours TEXT,
                vicinity TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def discover_churches_by_radius(
        self, 
        user_lat: float, 
        user_lon: float, 
        radius_miles: int = 15
    ) -> List[Dict]:
        """
        Find churches within radius using LOCAL DATABASE (instant & free!)
        
        Args:
            user_lat: User's latitude
            user_lon: User's longitude
            radius_miles: Search radius in miles
            
        Returns:
            List of churches within radius with all details
        """
        logger.info(f"🔍 Searching LOCAL database for churches within {radius_miles} miles")
        logger.info(f"   Location: ({user_lat:.4f}, {user_lon:.4f})")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get ALL churches with coordinates
        cursor.execute("""
            SELECT place_id, name, address, latitude, longitude, phone, website, 
                   rating, user_ratings_total, vicinity
            FROM google_places_churches
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        
        all_churches = cursor.fetchall()
        conn.close()
        
        if not all_churches:
            logger.warning("⚠️  No churches in database! Run: python -m src.global_church_discovery")
            return []
        
        logger.info(f"📍 Checking {len(all_churches)} cached churches...")
        
        # Filter by distance
        nearby_churches = []
        user_coords = (user_lat, user_lon)
        
        for row in all_churches:
            church_coords = (row['latitude'], row['longitude'])
            distance = geodesic(user_coords, church_coords).miles
            
            if distance <= radius_miles:
                church = {
                    'place_id': row['place_id'],
                    'name': row['name'],
                    'address': row['address'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'phone': row['phone'],
                    'url': row['website'],  # Match old field name
                    'website': row['website'],
                    'rating': row['rating'],
                    'reviews': row['user_ratings_total'],
                    'vicinity': row['vicinity'],
                    'distance_miles': round(distance, 1),
                    # Parse city and state from address
                    'city': self._extract_city(row['address']),
                    'state': self._extract_state(row['address']),
                }
                nearby_churches.append(church)
        
        # Sort by distance
        nearby_churches.sort(key=lambda x: x['distance_miles'])
        
        logger.info(f"✅ Found {len(nearby_churches)} churches within {radius_miles} miles")
        
        # Show top 5
        for i, church in enumerate(nearby_churches[:5], 1):
            logger.info(f"   {i}. {church['name']} ({church['distance_miles']} mi)")
        
        return nearby_churches
    
    def _extract_city(self, address: str) -> Optional[str]:
        """Extract city from Google address format"""
        if not address:
            return None
        
        # Google format: "Street, City, State ZIP, Country"
        parts = address.split(',')
        if len(parts) >= 2:
            return parts[-3].strip() if len(parts) >= 3 else parts[-2].strip()
        return None
    
    def _extract_state(self, address: str) -> Optional[str]:
        """Extract state from Google address format"""
        if not address:
            return None
        
        # Google format: "Street, City, State ZIP, Country"
        parts = address.split(',')
        if len(parts) >= 3:
            state_zip = parts[-2].strip()
            # Extract state code (first 2 letters before space)
            state = state_zip.split()[0] if state_zip else None
            return state
        return None
    
    def get_church_count(self) -> int:
        """Get total number of churches in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM google_places_churches")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_coverage_stats(self) -> Dict:
        """Get statistics about database coverage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN website IS NOT NULL THEN 1 ELSE 0 END) as with_website,
                SUM(CASE WHEN phone IS NOT NULL THEN 1 ELSE 0 END) as with_phone,
                SUM(CASE WHEN rating IS NOT NULL THEN 1 ELSE 0 END) as with_rating,
                AVG(rating) as avg_rating
            FROM google_places_churches
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_churches': row[0],
            'with_website': row[1],
            'with_phone': row[2],
            'with_rating': row[3],
            'avg_rating': round(row[4], 2) if row[4] else None,
            'website_pct': round(row[1] / row[0] * 100, 1) if row[0] else 0,
            'phone_pct': round(row[2] / row[0] * 100, 1) if row[0] else 0,
        }


if __name__ == "__main__":
    """Test the directory"""
    logging.basicConfig(level=logging.INFO)
    
    directory = GooglePlacesChurchDirectory()
    
    # Show stats
    stats = directory.get_coverage_stats()
    print(f"\n📊 CHURCH DATABASE STATISTICS")
    print("="*60)
    print(f"Total churches: {stats['total_churches']}")
    print(f"With website: {stats['with_website']} ({stats['website_pct']}%)")
    print(f"With phone: {stats['with_phone']} ({stats['phone_pct']}%)")
    print(f"With rating: {stats['with_rating']}")
    print(f"Average rating: {stats['avg_rating']}/5.0")
    print("="*60)
    
    # Test search near Clark, NJ
    print(f"\n🔍 Testing search near Clark, NJ (15 mile radius)")
    churches = directory.discover_churches_by_radius(40.62, -74.32, radius_miles=15)
    
    print(f"\nFound {len(churches)} churches:")
    for i, church in enumerate(churches[:10], 1):
        print(f"\n{i}. {church['name']}")
        print(f"   📏 {church['distance_miles']} miles")
        print(f"   📍 {church['city']}, {church['state']}")
        print(f"   🌐 {church['website'] or 'No website'}")
        if church['rating']:
            print(f"   ⭐ {church['rating']}/5 ({church['reviews']} reviews)")
