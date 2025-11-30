# Configuration Guide

This guide explains all configuration options in `config.json`.

## 🎯 Your Use Case: Mission Trips (Nationwide) + Local Service/Social

Perfect setup for:
- **Mission trips**: From anywhere in the US (need advance planning time)
- **Service events**: Only nearby (local one-day commitments)
- **Social events**: Only nearby (local gatherings)

---

## 📍 Location Settings

```json
"location": {
  "zip_code": "07066",                    // Your ZIP code
  "use_current_location": false,          // Use GPS instead of ZIP
  "radius_miles": 10,                     // Default radius for LOCAL events
  "include_diocese_events": true,         // Include diocese-wide events
  "nationwide_for_mission_trips": true    // Search all US for mission trips
}
```

**What this means:**
- Service/social events: Only within 10 miles of Clark, NJ
- Mission trips: From churches anywhere in the USA!

---

## 🎭 Event Preferences - Smart Distance Rules

```json
"event_preferences": {
  "distance_rules": {
    "mission_trips": "nationwide",        // ✈️ Find mission trips from anywhere
    "service_events": "local_only",       // 🏠 Service only from nearby churches
    "social_events": "local_only"         // 🎉 Social only from nearby churches
  }
}
```

**Options:**
- `"nationwide"` - Search entire country
- `"local_only"` - Only within your radius_miles
- `"region"` - Within your state + neighboring states

---

## ✈️ Mission Trip Settings

```json
"mission_trip_settings": {
  "min_advance_notice_days": 30,    // Only show trips at least 30 days away
  "include_domestic": true,         // Include US mission trips
  "include_international": true,    // Include international trips
  "max_duration_days": null,        // Any length (set to 14 for 2 weeks max)
  "destinations": []                // Empty = all destinations
                                    // Or: ["Mexico", "Egypt", "Kenya"]
}
```

**Examples:**
```json
// Only international trips, at least 60 days notice
{
  "min_advance_notice_days": 60,
  "include_domestic": false,
  "include_international": true
}

// Only short domestic trips (1 week or less)
{
  "min_advance_notice_days": 30,
  "include_domestic": true,
  "include_international": false,
  "max_duration_days": 7
}

// Only trips to specific countries
{
  "destinations": ["Egypt", "Ethiopia", "Kenya"]
}
```

---

## 🏠 Local Event Settings

```json
"local_event_settings": {
  "max_radius_miles": 10,           // Override default radius for local events
  "same_day_events": false,         // Exclude events happening today
  "min_advance_notice_days": 0      // Show events starting tomorrow
}
```

**Examples:**
```json
// Only events with at least 3 days notice
{
  "max_radius_miles": 10,
  "same_day_events": false,
  "min_advance_notice_days": 3
}

// Willing to travel farther for local events
{
  "max_radius_miles": 25,
  "same_day_events": true,
  "min_advance_notice_days": 0
}
```

---

## 🎯 Event Types

Control which types of events you want:

```json
"event_types": [
  // Service Events (local only)
  "food_pantry",              // Food pantry service
  "homeless_outreach",        // Homeless ministry
  "hospital_visits",          // Hospital visitations
  "nursing_home",             // Nursing home visits
  "youth_service",            // Youth service projects
  "community_service",        // General community service
  "charity_events",           // Charity fundraisers

  // Mission Trips (nationwide)
  "mission_trips_domestic",   // US mission trips
  "mission_trips_international", // International trips

  // Social Events (local only)
  "festival",                 // Church festivals
  "social_gathering",         // Social gatherings
  "retreat",                  // Retreats
  "conference",               // Conferences
  "sports_event",             // Sports events
  "cultural_event",           // Cultural events
  "family_event"              // Family events
]
```

**Remove any you don't want!**

---

## 📅 Google Calendar

```json
"google_calendar": {
  "enabled": true,                  // Auto-add to calendar
  "calendar_name": "Coptic Service Events",
  "auto_add_events": true,
  "reminder_minutes": [1440, 60]    // Reminders: 1 day before, 1 hour before
}
```

**Reminder options:**
- `[10080]` = 1 week before
- `[4320, 1440, 60]` = 3 days, 1 day, 1 hour before
- `[43200]` = 30 days before (good for mission trips!)

