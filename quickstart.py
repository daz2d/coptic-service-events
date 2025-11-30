#!/usr/bin/env python3
"""
Quick start script - Tests the bot with mock data
"""

import sys
from datetime import datetime

# Add examples to path
sys.path.insert(0, '.')

from examples.mock_events import get_mock_events
from src.config_manager import ConfigManager


def main():
    print("\n" + "="*70)
    print("COPTIC ORTHODOX SERVICE EVENTS BOT - QUICK START")
    print("="*70 + "\n")
    
    print("This is a demonstration using mock data.")
    print("To use real data, you'll need to:")
    print("  1. Configure your location in config.json")
    print("  2. Add church/diocese websites to data_sources")
    print("  3. Set up Google Calendar API (see docs/google_calendar_setup.md)")
    print("  4. Optionally create custom scrapers for specific websites\n")
    
    # Get mock events
    events = get_mock_events()
    
    print(f"Found {len(events)} upcoming service opportunities:\n")
    print("-"*70 + "\n")
    
    for i, event in enumerate(events, 1):
        print(f"📅 {i}. {event.title}")
        print(f"   ⛪ Church: {event.church_name}")
        print(f"   📍 Location: {event.location}")
        print(f"   🕐 When: {event.date} at {event.time}")
        print(f"   🏷️  Type: {event.event_type.replace('_', ' ').title()}")
        
        if event.is_mission_trip:
            print(f"   ✈️  MISSION TRIP to {event.destination}")
            print(f"   ⏱️  Duration: {event.trip_duration_days} days")
            print(f"   💰 Cost: {event.cost}")
        
        if event.spots_available:
            print(f"   👥 Spots Available: {event.spots_available}" + 
                  (f"/{event.capacity}" if event.capacity else ""))
        
        if event.contact_person:
            print(f"   👤 Contact: {event.contact_person}")
            if event.contact_email:
                print(f"   📧 {event.contact_email}")
        
        if event.registration_link:
            print(f"   🔗 Register: {event.registration_link}")
        
        if event.registration_deadline:
            print(f"   ⚠️  Registration Deadline: {event.registration_deadline}")
        
        print()
    
    print("-"*70)
    print("\nNext steps:")
    print("  • Edit config.json to set your location")
    print("  • Run: python main.py --once")
    print("  • For scheduled runs: python main.py --schedule")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
