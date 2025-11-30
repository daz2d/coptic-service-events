"""Multi-threaded church event scraper"""

import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from src.event_model import ServiceEvent

logger = logging.getLogger(__name__)


class ChurchEventScraper:
    """Scrapes events from individual church websites"""
    
    def __init__(self, session):
        self.session = session
    
    def scrape_church_events(self, church: Dict) -> List[ServiceEvent]:
        """Scrape all events from a church website"""
        events = []
        
        if not church.get('url'):
            logger.debug(f"No URL for church: {church.get('name')}")
            return events
        
        try:
            logger.info(f"Scraping events from {church['name']}: {church['url']}")
            
            # Try common event page patterns
            event_urls = self._get_event_page_urls(church['url'])
            
            for event_url in event_urls:
                try:
                    response = self.session.get(event_url, timeout=5)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Parse events from page
                    page_events = self._parse_events_from_page(soup, church, event_url)
                    events.extend(page_events)
                    
                    if page_events:
                        logger.info(f"Found {len(page_events)} events from {event_url}")
                        break  # Found events, no need to try other URLs
                    
                except Exception as e:
                    logger.debug(f"Error scraping {event_url}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping church {church.get('name')}: {e}")
        
        return events
    
    def _get_event_page_urls(self, base_url: str) -> List[str]:
        """Generate common event page URL patterns"""
        urls = [base_url]  # Try homepage first
        
        # Common event page paths
        event_paths = [
            '/events',
            '/calendar',
            '/events-calendar',
            '/upcoming-events',
            '/news-events',
            '/activities',
            '/ministries/events',
            '/community/events'
        ]
        
        for path in event_paths:
            urls.append(f"{base_url.rstrip('/')}{path}")
        
        return urls
    
    def _parse_events_from_page(self, soup: BeautifulSoup, church: Dict, source_url: str) -> List[ServiceEvent]:
        """Parse events from HTML page"""
        events = []
        
        # Look for calendar/event plugins (WordPress, etc.)
        event_containers = self._find_event_containers(soup)
        
        for container in event_containers:
            event = self._parse_event_container(container, church, source_url)
            if event:
                events.append(event)
        
        return events
    
    def _find_event_containers(self, soup: BeautifulSoup) -> List:
        """Find HTML elements that likely contain events"""
        containers = []
        
        # Common event container patterns
        patterns = [
            # Calendar plugins
            {'name': 'div', 'class_': lambda x: x and 'tribe-events' in str(x).lower()},
            {'name': 'article', 'class_': lambda x: x and 'event' in str(x).lower()},
            {'name': 'div', 'class_': lambda x: x and 'event-item' in str(x).lower()},
            {'name': 'div', 'class_': lambda x: x and 'calendar-event' in str(x).lower()},
            # WordPress
            {'name': 'article', 'class_': 'post'},
            {'name': 'div', 'class_': 'post'},
            # Generic
            {'name': 'div', 'class_': lambda x: x and any(word in str(x).lower() for word in ['event', 'activity', 'upcoming'])},
        ]
        
        for pattern in patterns:
            found = soup.find_all(pattern['name'], class_=pattern.get('class_'))
            if found:
                containers.extend(found)
                if len(containers) > 0:
                    break  # Found some containers, stop searching
        
        return containers[:50]  # Limit to 50 to avoid processing too much
    
    def _parse_event_container(self, container, church: Dict, source_url: str) -> ServiceEvent:
        """Parse individual event from HTML container"""
        try:
            # Extract title
            title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'a'])
            if not title_elem:
                return None
            
            title = title_elem.get_text().strip()
            
            # Skip if title is empty or too short
            if not title or len(title) < 3:
                return None
            
            # Extract date and time
            date_str, time_str = self._extract_date_time(container)
            if not date_str:
                date_str = "TBD"  # Mark as To Be Determined instead of skipping
            if not time_str:
                time_str = "TBD"
            
            # Extract description
            description = self._extract_description(container)
            
            # Extract location
            location = self._extract_location(container, church)
            
            # Determine event type
            event_type = self._determine_event_type(title, description)
            
            # Check if it's a mission trip
            is_mission_trip = self._is_mission_trip(title, description)
            
            # Extract additional details
            contact = self._extract_contact_info(container)
            registration_link = self._extract_registration_link(container, source_url)
            
            event = ServiceEvent(
                title=title,
                church_name=church['name'],
                date=date_str,
                time=time_str,
                location=location,
                event_type=event_type,
                description=description,
                diocese=church.get('diocese'),
                source_url=source_url,
                is_mission_trip=is_mission_trip,
                contact_person=contact.get('person'),
                contact_email=contact.get('email'),
                contact_phone=contact.get('phone'),
                registration_link=registration_link,
                latitude=church.get('latitude'),
                longitude=church.get('longitude'),
                city=church.get('city'),
                state=church.get('state')
            )
            
            return event
            
        except Exception as e:
            logger.debug(f"Error parsing event container: {e}")
            return None
    
    def _extract_date_time(self, container) -> tuple:
        """Extract date and time from container"""
        # Look for date/time elements
        date_elem = container.find(['time', 'span', 'div'], class_=lambda x: x and any(
            word in str(x).lower() for word in ['date', 'time', 'when']
        ))
        
        if date_elem:
            datetime_str = date_elem.get('datetime') or date_elem.get_text()
            return self._parse_datetime_string(datetime_str)
        
        # Fallback: look in text
        text = container.get_text()
        return self._parse_datetime_from_text(text)
    
    def _parse_datetime_string(self, datetime_str: str) -> tuple:
        """Parse date and time from string"""
        import re
        from datetime import datetime
        
        try:
            # Try ISO format first
            dt = datetime.fromisoformat(datetime_str.strip())
            return dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M')
        except:
            pass
        
        # Try common formats
        formats = [
            '%B %d, %Y %I:%M %p',  # December 1, 2024 2:00 PM
            '%m/%d/%Y %I:%M %p',   # 12/01/2024 2:00 PM
            '%Y-%m-%d %H:%M',      # 2024-12-01 14:00
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(datetime_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M')
            except:
                continue
        
        return None, None
    
    def _parse_datetime_from_text(self, text: str) -> tuple:
        """Extract date/time from free text using regex"""
        import re
        from datetime import datetime
        
        # Look for common date patterns
        date_patterns = [
            # December 1, 2024 or Dec 1, 2024
            (r'(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{1,2}),?\s+(\d{4})', '%B %d %Y'),
            # 12/01/2024 or 12-01-2024
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', '%m/%d/%Y'),
            # 2024-12-01
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
        ]
        
        # Look for common time patterns
        time_patterns = [
            # 2:00 PM, 2:00pm, 14:00
            r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?',
            # 2pm, 2 pm
            r'(\d{1,2})\s*(AM|PM|am|pm)',
        ]
        
        date_str = None
        time_str = None
        
        # Try to find date
        for pattern, fmt_template in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_text = match.group(0)
                    # Try to parse it
                    for fmt in [fmt_template, fmt_template.replace('%B', '%b')]:
                        try:
                            dt = datetime.strptime(date_text, fmt)
                            date_str = dt.strftime('%Y-%m-%d')
                            break
                        except:
                            continue
                    if date_str:
                        break
                except:
                    continue
        
        # Try to find time
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2).isdigit() else 0
                    meridiem = match.group(3) if len(match.groups()) > 2 else None
                    
                    # Convert to 24-hour format
                    if meridiem and meridiem.upper() == 'PM' and hour != 12:
                        hour += 12
                    elif meridiem and meridiem.upper() == 'AM' and hour == 12:
                        hour = 0
                    
                    time_str = f"{hour:02d}:{minute:02d}"
                    break
                except:
                    continue
        
        return date_str, time_str
    
    def _extract_description(self, container) -> str:
        """Extract event description"""
        desc_elem = container.find(['p', 'div'], class_=lambda x: x and any(
            word in str(x).lower() for word in ['description', 'content', 'excerpt', 'summary']
        ))
        
        if desc_elem:
            return desc_elem.get_text().strip()
        
        # Fallback: get all text
        return container.get_text().strip()[:500]  # Limit length
    
    def _extract_location(self, container, church: Dict) -> str:
        """Extract event location"""
        loc_elem = container.find(['address', 'span', 'div'], class_=lambda x: x and any(
            word in str(x).lower() for word in ['location', 'venue', 'address', 'where']
        ))
        
        if loc_elem:
            return loc_elem.get_text().strip()
        
        # Default to church address
        if church.get('address'):
            return church['address']
        
        return f"{church.get('city', '')}, {church.get('state', '')}".strip(', ')
    
    def _determine_event_type(self, title: str, description: str) -> str:
        """Determine event type from title and description"""
        text = f"{title} {description}".lower()
        
        # Mission trips
        if any(word in text for word in ['mission', 'trip', 'pilgrimage']):
            return 'mission_trips_domestic' if 'domestic' in text or any(state in text for state in ['kentucky', 'appalachia', 'mississippi']) else 'mission_trips_international'
        
        # Service events
        if any(word in text for word in ['food', 'pantry', 'hunger', 'feeding']):
            return 'food_pantry'
        if any(word in text for word in ['homeless', 'shelter', 'street']):
            return 'homeless_outreach'
        if any(word in text for word in ['hospital', 'visit', 'sick', 'patient']):
            return 'hospital_visits'
        if any(word in text for word in ['nursing', 'elderly', 'senior']):
            return 'nursing_home'
        if any(word in text for word in ['volunteer', 'service']):
            return 'community_service'
        
        # Social events
        if any(word in text for word in ['festival', 'feast', 'celebration']):
            return 'festival'
        if any(word in text for word in ['retreat', 'convention']):
            return 'retreat'
        if any(word in text for word in ['sports', 'game', 'tournament']):
            return 'sports_event'
        if any(word in text for word in ['cultural', 'heritage', 'tradition']):
            return 'cultural_event'
        if any(word in text for word in ['family', 'picnic', 'gathering']):
            return 'family_event'
        if any(word in text for word in ['social', 'party', 'dinner']):
            return 'social_gathering'
        if any(word in text for word in ['conference', 'seminar', 'workshop']):
            return 'conference'
        
        return 'social_gathering'  # Default
    
    def _is_mission_trip(self, title: str, description: str) -> bool:
        """Check if event is a mission trip"""
        text = f"{title} {description}".lower()
        return any(word in text for word in ['mission', 'trip', 'pilgrimage'])
    
    def _extract_contact_info(self, container) -> Dict[str, str]:
        """Extract contact information"""
        import re
        
        text = container.get_text()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        
        # Extract phone
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        
        return {
            'person': None,  # TODO: Extract contact person name
            'email': email_match.group(0) if email_match else None,
            'phone': phone_match.group(0) if phone_match else None
        }
    
    def _extract_registration_link(self, container, source_url: str) -> str:
        """Extract registration/RSVP link"""
        links = container.find_all('a', href=True)
        
        for link in links:
            text = link.get_text().lower()
            href = link['href']
            
            if any(word in text for word in ['register', 'rsvp', 'sign up', 'signup']):
                if href.startswith('http'):
                    return href
                elif href.startswith('/'):
                    base_url = '/'.join(source_url.split('/')[:3])
                    return f"{base_url}{href}"
        
        return None


class MultiThreadedScraper:
    """Coordinates multi-threaded scraping of multiple churches"""
    
    def __init__(self, session, max_workers: int = 10):
        self.session = session
        self.max_workers = max_workers
        self.church_scraper = ChurchEventScraper(session)
    
    def scrape_all_churches(self, churches: List[Dict]) -> List[ServiceEvent]:
        """Scrape events from all churches in parallel"""
        all_events = []
        
        logger.info(f"Starting multi-threaded scraping of {len(churches)} churches with {self.max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all church scraping tasks
            future_to_church = {
                executor.submit(self.church_scraper.scrape_church_events, church): church 
                for church in churches
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_church):
                church = future_to_church[future]
                try:
                    events = future.result()
                    if events:
                        all_events.extend(events)
                        logger.info(f"✓ {church['name']}: {len(events)} events")
                    else:
                        logger.debug(f"✗ {church['name']}: no events found")
                except Exception as e:
                    logger.error(f"✗ {church['name']}: {str(e)}")
        
        logger.info(f"Multi-threaded scraping complete: {len(all_events)} total events from {len(churches)} churches")
        
        return all_events
