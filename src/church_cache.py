"""
Church Directory Cache Manager
Caches discovered churches to avoid re-fetching from directory every time
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ChurchCache:
    """Manages caching of discovered churches from directories"""
    
    def __init__(self, cache_file: str = 'church_cache.json'):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
            logger.info(f"Cache saved to {self.cache_file}")
        except Exception as e:
            logger.error(f"Could not save cache: {e}")
    
    def get_churches_for_state(self, state: str, max_age_hours: int = 24) -> Optional[List[Dict]]:
        """Get cached churches for a state if not expired"""
        cache_key = f"state_{state.upper()}"
        
        if cache_key not in self.cache:
            return None
        
        cached_data = self.cache[cache_key]
        
        # Check if expired
        cached_time = datetime.fromisoformat(cached_data['timestamp'])
        age = datetime.now() - cached_time
        
        if age > timedelta(hours=max_age_hours):
            logger.info(f"Cache for {state} expired ({age.total_seconds() / 3600:.1f} hours old)")
            return None
        
        logger.info(f"Using cached data for {state} ({len(cached_data['churches'])} churches, {age.total_seconds() / 3600:.1f} hours old)")
        return cached_data['churches']
    
    def set_churches_for_state(self, state: str, churches: List[Dict]):
        """Cache churches for a state"""
        cache_key = f"state_{state.upper()}"
        
        self.cache[cache_key] = {
            'state': state.upper(),
            'timestamp': datetime.now().isoformat(),
            'count': len(churches),
            'churches': churches
        }
        
        self._save_cache()
        logger.info(f"Cached {len(churches)} churches for {state}")
    
    def get_church_contact(self, church_id: str, max_age_hours: int = 168) -> Optional[Dict]:
        """Get cached contact info for a specific church (1 week default)"""
        cache_key = f"contact_{church_id}"
        
        if cache_key not in self.cache:
            return None
        
        cached_data = self.cache[cache_key]
        
        # Check if expired
        cached_time = datetime.fromisoformat(cached_data['timestamp'])
        age = datetime.now() - cached_time
        
        if age > timedelta(hours=max_age_hours):
            return None
        
        return cached_data['contact_info']
    
    def set_church_contact(self, church_id: str, contact_info: Dict):
        """Cache contact info for a specific church"""
        cache_key = f"contact_{church_id}"
        
        self.cache[cache_key] = {
            'church_id': church_id,
            'timestamp': datetime.now().isoformat(),
            'contact_info': contact_info
        }
        
        # Save every 50 contact updates to avoid too frequent writes
        if len([k for k in self.cache.keys() if k.startswith('contact_')]) % 50 == 0:
            self._save_cache()
    
    def clear_expired(self, max_age_hours: int = 168):
        """Clear expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, value in self.cache.items():
            if 'timestamp' in value:
                cached_time = datetime.fromisoformat(value['timestamp'])
                age = now - cached_time
                if age > timedelta(hours=max_age_hours):
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        state_caches = [k for k in self.cache.keys() if k.startswith('state_')]
        contact_caches = [k for k in self.cache.keys() if k.startswith('contact_')]
        
        total_churches = 0
        for key in state_caches:
            if 'count' in self.cache[key]:
                total_churches += self.cache[key]['count']
        
        return {
            'states_cached': len(state_caches),
            'contacts_cached': len(contact_caches),
            'total_churches': total_churches,
            'cache_file': self.cache_file,
            'cache_size_kb': os.path.getsize(self.cache_file) / 1024 if os.path.exists(self.cache_file) else 0
        }


if __name__ == '__main__':
    # Test the cache
    logging.basicConfig(level=logging.INFO)
    
    cache = ChurchCache()
    stats = cache.get_stats()
    
    print("\n" + "="*70)
    print("CHURCH CACHE STATISTICS")
    print("="*70)
    print(f"States cached: {stats['states_cached']}")
    print(f"Contacts cached: {stats['contacts_cached']}")
    print(f"Total churches: {stats['total_churches']}")
    print(f"Cache file: {stats['cache_file']}")
    print(f"Cache size: {stats['cache_size_kb']:.1f} KB")
    print("="*70)
