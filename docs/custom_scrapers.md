# Adding Custom Website Scrapers

This guide explains how to add custom scrapers for specific church or diocese websites.

## Overview

The event scraper system uses a modular approach. You can create custom scrapers for specific websites by extending the base `EventScraper` class.

## Creating a Custom Scraper

### Step 1: Create a new scraper file

Create a new file in `src/scrapers/` directory (you may need to create this directory):

```bash
mkdir -p src/scrapers
```

### Step 2: Implement the scraper

Here's a template for a custom scraper:

```python
"""Scraper for [Church/Diocese Name] website"""

import logging
from bs4 import BeautifulSoup
from typing import List
from src.event_model import ServiceEvent

logger = logging.getLogger(__name__)


class CustomChurchScraper:
    """Scraper for specific church website"""
    
    def __init__(self, session):
        self.session = session
        self.base_url = "https://example-church.org"
    
    def scrape_events(self) -> List[ServiceEvent]:
        """Scrape events from the website"""
        events = []
        
        try:
            # Fetch the events page
            url = f"{self.base_url}/events"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find event containers (customize based on website structure)
            event_containers = soup.find_all('div', class_='event-item')
            
            for container in event_containers:
                event = self._parse_event(container)
                if event:
                    events.append(event)
            
            logger.info(f"Found {len(events)} events from {self.base_url}")
            
        except Exception as e:
            logger.error(f"Error scraping {self.base_url}: {e}")
        
        return events
    
    def _parse_event(self, container) -> ServiceEvent:
        """Parse individual event from HTML"""
        try:
            # Extract event details (customize based on HTML structure)
            title = container.find('h3', class_='event-title').get_text().strip()
            date = container.find('span', class_='event-date').get_text().strip()
            time = container.find('span', class_='event-time').get_text().strip()
            location = container.find('span', class_='event-location').get_text().strip()
            description = container.find('div', class_='event-description').get_text().strip()
            
            # Create ServiceEvent object
            event = ServiceEvent(
                title=title,
                church_name="St. Mark Coptic Orthodox Church",  # Update
                date=self._parse_date(date),  # Convert to ISO format
                time=self._parse_time(time),  # Convert to HH:MM format
                location=location,
                event_type=self._determine_event_type(title, description),
                description=description,
                source_url=f"{self.base_url}/events"
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> str:
        """Convert date string to ISO format (YYYY-MM-DD)"""
        from datetime import datetime
        
        # Example: "December 15, 2024" -> "2024-12-15"
        # Adjust based on actual format
        try:
            dt = datetime.strptime(date_str, "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except:
            logger.warning(f"Could not parse date: {date_str}")
            return date_str
    
    def _parse_time(self, time_str: str) -> str:
        """Convert time string to HH:MM format"""
        from datetime import datetime
        
        # Example: "2:00 PM" -> "14:00"
        try:
            dt = datetime.strptime(time_str, "%I:%M %p")
            return dt.strftime("%H:%M")
        except:
            logger.warning(f"Could not parse time: {time_str}")
            return time_str
    
    def _determine_event_type(self, title: str, description: str) -> str:
        """Determine event type from title and description"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['mission', 'trip', 'travel']):
            return 'mission_trips_domestic' if 'domestic' in text else 'mission_trips_international'
        elif any(word in text for word in ['food', 'pantry', 'hunger']):
            return 'food_pantry'
        elif any(word in text for word in ['homeless', 'shelter']):
            return 'homeless_outreach'
        elif any(word in text for word in ['hospital', 'visit', 'sick']):
            return 'hospital_visits'
        elif any(word in text for word in ['nursing', 'elderly']):
            return 'nursing_home'
        elif any(word in text for word in ['youth', 'teen', 'young']):
            return 'youth_service'
        else:
            return 'community_service'
```

### Step 3: Register the scraper

Update `src/event_scraper.py` to include your custom scraper:

```python
# Add import at the top
from src.scrapers.custom_church_scraper import CustomChurchScraper

# In the discover_events method, add:
def discover_events(self) -> List[ServiceEvent]:
    events = []
    
    # ... existing code ...
    
    # Add custom scrapers
    custom_scraper = CustomChurchScraper(self.session)
    events.extend(custom_scraper.scrape_events())
    
    return events
```

## Example: Diocese Website Scraper

For a diocese website that lists multiple churches' events:

```python
class DioceseScraper:
    def scrape_events(self) -> List[ServiceEvent]:
        events = []
        
        # Get list of churches
        churches = self._get_church_list()
        
        for church in churches:
            # Scrape each church's events
            church_events = self._scrape_church_events(church)
            events.extend(church_events)
        
        return events
```

## Tips for Website-Specific Scrapers

1. **Inspect the HTML**: Use browser developer tools to understand the website structure
2. **Look for patterns**: Find consistent CSS classes or IDs used for events
3. **Handle variations**: Different events might have different HTML structures
4. **Test thoroughly**: Make sure your scraper handles missing fields gracefully
5. **Respect rate limits**: Add delays between requests if needed
6. **Cache results**: Don't re-scrape data unnecessarily

## Common Patterns

### WordPress Sites
Many churches use WordPress with event plugins:

```python
# Look for these common classes:
events = soup.find_all('div', class_='tribe-events-list-event-row')
events = soup.find_all('article', class_='event')
```

### Facebook Events (via Page)
If a church publishes events on Facebook, you might need to use Facebook's Graph API (requires API key).

### Google Calendar Embed
Some churches embed Google Calendar. You can use the Calendar API to fetch those events directly.

## Need Help?

- Check `src/event_scraper.py` for the base implementation
- Look at example scrapers in `examples/scrapers/`
- Read the BeautifulSoup documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
