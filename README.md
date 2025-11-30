# Coptic Orthodox Church Service Events Bot

A bot that automatically discovers and aggregates **service/volunteer events, mission trips, and social events** from Coptic Orthodox churches in your area, with Google Calendar integration.

## 🎯 What Makes This Different

**Diocese-First Discovery**: Instead of manually adding church websites, the bot:
1. 🔍 **Detects your diocese** based on your location
2. 📋 **Scrapes the diocese directory** to find all churches
3. 📍 **Filters by distance** (only churches within your radius)
4. ⚡ **Multi-threaded scraping** of all nearby churches simultaneously
5. 📅 **Auto-adds to Google Calendar** with all event details

**Comprehensive Event Coverage**: Service events, mission trips, festivals, retreats, conferences, social gatherings, and more!

## Features

### Core Features (v1)
- 🏛️ **Diocese-First Discovery**: Automatically detects your diocese and discovers all churches
- ⚡ **Multi-threaded Scraping**: Fast parallel processing of multiple church websites
- 📍 **Location-based**: Configure by ZIP code or use current location
- 📅 **Google Calendar Integration**: Automatically creates calendar invites
- ⛪ **Comprehensive Events**:
  - **Service**: Food pantry, homeless outreach, hospital visits, nursing homes
  - **Mission Trips**: Domestic and international with full details
  - **Social**: Festivals, retreats, conferences, sports, cultural events
- 🎯 **Smart Filtering**: By distance, event type, and preferences
- 🔄 **Auto-sync**: Scheduled daily/weekly discovery
- 💾 **Smart Caching**: Prevents duplicate events

### Suggested Additional Features
- 🔔 **Smart Notifications**: Configurable alerts (weekly digest, new events, deadlines)
- 🔄 **Auto-sync**: Periodic checking for new events (daily/weekly)
- 🏷️ **Event Categorization**: Filter by type (food pantry, homeless outreach, hospital visits, mission trips, youth service, etc.)
- 👥 **Capacity Tracking**: Shows available spots if listed
- 🎯 **Preferences**: Save interests (age groups, service types) for personalized recommendations
- 📊 **Service Log**: Track your participation history and hours
- 🔗 **Registration Links**: Direct links to sign up through church websites
- 📧 **Email Digest**: Optional email summaries
- 🗺️ **Map View**: Visual map of events in your area
- ⏰ **Deadline Alerts**: Notifications for registration deadlines
- 🌐 **Diocese Coverage**: Option to include events from entire diocese
- 📱 **Share Events**: Easy sharing with friends/family
- 💬 **Contact Info**: Church coordinator contact details

## Tech Stack

- **Language**: Python 3.9+
- **Web Scraping**: BeautifulSoup4, Selenium (for dynamic content)
- **Calendar**: Google Calendar API
- **Location**: Geopy, uszipcode, Google Geocoding API
- **Storage**: SQLite (event cache), JSON (config)
- **Scheduling**: APScheduler (for periodic runs)
- **Concurrency**: ThreadPoolExecutor (multi-threaded scraping)

## How It Works

```
Your Location → Detect Diocese → Scrape Directory → Find Churches Within Radius
                                                              ↓
                                                    Multi-threaded Scraping
                                                              ↓
                                            Aggregate Events → Filter → Google Calendar
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture.

## Setup

1. Install dependencies:
   ```bash
   # Create virtual environment (recommended)
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install packages
   pip install -r requirements.txt
   ```

   Or use the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. Configure your settings in `config.json`:
   ```json
   {
     "location": {
       "zip_code": "30309",           // Your ZIP code
       "use_current_location": false,
       "radius_miles": 50              // Search radius
     },
     "event_preferences": {
       "include_service_events": true,
       "include_mission_trips": true,
       "include_social_events": true   // Festivals, retreats, etc.
     },
     "scraping_strategy": {
       "start_with_diocese": true,     // Diocese-first approach
       "discover_churches": true,      // Auto-discover from directory
       "multi_threaded": true,         // Parallel scraping
       "max_workers": 10               // Number of threads
     }
   }
   ```

3. Set up Google Calendar API credentials (see docs/google_calendar_setup.md)

4. Run the bot:
   ```bash
   python main.py
   ```

## Configuration

See `config.json` for all available options.

## Data Sources

The bot automatically discovers events from:

### Diocese-First Approach (Default)
1. **Diocese Directory**: Scrapes your local diocese website for church listings
2. **All Churches**: Automatically discovers and scrapes all churches in the directory
3. **Distance Filtered**: Only includes churches within your configured radius

### Supported Dioceses
- Southern USA Diocese (`suscopts.org`)
- Diocese of Los Angeles (`lacopts.org`)
- Diocese of New York & New Jersey (`stmarknj.org`)
- *More can be easily added*

### Fallback Sources
- Individual church websites (manually configured)
- Social media pages (future: Facebook, Instagram)
- Church management platforms (future)

## Future Enhancements

- Mobile app integration
- Multi-language support (Arabic, Coptic)
- Integration with church management systems
- Community features (carpooling, meal coordination)
- Volunteer hour certification
