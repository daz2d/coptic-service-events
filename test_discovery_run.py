#!/usr/bin/env python3
"""
Test discovery run to see what's failing
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Setup logging to see everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_discovery.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

load_dotenv()

from src.global_church_discovery import GlobalChurchDatabase
from src.event_database import EventDatabase

logger = logging.getLogger(__name__)

def main():
    """Run discovery for just a few states to test"""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        logger.error("❌ GOOGLE_MAPS_API_KEY not found in environment!")
        return
    
    logger.info("✅ API key found")
    logger.info(f"   Key starts with: {api_key[:10]}...")
    
    # Initialize
    logger.info("Initializing discovery...")
    discovery = GlobalChurchDatabase(api_key)
    
    # Test just NJ first
    logger.info("\n🧪 TESTING: New Jersey only")
    logger.info("="*60)
    
    try:
        # Manually search NJ
        churches = discovery.discovery.search_churches_in_state('NJ', max_results=50)
        logger.info(f"✅ Found {len(churches)} churches in NJ")
        
        for i, church in enumerate(churches[:5], 1):
            logger.info(f"   {i}. {church.name}")
            logger.info(f"      📍 {getattr(church, 'city', 'Unknown')}, {getattr(church, 'state', '?')}")
            logger.info(f"      🌐 {church.website or 'No website'}")
        
        # Now save to DB
        logger.info(f"\n💾 Saving to database...")
        db = EventDatabase()
        
        for church in churches:
            try:
                db.add_church(
                    name=church.name,
                    address=church.address,
                    city=getattr(church, 'city', ''),
                    state=getattr(church, 'state', ''),
                    country=getattr(church, 'country', 'USA'),
                    website=church.website,
                    latitude=church.latitude,
                    longitude=church.longitude,
                    place_id=church.place_id,
                    phone=getattr(church, 'phone', None)
                )
            except Exception as e:
                logger.error(f"   ❌ Failed to save {church.name}: {e}")
        
        logger.info(f"✅ Saved {len(churches)} churches to database")
        
    except Exception as e:
        logger.error(f"❌ ERROR: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
