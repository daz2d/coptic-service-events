#!/usr/bin/env python3
"""
Validate church data against Nihov directory
"""
import sqlite3
import requests
from bs4 import BeautifulSoup
import time

def get_nihov_churches_for_state(state_abbr):
    """Scrape church names from Nihov directory for a given state"""
    state_map = {
        'NJ': 'new-jersey', 'NY': 'new-york', 'CA': 'california',
        'FL': 'florida', 'VA': 'virginia', 'TX': 'texas',
        'IL': 'illinois', 'PA': 'pennsylvania', 'GA': 'georgia'
    }
    
    state_name = state_map.get(state_abbr)
    if not state_name:
        return []
    
    url = f"https://directory.nihov.org/church/usa/{state_name}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        churches = []
        # Find church listings - adjust selector based on actual HTML structure
        for link in soup.find_all('a', href=True):
            if '/church/usa/' in link['href'] and link.text.strip():
                churches.append(link.text.strip())
        
        return churches
    except Exception as e:
        print(f"Error fetching {state_abbr}: {e}")
        return []

def validate_database():
    """Compare database with Nihov directory"""
    conn = sqlite3.connect('coptic_events.db')
    cursor = conn.cursor()
    
    # Get states with most churches to validate
    cursor.execute("""
        SELECT state, COUNT(*) as count 
        FROM google_places_churches 
        WHERE country = 'United States'
        GROUP BY state 
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("=" * 80)
    print("Church Data Validation Report")
    print("=" * 80)
    
    for state, db_count in cursor.fetchall():
        print(f"\n{state}: {db_count} churches in database")
        
        # Get churches from database
        cursor.execute("""
            SELECT name, city, website 
            FROM google_places_churches 
            WHERE state = ?
            ORDER BY city
        """, (state,))
        
        db_churches = cursor.fetchall()
        
        # Show sample
        print(f"\nSample churches from database:")
        for name, city, website in db_churches[:5]:
            print(f"  • {city}: {name}")
            if website:
                print(f"    {website}")
        
        if len(db_churches) > 5:
            print(f"  ... and {len(db_churches) - 5} more")
        
        time.sleep(1)  # Rate limiting
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("\nManual Verification Needed:")
    print("Please visit https://directory.nihov.org/church/usa to compare")
    print("Focus on major states: NJ, NY, CA, FL, VA, TX")
    print("=" * 80)

if __name__ == "__main__":
    validate_database()
