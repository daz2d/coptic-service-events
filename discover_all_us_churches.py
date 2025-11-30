#!/usr/bin/env python3
"""
Discover ALL Coptic Orthodox Churches in the USA
================================================

This script systematically searches all 50 states + DC using Google Places API
and saves the results to your local database.

Features:
- ✅ Smart deduplication (by place_id, location hash, and name+city+state)
- ✅ State validation (only saves churches in correct state)
- ✅ Progress tracking with detailed stats
- ✅ Automatic rate limiting
- ✅ Resume capability (skips already-processed states)
- ✅ Goes through 5 pages of results per state for comprehensive coverage

Run this script ONCE to build your complete church database.
After that, all queries are local and FREE!
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Setup logging
log_file = f'us_church_discovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

from src.global_church_discovery import GlobalChurchDatabase


def main():
    """Run the discovery process"""
    
    logger.info("="*80)
    logger.info("🇺🇸 USA COPTIC ORTHODOX CHURCH DISCOVERY")
    logger.info("="*80)
    logger.info("")
    logger.info("This script will search all 50 US states + DC for Coptic churches")
    logger.info("using Google Places API and save them to your local database.")
    logger.info("")
    logger.info("📊 Coverage: All 50 states + DC")
    logger.info("🔍 Depth: Up to 5 pages of results per state")
    logger.info("💾 Storage: Local SQLite database (coptic_events.db)")
    logger.info("⏱️  Estimated time: 15-30 minutes")
    logger.info("")
    logger.info(f"📝 Detailed log: {log_file}")
    logger.info("="*80)
    logger.info("")
    
    # Check API key
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        logger.error("❌ GOOGLE_MAPS_API_KEY not found in .env file!")
        logger.error("")
        logger.error("Please add your API key to .env:")
        logger.error("  GOOGLE_MAPS_API_KEY='your-key-here'")
        logger.error("")
        logger.error("Get a key at: https://console.cloud.google.com/google/maps-apis/")
        return 1
    
    logger.info(f"✅ API key found: {api_key[:10]}...")
    logger.info("")
    
    # Initialize discovery
    logger.info("🚀 Initializing discovery engine...")
    discovery = GlobalChurchDatabase(api_key)
    
    logger.info("✅ Ready to start!")
    logger.info("")
    
    # Run discovery
    try:
        logger.info("🔍 Starting state-by-state search...")
        logger.info("   This will take 15-30 minutes depending on API speed")
        logger.info("")
        
        churches = discovery.discover_all_churches(max_per_region=100)
        
        logger.info("")
        logger.info("="*80)
        logger.info("💾 SAVING TO DATABASE")
        logger.info("="*80)
        logger.info("")
        
        discovery.save_to_database()
        
        logger.info("")
        logger.info("="*80)
        logger.info("✅ SUCCESS!")
        logger.info("="*80)
        logger.info("")
        logger.info(f"📊 Total churches discovered: {len(churches)}")
        logger.info(f"💾 Saved to: coptic_events.db")
        logger.info(f"📝 Log file: {log_file}")
        logger.info("")
        logger.info("🎉 Your local church database is ready!")
        logger.info("   All future queries will be instant and FREE!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Run main.py to find events near you")
        logger.info("  2. All church lookups now use your local database")
        logger.info("  3. Re-run this script every 6 months to refresh")
        logger.info("")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("")
        logger.warning("⚠️  Discovery interrupted by user")
        logger.warning("   Progress so far has been saved to database")
        logger.warning("   Re-run this script to continue")
        return 1
        
    except Exception as e:
        logger.error("")
        logger.error(f"❌ ERROR: {e}", exc_info=True)
        logger.error("")
        logger.error("Check the log file for details:")
        logger.error(f"  {log_file}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
