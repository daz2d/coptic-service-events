#!/usr/bin/env python3
"""
Validation Report - Verify church data accuracy
Checks location accuracy, data completeness, and potential issues
"""

import sqlite3
import sys
from collections import defaultdict

def validate_database(db_path='coptic_events.db'):
    """Generate comprehensive validation report"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='google_places_churches'")
        if not cursor.fetchone():
            print("❌ No church database found. Run discovery first.")
            return False
        
        print("="*80)
        print("🔍 CHURCH DATABASE VALIDATION REPORT")
        print("="*80)
        
        # 1. Total count
        cursor.execute("SELECT COUNT(*) FROM google_places_churches")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total Churches: {total}")
        
        # 2. State distribution
        print(f"\n📍 Churches by State:")
        cursor.execute("""
            SELECT state, COUNT(*) as count
            FROM google_places_churches
            WHERE state IS NOT NULL
            GROUP BY state
            ORDER BY count DESC
        """)
        
        state_counts = cursor.fetchall()
        for state, count in state_counts[:10]:
            print(f"   {state}: {count}")
        if len(state_counts) > 10:
            print(f"   ... and {len(state_counts) - 10} more states")
        
        # 3. Data completeness
        print(f"\n✅ Data Completeness:")
        cursor.execute("SELECT COUNT(*) FROM google_places_churches WHERE website IS NOT NULL AND website != ''")
        with_website = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM google_places_churches WHERE phone IS NOT NULL AND phone != ''")
        with_phone = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM google_places_churches WHERE address IS NOT NULL AND address != ''")
        with_address = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM google_places_churches WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
        with_coords = cursor.fetchone()[0]
        
        print(f"   Websites: {with_website}/{total} ({100*with_website/total:.1f}%)")
        print(f"   Phone numbers: {with_phone}/{total} ({100*with_phone/total:.1f}%)")
        print(f"   Addresses: {with_address}/{total} ({100*with_address/total:.1f}%)")
        print(f"   Coordinates: {with_coords}/{total} ({100*with_coords/total:.1f}%)")
        
        # 4. Quality metrics
        print(f"\n⭐ Quality Metrics:")
        cursor.execute("""
            SELECT 
                AVG(rating) as avg_rating,
                AVG(user_ratings_total) as avg_reviews
            FROM google_places_churches
            WHERE rating IS NOT NULL
        """)
        avg_rating, avg_reviews = cursor.fetchone()
        if avg_rating:
            print(f"   Average rating: {avg_rating:.2f}/5.0")
            print(f"   Average reviews: {avg_reviews:.1f}")
        
        # 5. Potential issues
        print(f"\n⚠️  Potential Issues:")
        issues = []
        
        # Missing state
        cursor.execute("SELECT COUNT(*) FROM google_places_churches WHERE state IS NULL OR state = ''")
        missing_state = cursor.fetchone()[0]
        if missing_state > 0:
            issues.append(f"   {missing_state} churches missing state")
        
        # No website or phone
        cursor.execute("""
            SELECT COUNT(*) FROM google_places_churches 
            WHERE (website IS NULL OR website = '') 
            AND (phone IS NULL OR phone = '')
        """)
        no_contact = cursor.fetchone()[0]
        if no_contact > 0:
            issues.append(f"   {no_contact} churches with no website or phone")
        
        # Duplicate names in same state
        cursor.execute("""
            SELECT state, name, COUNT(*) as count
            FROM google_places_churches
            WHERE state IS NOT NULL
            GROUP BY state, name
            HAVING count > 1
            ORDER BY count DESC
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            issues.append(f"   {len(duplicates)} potential duplicate church names")
            issues.append(f"      (These may be legitimate - e.g., same name, different cities)")
            for state, name, count in duplicates[:5]:
                # Get cities for these duplicates
                cursor.execute("""
                    SELECT city, address 
                    FROM google_places_churches 
                    WHERE state = ? AND name = ?
                    LIMIT 3
                """, (state, name))
                cities = cursor.fetchall()
                city_list = [f"{city} ({addr[:30]}...)" if addr else city for city, addr in cities]
                issues.append(f"      - {state}: '{name}' ({count}x) in {', '.join(city_list[:2])}")
                if len(city_list) > 2:
                    issues.append(f"        ... and {len(city_list) - 2} more locations")
        
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("   ✅ No issues found!")
        
        # 6. Sample churches
        print(f"\n📋 Sample Churches (first 5):")
        cursor.execute("""
            SELECT name, city, state, website, phone
            FROM google_places_churches
            LIMIT 5
        """)
        for name, city, state, website, phone in cursor.fetchall():
            print(f"   • {name}")
            print(f"     📍 {city}, {state}")
            if website:
                print(f"     🌐 {website}")
            if phone:
                print(f"     📞 {phone}")
            print()
        
        print("="*80)
        print(f"✅ Validation complete! Database has {total} churches")
        print("="*80)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error validating database: {e}")
        return False

if __name__ == '__main__':
    validate_database()
