# Quick Reference Card

## 🚀 Getting Started

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Try demo with mock data
python quickstart.py

# 3. Edit your configuration
nano config.json

# 4. Run the bot
python main.py --once
```

## ⚙️ Configuration Quick Start

**config.json** - Minimum required settings:

```json
{
  "location": {
    "zip_code": "YOUR_ZIP",      // e.g., "30309" for Atlanta
    "radius_miles": 50
  }
}
```

## 📅 Event Types

### Service Events
- `food_pantry` - Food distribution
- `homeless_outreach` - Homeless ministry
- `hospital_visits` - Hospital ministry
- `nursing_home` - Elderly care
- `youth_service` - Youth activities
- `community_service` - General service

### Mission Trips
- `mission_trips_domestic` - USA missions
- `mission_trips_international` - International missions

### Social Events
- `festival` - Church feasts, celebrations
- `retreat` - Spiritual retreats
- `conference` - Seminars, workshops
- `sports_event` - Tournaments, games
- `cultural_event` - Heritage events
- `family_event` - Picnics, gatherings
- `social_gathering` - Dinners, parties

## 🎯 Common Commands

```bash
# Run once and exit
python main.py --once

# Run on schedule (daily/weekly)
python main.py --schedule

# Use different config file
python main.py --config my-config.json

# View logs
tail -f coptic_events.log
```

## 🏛️ Supported Dioceses

| Diocese | States | Website |
|---------|--------|---------|
| Southern USA | GA, FL, SC, NC, TN, KY, AL, LA, MS, AR | suscopts.org |
| Los Angeles | CA | lacopts.org |
| NY & NJ | NY, NJ, PA, CT | stmarknj.org |

## ⚡ Performance Settings

```json
{
  "scraping_strategy": {
    "multi_threaded": true,      // Enable parallel scraping
    "max_workers": 10,           // Number of threads (1-20)
    "timeout_seconds": 30        // Per-request timeout
  }
}
```

**Recommended:**
- Small diocese (< 20 churches): 5 workers
- Medium diocese (20-50 churches): 10 workers
- Large diocese (> 50 churches): 15 workers

## 📍 Location Options

### Option 1: ZIP Code
```json
{
  "location": {
    "zip_code": "30309",
    "use_current_location": false,
    "radius_miles": 50
  }
}
```

### Option 2: Current Location (GPS/IP)
```json
{
  "location": {
    "use_current_location": true,
    "radius_miles": 50
  }
}
```

## 📅 Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable "Google Calendar API"
4. Create OAuth credentials (Desktop app)
5. Download as `credentials.json`
6. Place in project root
7. Run bot - it will open browser for authorization

## 🔍 Filtering Events

```json
{
  "event_preferences": {
    "include_service_events": true,
    "include_mission_trips": true,
    "include_social_events": true,
    "event_types": [
      "food_pantry",
      "homeless_outreach",
      "festival",
      "retreat"
    ]
  }
}
```

## 🔔 Notifications (Coming Soon)

```json
{
  "notifications": {
    "enabled": true,
    "email": "your-email@example.com",
    "frequency": "weekly",
    "new_event_alerts": true
  }
}
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `config.json` | Your settings |
| `credentials.json` | Google Calendar API (create yourself) |
| `token.json` | Google Calendar auth (auto-generated) |
| `coptic_events.db` | Event cache database |
| `coptic_events.log` | Application logs |

## 🐛 Troubleshooting

**No events found?**
- Check your ZIP code is correct
- Increase `radius_miles`
- Verify diocese website is accessible
- Check logs: `tail -f coptic_events.log`

**Slow scraping?**
- Increase `max_workers` (up to 20)
- Decrease `timeout_seconds` for faster failures
- Some church websites may be slow

**Google Calendar not working?**
- Ensure `credentials.json` exists
- Delete `token.json` and re-authorize
- Check Calendar API is enabled in Google Cloud

## 📊 Database Queries

```bash
# View all events in database
sqlite3 coptic_events.db "SELECT title, church_name, date FROM events ORDER BY date;"

# Count events by type
sqlite3 coptic_events.db "SELECT event_type, COUNT(*) FROM events GROUP BY event_type;"

# Clear database (start fresh)
rm coptic_events.db
```

## 🔧 Advanced Configuration

### Custom Diocese
Edit `src/diocese_scraper.py` and add to `DIOCESE_CONFIGS`:

```python
'your_diocese': {
    'url': 'https://diocese-website.org',
    'churches_page': '/churches',
    'name': 'Your Diocese Name',
    'states': ['STATE1', 'STATE2']
}
```

### Schedule Configuration

```json
{
  "scraping": {
    "schedule": "daily",         // or "weekly"
    "run_time": "08:00"         // HH:MM format (24-hour)
  }
}
```

## 📞 Need Help?

- Read: `README.md`
- Architecture: `docs/architecture.md`
- Google Calendar: `docs/google_calendar_setup.md`
- Custom scrapers: `docs/custom_scrapers.md`