---

## 🔔 Notifications

```json
"notifications": {
  "enabled": true,
  "email": "your-email@example.com",  // Your email address
  "frequency": "weekly",               // daily, weekly, or monthly
  "new_event_alerts": true,            // Email when new events found
  "deadline_alerts": true,             // Email before registration deadlines
  "days_before_deadline": 3            // Alert 3 days before deadline
}
```

---

## 🌐 Data Sources

Control where to search for events:

```json
"data_sources": {
  "diocese_directory": {
    "enabled": false,               // Use global directory instead
    "auto_detect": true,
    "manual_dioceses": []
  },
  "diocese_websites": {
    "southern_usa": "https://suscopts.org"  // Diocese websites to check
  },
  "church_websites": [              // Specific church websites
    "https://stmarknj.org",
    "https://stmarkjerseycity.org"
  ],
  "facebook_pages": [],             // Church Facebook pages
  "instagram_accounts": []          // Church Instagram accounts
}
```

**Note:** With `nationwide_for_mission_trips: true`, the bot will search ALL US dioceses for mission trips automatically!

---

## ⚡ Scraping Strategy

```json
"scraping_strategy": {
  "start_with_diocese": true,       // Use global church directory
  "discover_churches": true,        // Auto-discover churches
  "multi_threaded": true,           // Scrape multiple churches at once
  "max_workers": 10,                // Number of concurrent scrapers
  "timeout_seconds": 30             // Timeout per website
}
```

---

## 📝 Example Configurations

### Example 1: Your Current Setup (Recommended!)

```json
{
  "location": {
    "zip_code": "07066",
    "radius_miles": 10,
    "nationwide_for_mission_trips": true
  },
  "event_preferences": {
    "distance_rules": {
      "mission_trips": "nationwide",
      "service_events": "local_only",
      "social_events": "local_only"
    },
    "mission_trip_settings": {
      "min_advance_notice_days": 30,
      "include_domestic": true,
      "include_international": true
    },
    "local_event_settings": {
      "max_radius_miles": 10,
      "min_advance_notice_days": 0
    }
  }
}
```

**Result:**
- ✈️ Mission trips from ALL US churches (30+ days notice)
- 🏠 Service events from churches within 10 miles
- 🎉 Social events from churches within 10 miles

### Example 2: Only International Mission Trips + Nearby Service

```json
{
  "event_preferences": {
    "include_social_events": false,
    "mission_trip_settings": {
      "min_advance_notice_days": 60,
      "include_domestic": false,
      "include_international": true,
      "destinations": ["Egypt", "Ethiopia", "Kenya"]
    },
    "local_event_settings": {
      "max_radius_miles": 5
    }
  }
}
```

### Example 3: Everything Nearby (No Nationwide Search)

```json
{
  "location": {
    "radius_miles": 25,
    "nationwide_for_mission_trips": false
  },
  "event_preferences": {
    "distance_rules": {
      "mission_trips": "local_only",
      "service_events": "local_only",
      "social_events": "local_only"
    }
  }
}
```

---

## 🚀 Quick Start

1. **Edit your preferences:**
   ```bash
   nano config.json
   ```

2. **Test your settings:**
   ```bash
   python main.py --once
   ```

3. **Check the results:**
   - Mission trips from nationwide: ✈️
   - Service events nearby: 🏠
   - Social events nearby: 🎉

4. **Schedule daily runs:**
   ```bash
   python main.py --schedule
   ```

---

## 💡 Pro Tips

1. **For mission trip planning:**
   - Set `min_advance_notice_days: 60` (2 months)
   - Enable `deadline_alerts: true`
   - Set reminders: `[43200, 10080, 1440]` (30d, 7d, 1d)

2. **For weekend service:**
   - Set `max_radius_miles: 15` (willing to drive)
   - Set `min_advance_notice_days: 3` (plan ahead)
   - Enable weekend-only filtering (coming soon)

3. **For social events:**
   - Keep `max_radius_miles: 10` (local only)
   - Enable `same_day_events: true` (spontaneous)
   - Focus on: `["festival", "retreat", "conference"]`

---

## ❓ Need Help?

See `README.md` for full documentation or `QUICK_REFERENCE.md` for commands.
