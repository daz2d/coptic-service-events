# Google Places API Setup Guide

## 🎯 Why Google Places API?

Google Places provides **verified, high-quality church data**:
- ✅ Exact addresses and coordinates
- ✅ Phone numbers
- ✅ Website URLs
- ✅ Hours of operation
- ✅ Reviews and ratings
- ✅ Photos

Much better than scraping NIHOV directory!

## 💰 Pricing

- **FREE for our use case!**
- $200 free credit/month = ~6,000 searches
- NJ churches: ~60-100 searches = $0
- One-time population, not recurring cost

## 📝 Setup Steps (5 minutes)

### 1. Create Google Cloud Account

Go to: https://console.cloud.google.com/

- Sign in with your Google account
- Accept terms of service
- No credit card required for free tier

### 2. Create a New Project

1. Click "Select a project" dropdown (top left)
2. Click "New Project"
3. Name it: "Coptic Events Bot"
4. Click "Create"

### 3. Enable Places API

1. Go to: https://console.cloud.google.com/apis/library
2. Search for "Places API (New)"
3. Click on it
4. Click "Enable"

### 4. Create API Key

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "+ CREATE CREDENTIALS"
3. Select "API Key"
4. Copy the key (looks like: `AIzaSyD...`)
5. Click "Restrict Key" (recommended)
   - Under "API restrictions", select "Restrict key"
   - Choose "Places API"
   - Click "Save"

### 5. Set Environment Variable

**Linux/Mac:**
```bash
export GOOGLE_PLACES_API_KEY="AIzaSyD..."
```

**Add to your shell profile** (~/.bashrc or ~/.zshrc):
```bash
echo 'export GOOGLE_PLACES_API_KEY="AIzaSyD..."' >> ~/.bashrc
source ~/.bashrc
```

**Windows:**
```cmd
set GOOGLE_PLACES_API_KEY=AIzaSyD...
```

## 🚀 Run the Discovery Script

```bash
cd /home/minaa/coptic-service-events
source venv/bin/activate

# Discover churches in NJ
python -m src.google_places_discovery
```

This will:
1. Search Google Maps for all Coptic Orthodox churches in NJ
2. Get detailed info for each church
3. Save to SQLite database (`google_places_churches` table)
4. **One-time operation** - only run when you want to update church data

## 📊 What You'll Get

```
✅ SUCCESS! Discovered 47 Coptic Orthodox churches in NJ
💾 Saved to database: coptic_events.db (table: google_places_churches)

📊 Sample churches:

1. St. Mary & St. Mercurius Coptic Orthodox Church
   📍 123 Main St, Belleville, NJ 07109
   📞 (973) 555-1234
   🌐 http://www.smandsm.org
   ⭐ 4.8/5 (156 reviews)

2. Virgin Mary & St. John Coptic Orthodox Church
   📍 456 Church Ave, Bayonne, NJ 07002
   📞 (201) 555-5678
   🌐 http://www.saintsmaryandjohn.org
   ⭐ 4.9/5 (203 reviews)
```

## 🔧 Integrate with Existing App

Once you have the database populated, you can:

1. **Use Google Places churches instead of NIHOV**
2. **Much better data quality**:
   - Verified addresses
   - Working phone numbers
   - Accurate website URLs
   - Real customer reviews

3. **Update church discovery** to use SQL database:
```python
# Instead of scraping NIHOV
churches = load_from_google_places_db()

# Filter by radius (already have lat/lon)
nearby = filter_by_radius(churches, user_lat, user_lon, radius_miles)

# Scrape events from verified websites
events = scrape_events(nearby)
```

## 🔄 When to Re-Run

Churches don't change often, but you can re-run monthly or quarterly to:
- Catch new churches
- Update phone numbers
- Get latest reviews
- Update hours of operation

## 💡 Advanced: Multi-State Discovery

To discover churches in multiple states:

```python
from src.google_places_discovery import GooglePlacesChurchDiscovery

discovery = GooglePlacesChurchDiscovery(api_key)

# Discover churches in multiple states
for state in ['NJ', 'NY', 'CT', 'PA']:
    churches = discovery.search_churches_in_state(state)
    discovery.save_to_database(churches)
```

## 🛡️ Security Best Practices

1. **Don't commit API key to git**
   - Already in `.gitignore`
   - Use environment variables only

2. **Restrict API key** (in Google Cloud Console)
   - Limit to Places API only
   - Set application restrictions if needed

3. **Monitor usage**
   - Check: https://console.cloud.google.com/apis/dashboard
   - Stay under free tier

## 📈 Cost Monitoring

Check your usage:
1. Go to: https://console.cloud.google.com/billing
2. View "Reports"
3. Filter by "Places API"

For our use case (60-100 churches in NJ):
- Text search: ~10 queries × $0.017 = $0.17
- Place details: ~60 churches × $0.032 = $1.92
- **Total: ~$2.09** (covered by $200 free credit)

## ❓ Troubleshooting

### "API key not set" error
```bash
echo $GOOGLE_PLACES_API_KEY
# Should print your key
# If empty, set it again
```

### "API not enabled" error
- Go to: https://console.cloud.google.com/apis/library
- Enable "Places API (New)"

### "INVALID_REQUEST" error
- Check API key restrictions
- Make sure billing is enabled (even for free tier)

### "OVER_QUERY_LIMIT" error
- Check usage dashboard
- Wait for monthly credit refresh
- Script has built-in rate limiting (0.2s delay)

## 🎉 Benefits vs NIHOV

| Feature | NIHOV | Google Places |
|---------|-------|---------------|
| Data accuracy | ⚠️ Mixed | ✅ Verified |
| Phone numbers | ⚠️ Sometimes | ✅ Always |
| Websites | ⚠️ Sometimes | ✅ Usually |
| Hours | ❌ No | ✅ Yes |
| Reviews | ❌ No | ✅ Yes |
| Photos | ❌ No | ✅ Yes |
| Coordinates | ⚠️ Via geocoding | ✅ Native |
| Global coverage | ✅ Yes | ✅ Yes |
| Cost | ✅ Free | ✅ Free (tier) |
| Quality | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Next Steps

1. Get your API key (5 minutes)
2. Run the discovery script
3. Check the database
4. Integrate with main app
5. Enjoy better church data! 🎉
