# Global Church Database - Setup Guide

## 🌍 Overview

The app now includes a **global Coptic Orthodox church database** powered by Google Places API. This is a one-time discovery that creates a local database of churches worldwide.

## 📊 Coverage

- **141 regions worldwide**:
  - 🇺🇸 All 50 US states
  - 🇨🇦 10 Canadian provinces
  - 🌍 15 Middle East countries (Egypt, Jordan, Lebanon, UAE, etc.)
  - 🇪🇺 26 European countries
  - 🌍 17 African countries
  - 🌏 12 Asian countries
  - 🌏 6 Oceania regions (Australia + New Zealand)
  - 🌎 10 South/Central American countries

- **Estimated churches**: ~2,000-2,500 worldwide
- **Data stored**: name, address, city, state, country, phone, website, coordinates, ratings

## 🚀 Quick Start

### 1. Run Global Discovery (ONE-TIME)

```bash
# This takes 90-120 minutes and costs ~$77 (FREE under Google's $200/month tier)
python -m src.global_church_discovery
```

This will:
- Search all 141 regions
- Validate church locations (ensures accuracy)
- Store data in `coptic_events.db`
- **After this, all queries are FREE and instant!**

### 2. Use the Database

```python
from src.church_directory_v2 import GooglePlacesChurchDirectory

# Find churches near you
directory = GooglePlacesChurchDirectory()
churches = directory.discover_churches_by_radius(
    user_lat=40.62,
    user_lon=-74.32,
    radius_miles=15
)

# Show stats
stats = directory.get_coverage_stats()
print(f"Total churches: {stats['total_churches']}")
print(f"With website: {stats['with_website']} ({stats['website_pct']}%)")
```

## 💰 Cost Breakdown

- **One-time discovery**: ~$77
  - Text searches: 564 × $0.017 = $9.59
  - Place details: 2,115 × $0.032 = $67.68
- **Google Free Tier**: $200/month (so this is FREE!)
- **Future queries**: $0 (all local SQL)

## 🔄 Refresh Frequency

Run global discovery every **6-12 months** to keep data current:

```bash
# Re-run to update database
python -m src.global_church_discovery
```

## 📁 Database Location

- **Local database**: `coptic_events.db` (excluded from git)
- **Backup**: You can download the populated database from releases

## 🛠️ Technical Details

### Location Validation

The discovery includes strict validation:
- US churches: Verified by state code
- International: Verified by country name
- Duplicate detection by `place_id`
- Skips churches with mismatched locations

### Schema

```sql
CREATE TABLE google_places_churches (
    place_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    latitude REAL,
    longitude REAL,
    phone TEXT,
    website TEXT,
    email TEXT,
    rating REAL,
    user_ratings_total INTEGER,
    vicinity TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    postal_code TEXT,
    types TEXT,
    business_status TEXT,
    discovered_at TIMESTAMP,
    last_updated TIMESTAMP
)
```

## 🎯 Benefits

1. **Accurate locations**: Google Places data is authoritative
2. **Rich metadata**: Ratings, phone, website, hours
3. **Fast queries**: Local SQL (no API calls)
4. **Global coverage**: Every Coptic church worldwide
5. **Cost-effective**: One-time $77 vs. $40+ per query

## 📝 Notes

- First run takes 90-120 minutes
- Progress bar shows real-time status
- Database size: ~50-100 MB when complete
- Includes location validation to ensure accuracy
