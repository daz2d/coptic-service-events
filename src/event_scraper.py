"""Event scraper for discovering service and social events"""

import logging
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from src.event_model import ServiceEvent
from src.diocese_scraper import DioceseScraper
from src.church_scraper import MultiThreadedScraper

logger = logging.getLogger(__name__)


class EventScraper:
    """
    Discovers events using diocese-first approach:
    1. Detect user's diocese based on location
    2. Scrape diocese directory to get list of churches
    3. Multi-threaded scraping of all churches within radius
    4. Aggregate and filter events
    """
    
    def __init__(self, config, location_service):
        self.config = config
        self.location_service = location_service
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('scraping.user_agent', 'CopticServiceEventsBot/1.0')
        })
        
        # Initialize specialized scrapers
        self.diocese_scraper = DioceseScraper(config, location_service)
        self.multi_threaded_scraper = MultiThreadedScraper(
            self.session, 
            max_workers=config.get('scraping_strategy.max_workers', 10)
        )
    
    def discover_events(self) -> List[ServiceEvent]:
        """
        Main discovery method using diocese-first strategy
        """
        events = []
        
        # Get user location
        lat, lon, location_name = self.location_service.get_location()
        radius = self.config.get('location.radius_miles', 50)
        
        logger.info(f"🔍 Searching for events within {radius} miles of {location_name}")
        
        # Check if we should use diocese-first strategy
        if self.config.get('scraping_strategy.start_with_diocese', True):
            events = self._discover_via_diocese(lat, lon, radius, location_name)
        else:
            # Fallback to direct church scraping
            events = self._discover_via_direct_scraping()
        
        # Filter by distance
        events = self._filter_by_distance(events, lat, lon, radius)
        
        # Filter by preferences
        events = self._filter_by_preferences(events)
        
        logger.info(f"✅ Discovery complete: {len(events)} events found")
        
        return events
    
    def _discover_via_diocese(self, lat: float, lon: float, radius: float, location_name: str) -> List[ServiceEvent]:
        """
        Diocese-first discovery strategy using global church directory
        """
        events = []
        
        # Step 1: Use global church directory
        from src.church_directory import ChurchDirectoryScraper
        
        directory_scraper = ChurchDirectoryScraper(self.session)
        
        # Extract state from location if possible
        state = None
        if ',' in location_name:
            parts = location_name.split(',')
            if len(parts) >= 2:
                state = parts[1].strip().upper()
        
        logger.info(f"🌍 Using global Coptic church directory")
        
        # Discover all churches (or filter by state if known)
        if state:
            churches_list = directory_scraper.discover_churches_by_location(state=state, country='USA')
            logger.info(f"📋 Found {len(churches_list)} churches in {state}")
        else:
            churches_list = directory_scraper.discover_all_churches()
            logger.info(f"📋 Found {len(churches_list)} churches globally")
        
        # Convert to our church format
        churches = []
        for church_data in churches_list:
            church = {
                'name': church_data['name'],
                'url': church_data.get('url'),
                'city': church_data.get('city'),
                'state': church_data.get('state'),
                'diocese': f"{church_data.get('state')} Region" if church_data.get('state') else 'Unknown'
            }
            churches.append(church)
        
        # Filter by distance
        churches = self.diocese_scraper.filter_churches_by_distance(
            churches, lat, lon, radius
        )
        
        logger.info(f"📍 {len(churches)} churches within {radius} miles")
        
        # Only scrape churches that have website URLs
        churches_with_websites = [c for c in churches if c.get('url')]
        logger.info(f"🌐 {len(churches_with_websites)} churches have websites")
        
        # Multi-threaded scraping
        if churches_with_websites and self.config.get('scraping_strategy.multi_threaded', True):
            events = self.multi_threaded_scraper.scrape_all_churches(churches_with_websites)
        
        return events
    
    def _discover_via_direct_scraping(self) -> List[ServiceEvent]:
        """
        Fallback: Direct scraping without diocese discovery
        """
        events = []
        
        # Scrape from configured sources
        events.extend(self._scrape_diocese_websites())
        events.extend(self._scrape_church_websites())
        
        return events
    
    def _scrape_diocese_websites(self) -> List[ServiceEvent]:
        """Scrape events from diocese websites"""
        events = []
        diocese_websites = self.config.get('data_sources.diocese_websites', {})
        
        for diocese_key, diocese_url in diocese_websites.items():
            try:
                logger.info(f"Scraping diocese website: {diocese_url}")
                events.extend(self._scrape_generic_website(diocese_url))
            except Exception as e:
                logger.error(f"Error scraping {diocese_url}: {e}")
        
        return events
    
    def _scrape_church_websites(self) -> List[ServiceEvent]:
        """Scrape events from individual church websites"""
        events = []
        church_urls = self.config.get('data_sources.church_websites', [])
        
        for url in church_urls:
            try:
                logger.info(f"Scraping church website: {url}")
                events.extend(self._scrape_generic_website(url))
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
        
        return events
    
    def _scrape_generic_website(self, url: str) -> List[ServiceEvent]:
        """Generic website scraper - adapt based on common patterns"""
        events = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Example: Look for common event patterns
            # This is a template - needs to be customized per website
            
            # Look for keywords related to service events
            service_keywords = [
                'service', 'volunteer', 'outreach', 'mission', 
                'food pantry', 'homeless', 'charity', 'community'
            ]
            
            # Example parsing logic (needs customization)
            event_containers = soup.find_all(['article', 'div'], 
                                            class_=lambda x: x and any(k in str(x).lower() for k in ['event', 'post', 'news']))
            
            for container in event_containers:
                text = container.get_text().lower()
                
                # Check if contains service-related keywords
                if not any(keyword in text for keyword in service_keywords):
                    continue
                
                # Try to extract event details (this is very basic)
                # Real implementation would need site-specific parsing
                event = self._parse_event_from_container(container, url)
                if event:
                    events.append(event)
            
        except Exception as e:
            logger.error(f"Error in generic scraper for {url}: {e}")
        
        return events
    
    def _parse_event_from_container(self, container, source_url: str) -> ServiceEvent:
        """Parse event details from HTML container"""
        # This is a placeholder - real implementation needs site-specific logic
        try:
            title = container.find(['h1', 'h2', 'h3', 'h4'])
            title_text = title.get_text().strip() if title else "Unknown Event"
            
            # More parsing logic would go here...
            # For now, return None as this is just a template
            return None
            
        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            return None
    
    def _filter_by_distance(self, events: List[ServiceEvent], 
                           lat: float, lon: float, radius: float) -> List[ServiceEvent]:
        """Filter events by distance from location"""
        filtered = []
        
        for event in events:
            if event.latitude and event.longitude:
                distance = self.location_service.calculate_distance(
                    lat, lon, event.latitude, event.longitude
                )
                
                if distance <= radius:
                    filtered.append(event)
            else:
                # Include events without coordinates (geocode later)
                filtered.append(event)
        
        return filtered
    
    def _filter_by_preferences(self, events: List[ServiceEvent]) -> List[ServiceEvent]:
        """Filter events based on user preferences"""
        filtered = []
        
        include_service = self.config.get('event_preferences.include_service_events', True)
        include_missions = self.config.get('event_preferences.include_mission_trips', True)
        include_social = self.config.get('event_preferences.include_social_events', True)
        allowed_types = self.config.get('event_preferences.event_types', [])
        
        # Social event types
        social_types = {'festival', 'social_gathering', 'retreat', 'conference', 
                       'sports_event', 'cultural_event', 'family_event'}
        
        # Service event types
        service_types = {'food_pantry', 'homeless_outreach', 'hospital_visits', 
                        'nursing_home', 'youth_service', 'community_service', 'charity_events'}
        
        for event in events:
            # Filter by mission trips
            if event.is_mission_trip and not include_missions:
                continue
            
            # Filter by event category
            if event.event_type in social_types and not include_social:
                continue
            
            if event.event_type in service_types and not include_service:
                continue
            
            # Filter by specific event types if configured
            if allowed_types and event.event_type not in allowed_types:
                continue
            
            filtered.append(event)
        
        return filtered
