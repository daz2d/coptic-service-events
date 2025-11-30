# Finding Coptic Church Websites for Your Area

The bot is designed to scrape events from Coptic Orthodox church websites. However, you need to provide the actual website URLs.

## How to Find Church Websites in Your Area

### Method 1: Manual Search
1. **Google Search**: Search for "Coptic Orthodox Church [your city/state]"
2. **Visit church websites** and note their URLs
3. **Add URLs to config.json** under `data_sources.church_websites`

### Method 2: Diocese Website (If Available)
1. Find your diocese website (ask your priest or search online)
2. Look for a "Churches" or "Directory" page
3. Get the list of churches and their websites
4. Add to config.json

### Method 3: Ask Your Church
1. Ask your priest for a list of nearby Coptic churches
2. Get their website URLs
3. Add to config.json

## Example Configuration

```json
{
  "data_sources": {
    "church_websites": [
      "https://actual-church-url-1.org",
      "https://actual-church-url-2.org",
      "https://actual-church-url-3.org"
    ]
  }
}
```

## Verifying Church Websites

Before adding a website, check that it:
1. **Exists and loads** (visit it in your browser)
2. **Has an events page** (look for /events, /calendar, etc.)
3. **Actually posts events** (not just liturgy schedules)

## Example: Finding NJ Coptic Churches

For New Jersey area, you might search for:
- "Coptic Orthodox Church New Jersey"
- "Coptic Church Bergen County"
- "Coptic Church Hudson County"

Then visit each church's website to:
1. Confirm they have event listings
2. Note the URL format
3. Add working URLs to config.json

## If Diocese-First Approach Works

If you find an actual diocese website with a church directory:

1. **Update `src/diocese_scraper.py`**:
```python
DIOCESE_CONFIGS = {
    'your_area': {
        'url': 'https://actual-diocese-url.org',
        'churches_page': '/churches',  # or whatever path they use
        'name': 'Your Diocese Name',
        'states': ['YOUR', 'STATES']
    }
}
```

2. **Update `config.json`**:
```json
{
  "scraping_strategy": {
    "start_with_diocese": true,
    "discover_churches": true
  }
}
```

## Testing with Demo Data

Until you find actual church URLs, you can use the demo:

```bash
python quickstart.py
```

This shows how the bot works with sample events.

## Common Coptic Church Website Patterns

Many Coptic churches use these URL patterns:
- `st[saint-name][location].org`
- `[saint-name]church.org`
- `coptic[location].org`

Examples (these may or may not exist):
- `stmarkatlanta.org`
- `stgeorgela.org`
- `stmarynyc.org`

## Need Help?

1. Ask your priest for nearby church websites
2. Search Facebook for "Coptic Orthodox Church [your area]"
3. Contact your diocese office for a directory

Once you have real URLs, the bot will work perfectly!
