#!/usr/bin/env python3
"""
Retry Discovery for Failed States Only
"""

import logging
from src.global_church_discovery import GlobalChurchDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Failed states from the log
FAILED_STATES = [
    'Ohio', 'Oregon', 'Pennsylvania', 'South Dakota', 
    'Texas', 'Vermont', 'Virginia', 'Washington', 'Wyoming'
]

def main():
    print("\n" + "="*80)
    print("RETRYING FAILED STATES")
    print("="*80)
    print(f"\nStates to retry: {', '.join(FAILED_STATES)}\n")
    
    discovery = GlobalChurchDatabase()
    
    # Run discovery for failed states only
    discovery.discover_all_churches(states_filter=FAILED_STATES)
    
    print("\n" + "="*80)
    print("✅ RETRY COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()
