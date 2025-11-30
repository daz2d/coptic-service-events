#!/usr/bin/env python3
"""
Coptic Orthodox Church Service Events Bot
Main entry point for discovering and managing service/volunteer events
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from src.config_manager import ConfigManager
from src.location_service import LocationService
from src.event_scraper import EventScraper
from src.calendar_integration import GoogleCalendarIntegration
from src.event_database import EventDatabase
from src.scheduler import EventScheduler
from src.event_selector import EventSelector
from src.html_generator import HTMLCalendarGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coptic_events.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class CopticEventsBot:
    """Main bot orchestrator"""
    
    def __init__(self, config_path='config.json'):
        self.config = ConfigManager(config_path)
        self.location_service = LocationService(self.config)
        self.db = EventDatabase()
        self.scraper = EventScraper(self.config, self.location_service)
        self.calendar = GoogleCalendarIntegration(self.config)
        self.scheduler = EventScheduler(self.config, self.run_discovery)
        self.event_selector = EventSelector()
        self.html_generator = HTMLCalendarGenerator()
        
    def run_discovery(self):
        """Main discovery process"""
        logger.info("Starting event discovery...")
        
        # Get location
        location = self.location_service.get_location()
        logger.info(f"Searching for events near: {location}")
        
        # Scrape events
        events = self.scraper.discover_events()
        logger.info(f"Found {len(events)} events")
        
        # Filter new events
        new_events = []
        for event in events:
            if not self.db.event_exists(event):
                self.db.add_event(event)
                new_events.append(event)
        
        logger.info(f"Found {len(new_events)} new events")
        
        # Add to Google Calendar
        if self.config.get('google_calendar.enabled') and new_events:
            added_count = self.calendar.add_events(new_events)
            logger.info(f"Added {added_count} events to Google Calendar")
        
        # Send notifications
        if new_events and self.config.get('notifications.new_event_alerts'):
            self.send_notifications(new_events)
        
        # Return ALL events for display, not just new ones
        return events
    
    def send_notifications(self, events):
        """Send notifications for new events"""
        logger.info(f"Sending notifications for {len(events)} new events")
        # TODO: Implement email/push notifications
        
    def start_scheduled_runs(self):
        """Start the scheduler for automatic runs"""
        logger.info("Starting scheduled event discovery...")
        self.scheduler.start()
        
    def run_once(self):
        """Run discovery once and exit"""
        events = self.run_discovery()
        
        # Interactive selection
        selected_events = self.event_selector.select_events(events)
        
        if selected_events:
            # Generate HTML calendar
            html_file = self.html_generator.generate(selected_events)
            print(f"\n✅ Generated interactive calendar: {html_file}")
            print(f"\nOpen this file in your browser to:")
            print("  • View all selected events")
            print("  • Add events to Google Calendar with one click")
            print("  • See full event details")
            
            # Also print summary
            self.print_summary(selected_events)
        
        return events
    
    def print_summary(self, events):
        """Print event summary"""
        print("\n" + "="*60)
        print(f"COPTIC ORTHODOX SERVICE EVENTS - {datetime.now().strftime('%Y-%m-%d')}")
        print("="*60 + "\n")
        
        if not events:
            print("No new events found.")
            return
        
        for i, event in enumerate(events, 1):
            print(f"{i}. {event.title}")
            print(f"   Church: {event.church_name}")
            print(f"   Date: {event.date} at {event.time}")
            print(f"   Location: {event.location}")
            print(f"   Type: {event.event_type}")
            if event.description:
                print(f"   Description: {event.description[:100]}...")
            if event.registration_link:
                print(f"   Register: {event.registration_link}")
            print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Coptic Orthodox Service Events Bot')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule')
    parser.add_argument('--config', default='config.json', help='Config file path')
    
    args = parser.parse_args()
    
    bot = CopticEventsBot(args.config)
    
    if args.schedule:
        bot.start_scheduled_runs()
        # Keep running
        import time
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
    else:
        bot.run_once()


if __name__ == '__main__':
    main()
