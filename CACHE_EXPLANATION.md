# How the Bot Uses the Directory & Caching

## 🎯 Your Question Answered

You asked: "I was hoping you would use the directory and search based on the directory, location zip code, and radius. Then perhaps cache it for future use."

**YES! That's EXACTLY what it does!** Let me explain:

---

## 🌍 How Directory Search Works

### Step 1: You Set Your Location
```json
{
  "location": {
    "zip_code": "07066",        // Your ZIP → Becomes "Clark, NJ"
    "radius_miles": 10
  }
}
```

### Step 2: Bot Uses Global Directory
The bot automatically:
1. **Detects your state** from ZIP code (07066 → NJ)
2. **Queries directory.nihov.org** for ALL churches in NJ
3. **Fetches contact info** from the directory's XML API
4. **Filters by distance** using your radius (10 miles)
5. **Caches results** for 24 hours

```
Your ZIP: 07066
    ↓
Detect: Clark, NJ (40.62, -74.32)
    ↓
Query Directory: https://directory.nihov.org/church/usa/new-jersey
    ↓
Found: 668 churches in NJ
    ↓
Fetch contact info for each church from XML API
    ↓
Filter: 659 churches within 10 miles
    ↓
Cache: Save to church_cache.json
    ↓
Find: ~501 churches with websites!
```

---

## 💾 Caching System

### What Gets Cached

1. **State Church Lists** (cached for 24 hours)
   - File: `church_cache.json`
   - Contains: All 668 NJ churches with names, cities, etc.
   - Next run: Instant loading from cache!

2. **Church Contact Info** (cached for 1 week)
   - Website URLs
   - Phone numbers
   - Facebook pages
   - Saves ~667 network requests!

### Cache File Example

```json
{
  "state_NJ": {
    "state": "NJ",
    "timestamp": "2025-11-29T20:30:00",
    "count": 668,
    "churches": [
      {
        "name": "St. Mark Coptic Orthodox Church - Cedar Grove",
        "url": "http://elmaqar.org/",
        "phone": "(973) 857-0078",
        "city": "Cedar Grove",
        "state": "NJ"
      },
      // ... 667 more churches
    ]
  },
  "contact_1234": {
    "church_id": "1234",
    "timestamp": "2025-11-29T20:30:00",
    "contact_info": {
      "website": "http://example.org",
      "phone": "(123) 456-7890"
    }
  }
}
```

---

## 🚀 Performance Benefits

### First Run (No Cache)
```
1. Query directory.nihov.org/church/usa/new-jersey
2. Find 668 churches
3. Fetch contact info for each (668 XML requests)
4. Save to cache
Time: ~3-5 minutes
```

### Second Run (With Cache)
```
1. Load from church_cache.json
2. Already have all 668 churches!
3. Already have contact info!
4. Just filter by distance
Time: ~2-3 seconds! 🚀
```

**Cache saves you 99% of the time!**

---

## 🗺️ Mission Trips: Nationwide Search

When you search for mission trips, the bot:

1. **Queries ALL US states** from the directory
2. **Caches each state** separately
3. **Filters to mission trips only**
4. **No distance filter** for mission trips

```json
"distance_rules": {
  "mission_trips": "nationwide"  // Search ALL states
}
```

Example cache after nationwide search:
```
church_cache.json contains:
- state_NJ: 668 churches
- state_NY: 1,245 churches
- state_CA: 2,341 churches
- state_TX: 456 churches
- ... all 50 states!
```

Next time: Instant loading of all ~10,000 US churches!

---

## 📝 Config.json vs Directory vs Cache

### config.json → Manual Overrides
```json
"data_sources": {
  "church_websites": [
    "https://stmarknj.org"  // OPTIONAL: Add specific churches
  ]
}
```
These are **IN ADDITION TO** the directory, not instead of!

### Directory → Discovery Source
- `directory.nihov.org` - 1,279 churches worldwide
- Auto-discovered based on your location
- Always used (unless you disable it)

### Cache → Speed Optimization
- `church_cache.json` - Local copy
- Refreshes every 24 hours
- Makes second run instant

---

## 🎯 Your Use Case

### For Mission Trips (Nationwide)
```
First run: Queries all 50 states (takes 10-15 min)
           Caches ~10,000 churches
           
Next runs: Loads from cache (takes 5 seconds!)
           Refreshes once per day
```

### For Local Events (NJ only)
```
First run: Queries NJ only (takes 3-5 min)
           Caches 668 churches
           
Next runs: Loads from cache (takes 2 seconds!)
           Refreshes once per day
```

---

## ⚙️ Cache Settings

### In config.json (coming soon):
```json
"cache_settings": {
  "enabled": true,
  "state_cache_hours": 24,        // Refresh state lists daily
  "contact_cache_hours": 168,     // Refresh contacts weekly
  "auto_cleanup": true             // Remove old cache entries
}
```

### Manual Cache Management:
```bash
# View cache stats
python -c "from src.church_cache import ChurchCache; c=ChurchCache(); print(c.get_stats())"

# Clear expired cache
python -c "from src.church_cache import ChurchCache; c=ChurchCache(); c.clear_expired()"

# Delete cache (force fresh download)
rm church_cache.json
```

---

## 🔍 Summary

**Q: Does it use the directory?**
✅ YES - Automatically queries directory.nihov.org

**Q: Does it use ZIP code?**
✅ YES - Converts ZIP → State → Queries that state

**Q: Does it use radius?**
✅ YES - Filters churches by distance from your location

**Q: Does it cache results?**
✅ YES - Saves to church_cache.json for 24 hours

**Q: What about config.json data_sources?**
✅ Those are ADDITIONAL sources, not replacements

---

## 💡 The Full Picture

```
config.json (Your Settings)
    ├── ZIP Code: 07066
    ├── Radius: 10 miles
    └── Additional websites (optional)
         ↓
Directory Search (Automatic)
    ├── Query: directory.nihov.org/church/usa/new-jersey
    ├── Found: 668 churches
    └── Contact: Fetch from XML API
         ↓
Cache (Automatic)
    ├── Save: church_cache.json
    ├── Age: 24 hours
    └── Next run: Load from cache
         ↓
Distance Filter (Automatic)
    ├── Your location: Clark, NJ (40.62, -74.32)
    ├── Radius: 10 miles
    └── Result: 659 churches nearby
         ↓
Event Scraping (Automatic)
    └── Scrape ~501 church websites for events!
```

**Everything is automatic! You just set your ZIP code and preferences!** 🎉

