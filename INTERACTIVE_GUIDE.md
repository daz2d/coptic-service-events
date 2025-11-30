# Interactive Event Selection

## How It Works

When you run the app, it will:

1. **Discover events** within your radius (optimized with caching)
2. **Show you unique events** (deduplicated)
3. **Ask which ones you're interested in**
4. **Generate an HTML calendar** you can open in your browser

## Usage

```bash
python main.py --once
```

## Event Selection

When prompted, you can:

- **Select specific events**: `1,3,5` (events 1, 3, and 5)
- **Select ranges**: `1-5,10` (events 1 through 5, and event 10)
- **Select all**: Just press Enter
- **Select none**: Type `none`

Example:
```
Your selection: 1,3,5-7,10
```
This selects events: 1, 3, 5, 6, 7, and 10

## HTML Calendar Features

The generated `my_events.html` file includes:

✅ **Add to Google Calendar** - One-click button for each event  
✅ **Event Details** - Click to see full description, contact info, etc.  
✅ **Color-coded** - Different colors for service, mission, social, and festival events  
✅ **Responsive** - Works on desktop, tablet, and mobile  
✅ **Distance info** - Shows how far each church is from you  

## Example Output

```
============================================================
FOUND 7 UNIQUE EVENTS
============================================================

1. Clergy Meeting
   📍 Our Lady Of Zeitoun Church [Staten Island]
   📅 TBD at TBD
   🏷️  social_gathering
   📏 8.5 miles away

2. Youth Retreat
   📍 St. Mark Church [Jersey City]
   📅 2025-12-15 at 09:00
   🏷️  retreat
   📏 12.3 miles away

...

Which events are you interested in?
Enter numbers separated by commas (e.g., 1,3,5-7,10)
Or press Enter to select ALL events
Or type 'none' to skip

Your selection: 1-3,5

✅ Selected 4 events

✅ Generated interactive calendar: /home/minaa/coptic-service-events/my_events.html

Open this file in your browser to:
  • View all selected events
  • Add events to Google Calendar with one click
  • See full event details
```

## Tips

- Events are automatically deduplicated by title, church, date, and time
- The HTML file is regenerated each time you run the app
- You can select different events on each run
- The calendar works offline - just open the HTML file anytime
