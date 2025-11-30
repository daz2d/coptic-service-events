"""Test discovery with location validation"""
from src.global_church_discovery import GlobalChurchDatabase
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test with just 3 states to verify location filtering
test_regions = [
    ('NJ', 'New Jersey'),
    ('NY', 'New York'), 
    ('CA', 'California')
]

print("\n" + "="*80)
print("TESTING LOCATION VALIDATION")
print("="*80)
print(f"\nSearching 3 states: NJ, NY, CA")
print("Will verify each church is in the correct state\n")

db = GlobalChurchDatabase()
db.REGIONS = test_regions  # Override with test regions

# Discover
churches = db.discover_all_churches(max_per_region=30)

# Show results by state
print("\n" + "="*80)
print("RESULTS BY STATE:")
print("="*80)

by_state = {}
for church in churches:
    state = getattr(church, 'state', 'Unknown')
    if state not in by_state:
        by_state[state] = []
    by_state[state].append(church)

for state, churches_list in sorted(by_state.items()):
    print(f"\n{state}: {len(churches_list)} churches")
    for church in churches_list[:3]:
        print(f"   - {church.name[:50]}")
        print(f"     {getattr(church, 'city', 'N/A')}, {state}")

# Save
db.save_to_database()

print("\n" + "="*80)
print(f"✅ Test complete! {len(churches)} total churches")
print("="*80)
