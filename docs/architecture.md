# Architecture: Diocese-First Event Discovery

## Overview

The bot uses a **diocese-first, multi-threaded** approach to efficiently discover events from all Coptic Orthodox churches in your area.

## Discovery Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER LOCATION                                                │
│    - ZIP code or GPS coordinates                                │
│    - Configured radius (e.g., 50 miles)                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. DIOCESE DETECTION                                            │
│    - Match location to Coptic diocese                           │
│    - Support for: Southern USA, LA, NY/NJ, and more            │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. CHURCH DIRECTORY SCRAPING                                    │
│    - Scrape diocese website for church directory                │
│    - Extract: church name, location, URL                        │
│    - Example: suscopts.org/churches                             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. DISTANCE FILTERING                                           │
│    - Geocode church addresses                                   │
│    - Calculate distance from user                               │
│    - Filter to churches within radius                           │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. MULTI-THREADED EVENT SCRAPING                                │
│    - Parallel scraping of all nearby churches                   │
│    - Try common event page URLs:                                │
│      • /events                                                  │
│      • /calendar                                                │
│      • /upcoming-events                                         │
│    - Parse event details from each page                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. EVENT AGGREGATION & FILTERING                                │
│    - Combine events from all churches                           │
│    - Remove duplicates                                          │
│    - Filter by event type preferences                           │
│    - Filter by distance                                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. GOOGLE CALENDAR INTEGRATION                                  │
│    - Create calendar invites                                    │
│    - Add all event details                                      │
│    - Set reminders                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. DioceseScraper (`src/diocese_scraper.py`)

**Responsibilities:**
- Detect user's diocese based on location
- Scrape diocese directory pages
- Extract church information (name, URL, location)
- Geocode church addresses
- Filter churches by distance

**Supported Dioceses:**
- Southern USA Diocese (`suscopts.org`)
- Diocese of Los Angeles (`lacopts.org`)
- Diocese of New York & New Jersey (`stmarknj.org`)
- *Extensible for more dioceses*

**Key Methods:**
```python
detect_diocese_for_location(lat, lon, state) → diocese_key
discover_churches_from_diocese(diocese_key) → List[Church]
filter_churches_by_distance(churches, lat, lon, radius) → List[Church]
```

### 2. ChurchEventScraper (`src/church_scraper.py`)

**Responsibilities:**
- Scrape individual church websites for events
- Try common event page URL patterns
- Parse event details from HTML
- Extract: title, date, time, location, description, contact, registration

**Event Page Detection:**
- Tries multiple common URLs:
  - `/events`
  - `/calendar`
  - `/events-calendar`
  - `/upcoming-events`
  - Homepage

**HTML Parsing:**
- Supports common patterns:
  - WordPress event plugins (Tribe Events)
  - Calendar widgets
  - Generic event listings
  - Custom church websites

**Key Methods:**
```python
scrape_church_events(church) → List[ServiceEvent]
_parse_events_from_page(soup, church) → List[ServiceEvent]
```

### 3. MultiThreadedScraper (`src/church_scraper.py`)

**Responsibilities:**
- Coordinate parallel scraping of multiple churches
- Use ThreadPoolExecutor for concurrency
- Collect and aggregate results

**Performance:**
- Default: 10 worker threads (configurable)
- Scrapes 10+ churches simultaneously
- Significant speed improvement vs. sequential

**Key Methods:**
```python
scrape_all_churches(churches) → List[ServiceEvent]
```

### 4. EventScraper (`src/event_scraper.py`)

**Responsibilities:**
- Main orchestrator
- Implements diocese-first strategy
- Coordinates all components
- Applies filters

**Discovery Strategy:**
```python
1. Get user location
2. Detect diocese
3. Discover churches from diocese
4. Filter churches by distance
5. Multi-threaded scrape all churches
6. Filter events by preferences
```

## Configuration

### Diocese Strategy (`config.json`)

```json
{
  "scraping_strategy": {
    "start_with_diocese": true,      // Use diocese-first approach
    "discover_churches": true,        // Auto-discover from directory
    "multi_threaded": true,           // Parallel scraping
    "max_workers": 10,                // Thread pool size
    "timeout_seconds": 30             // Per-request timeout
  }
}
```

### Diocese Directory (`config.json`)

```json
{
  "data_sources": {
    "diocese_directory": {
      "enabled": true,
      "auto_detect": true,            // Auto-detect from location
      "manual_dioceses": []           // Or specify manually
    },
    "diocese_websites": {
      "southern_usa": "https://suscopts.org",
      "los_angeles": "https://lacopts.org"
    }
  }
}
```

## Event Type Detection

The bot automatically categorizes events based on title and description:

### Service Events
- Food pantry: keywords like "food", "pantry", "feeding"
- Homeless outreach: "homeless", "shelter", "street"
- Hospital visits: "hospital", "visit", "patient", "sick"
- Nursing home: "nursing", "elderly", "senior"

### Mission Trips
- Detects: "mission", "trip", "pilgrimage"
- Determines domestic vs. international
- Extracts: destination, duration, cost

### Social Events
- Festival: "festival", "feast", "celebration"
- Retreat: "retreat", "convention"
- Conference: "conference", "seminar", "workshop"
- Sports: "sports", "game", "tournament"
- Cultural: "cultural", "heritage", "tradition"
- Family: "family", "picnic", "gathering"

## Performance Optimization

### Multi-threading Benefits
- **Sequential**: ~2-3 seconds per church = 2-3 minutes for 50 churches
- **Multi-threaded (10 workers)**: ~30-60 seconds for 50 churches

### Caching
- Church directory cached in database
- Geocoded addresses cached
- Events deduplicated

### Timeouts
- Per-request timeout: 30 seconds (configurable)
- Prevents hanging on slow websites
- Graceful failure handling

## Extensibility

### Adding New Dioceses

Edit `src/diocese_scraper.py`:

```python
DIOCESE_CONFIGS = {
    'your_diocese': {
        'url': 'https://diocese-website.org',
        'churches_page': '/churches',  # Path to directory
        'name': 'Your Diocese Name',
        'states': ['STATE1', 'STATE2']
    }
}
```

### Custom Church Scrapers

For churches with unique HTML structure, create custom parsers:

```python
class CustomChurchScraper:
    def scrape_events(self, church_url):
        # Custom parsing logic
        pass
```

## Error Handling

- **Diocese not found**: Falls back to direct church scraping
- **Church URL unreachable**: Logs error, continues with other churches
- **Parse failure**: Skips event, continues parsing
- **Network timeout**: Moves to next church

## Future Enhancements

1. **Intelligent Retry**: Retry failed churches with exponential backoff
2. **Cache Diocese Directories**: Cache for 24 hours to reduce requests
3. **Machine Learning**: Learn HTML patterns for better parsing
4. **Social Media Integration**: Scrape Facebook Events, Instagram
5. **User Feedback**: Allow users to report missing/incorrect events
