# Project Summary: Coptic Orthodox Service Events Bot

## 🎯 What This Bot Does

This bot automatically discovers, aggregates, and organizes service/volunteer events and mission trips from Coptic Orthodox churches in your area. It creates Google Calendar invites with all event details so you never miss an opportunity to serve.

## ✨ Core Features Implemented (v1)

### Essential Features
- ✅ **Diocese-First Discovery**: Automatically detects your diocese and discovers all churches in the directory
- ✅ **Multi-threaded Scraping**: Fast parallel scraping of multiple church websites simultaneously
- ✅ **Location-based Discovery**: Configure by ZIP code or use current location
- ✅ **Event Aggregation**: Scrapes from diocese directories → church websites
- ✅ **Comprehensive Event Types**:
  - **Service Events**: Food pantry, homeless outreach, hospital visits, nursing homes, youth service
  - **Mission Trips**: Domestic and international with trip details
  - **Social Events**: Festivals, retreats, conferences, sports, cultural events, family gatherings
- ✅ **Google Calendar Integration**: Auto-creates calendar invites with reminders
- ✅ **Comprehensive Event Data**:
  - Event name, description
  - Church name and location
  - Date, time, duration
  - Contact information
  - Registration links and deadlines
  - Capacity tracking
  - Requirements and materials needed
- ✅ **Smart Filtering**: Filter by distance, event type, and preferences
- ✅ **Automated Scheduling**: Daily/weekly automatic discovery runs
- ✅ **Event Database**: SQLite storage to prevent duplicates

### How It Works

1. **🔍 Detect Diocese**: Based on your location (ZIP or GPS), the bot identifies your Coptic diocese
2. **📋 Discover Churches**: Scrapes the diocese directory to get a complete list of churches
3. **📍 Filter by Distance**: Only includes churches within your configured radius (e.g., 50 miles)
4. **⚡ Multi-threaded Scraping**: Simultaneously scrapes all nearby church websites for events
5. **📅 Calendar Integration**: Automatically adds discovered events to your Google Calendar
6. **🔄 Scheduled Updates**: Runs daily/weekly to find new events

## 💡 Additional Features Suggested

### High Priority
1. **Smart Notifications** 🔔
   - Weekly digest emails
   - New event alerts
   - Registration deadline reminders
   - Configurable notification preferences

2. **Event Categorization & Filtering** 🏷️
   - Filter by service type
   - Age group filtering
   - Save user preferences
   - Diocese-wide vs. local events

3. **Capacity & Registration Tracking** 👥
   - Real-time spot availability
   - Waitlist notifications
   - "Almost full" alerts

### Medium Priority
4. **Service History & Tracking** 📊
   - Personal participation log
   - Volunteer hours tracking
   - Service certificates/reports
   - Year-end summary

5. **Enhanced Discovery** 🔍
   - Social media integration (Facebook Events API, Instagram)
   - Multiple diocese support
   - Church management system integrations
   - Community bulletin boards

6. **Map & Visualization** 🗺️
   - Interactive map view
   - Route planning for multiple events
   - Nearby churches discovery

### Future Enhancements
7. **Community Features** 👨‍👩‍👧‍👦
   - Carpooling coordination
   - Meal/supply coordination
   - Team formation
   - Friend/family sharing

8. **Mobile App** 📱
   - iOS/Android apps
   - Push notifications
   - Offline access
   - Quick registration

9. **Multi-language Support** 🌐
   - Arabic interface
   - Coptic transliterations
   - Multi-lingual event descriptions

10. **Advanced Features** 🚀
    - AI-powered event recommendations
    - Calendar conflict detection
    - Weather-based alerts
    - Photo/video sharing from events
    - Volunteer recognition/gamification

## 📁 Project Structure

```
coptic-service-events/
├── main.py                    # Main entry point
├── quickstart.py              # Demo with mock data
├── config.json                # User configuration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
│
├── src/                      # Core source code
│   ├── __init__.py
│   ├── event_model.py        # Event data model
│   ├── config_manager.py     # Configuration handler
│   ├── location_service.py   # Location & geocoding
│   ├── diocese_scraper.py    # Diocese discovery & church lists
│   ├── church_scraper.py     # Multi-threaded church scraping
│   ├── event_scraper.py      # Main scraping orchestrator
│   ├── calendar_integration.py # Google Calendar API
│   ├── event_database.py     # SQLite database
│   └── scheduler.py          # Task scheduler
│
├── docs/                     # Documentation
│   ├── google_calendar_setup.md
│   └── custom_scrapers.md
│
└── examples/                 # Examples & demos
    ├── __init__.py
    └── mock_events.py        # Sample event data
```

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the demo** (uses mock data):
   ```bash
   python3 quickstart.py
   ```

3. **Configure your location** in `config.json`:
   ```json
   {
     "location": {
       "zip_code": "90001",
       "use_current_location": false,
       "radius_miles": 50
     }
   }
   ```

4. **Set up Google Calendar** (see `docs/google_calendar_setup.md`):
   - Create Google Cloud project
   - Enable Calendar API
   - Download credentials.json
   - Place in project root

5. **Add data sources** in `config.json`:
   ```json
   {
     "data_sources": {
       "diocese_websites": ["https://suscopts.org", "https://lacopts.org"],
       "church_websites": ["https://your-church.org"]
     }
   }
   ```

6. **Run the bot**:
   ```bash
   python main.py --once              # Run once
   python main.py --schedule          # Run on schedule
   ```

## 🛠️ Customization

### Add Custom Website Scrapers
See `docs/custom_scrapers.md` for detailed instructions on creating scrapers for specific church websites.

### Event Types
Configure which event types to include:

**Service Events:**
- `food_pantry`
- `homeless_outreach`
- `hospital_visits`
- `nursing_home`
- `youth_service`
- `community_service`
- `charity_events`

**Mission Trips:**
- `mission_trips_domestic`
- `mission_trips_international`

**Social Events:**
- `festival` (e.g., Church feasts, celebrations)
- `social_gathering` (e.g., Dinners, parties)
- `retreat` (e.g., Youth retreats, spiritual retreats)
- `conference` (e.g., Theological conferences, seminars)
- `sports_event` (e.g., Basketball tournaments)
- `cultural_event` (e.g., Heritage events, language classes)
- `family_event` (e.g., Picnics, family days)

## 🔐 Security

- Never commit `credentials.json`, `token.json`, or `.env` files
- Store sensitive data in `.env` file
- Use app-specific passwords for email notifications

## 📝 Next Steps for Production

1. **Implement Website Scrapers**: Create specific scrapers for popular Coptic church websites
2. **Add Notifications**: Implement email/SMS notifications
3. **Testing**: Add unit tests for scrapers and core functionality
4. **Error Handling**: Improve robustness for network failures
5. **Monitoring**: Add logging and error tracking
6. **User Interface**: Build a web dashboard or CLI interface
7. **Multi-user Support**: Support multiple users with different preferences

## 🤝 Contributing

To add support for a new church website:
1. Create a custom scraper in `src/scrapers/`
2. Follow the pattern in `docs/custom_scrapers.md`
3. Test with real data
4. Submit with documentation

## 📄 License

This is a personal project for the Coptic Orthodox community. Use freely for non-commercial purposes.

---

**Built with ❤️ to serve the Coptic Orthodox community**
