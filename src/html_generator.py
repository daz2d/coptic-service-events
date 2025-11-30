"""HTML calendar generator for selected events"""

import logging
from typing import List
from datetime import datetime
from pathlib import Path
from src.event_model import ServiceEvent

logger = logging.getLogger(__name__)


class HTMLCalendarGenerator:
    """Generates interactive HTML calendar page"""
    
    def generate(self, events: List[ServiceEvent], output_file: str = "my_events.html") -> str:
        """Generate HTML file with Add to Calendar buttons"""
        if not events:
            logger.warning("No events to generate HTML for")
            return None
        
        html = self._build_html(events)
        
        # Write to file
        output_path = Path(output_file)
        output_path.write_text(html, encoding='utf-8')
        
        logger.info(f"Generated HTML calendar: {output_path.absolute()}")
        return str(output_path.absolute())
    
    def _build_html(self, events: List[ServiceEvent]) -> str:
        """Build complete HTML page"""
        # Sort events by date
        sorted_events = sorted(events, key=lambda e: (e.date if e.date != 'TBD' else '9999-12-31', e.time if e.time != 'TBD' else '23:59'))
        
        event_cards = '\n'.join([self._build_event_card(event, i) for i, event in enumerate(sorted_events)])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Coptic Orthodox Events</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            color: #2d3748;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #718096;
            font-size: 1.1rem;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #718096;
            font-size: 0.9rem;
        }}
        
        .events-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .event-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .event-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .event-type {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}
        
        .type-service {{ background: #d4edda; color: #155724; }}
        .type-mission {{ background: #fff3cd; color: #856404; }}
        .type-social {{ background: #cce5ff; color: #004085; }}
        .type-festival {{ background: #f8d7da; color: #721c24; }}
        
        .event-title {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 12px;
            line-height: 1.3;
        }}
        
        .event-church {{
            color: #667eea;
            font-weight: 600;
            margin-bottom: 12px;
            font-size: 0.95rem;
        }}
        
        .event-details {{
            margin: 12px 0;
        }}
        
        .detail-row {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            color: #4a5568;
            font-size: 0.9rem;
        }}
        
        .detail-icon {{
            margin-right: 8px;
            font-size: 1.1rem;
        }}
        
        .event-description {{
            color: #718096;
            font-size: 0.9rem;
            line-height: 1.5;
            margin: 12px 0;
            max-height: 60px;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .event-actions {{
            display: flex;
            gap: 10px;
            margin-top: 16px;
        }}
        
        .btn {{
            flex: 1;
            padding: 10px 16px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            text-align: center;
            font-size: 0.9rem;
        }}
        
        .btn-calendar {{
            background: #667eea;
            color: white;
        }}
        
        .btn-calendar:hover {{
            background: #5568d3;
        }}
        
        .btn-details {{
            background: #e2e8f0;
            color: #2d3748;
        }}
        
        .btn-details:hover {{
            background: #cbd5e0;
        }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            padding: 20px;
        }}
        
        .modal-content {{
            background: white;
            margin: 50px auto;
            padding: 30px;
            border-radius: 12px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .modal-header {{
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .modal-title {{
            font-size: 1.5rem;
            color: #2d3748;
            margin-bottom: 10px;
        }}
        
        .close {{
            float: right;
            font-size: 28px;
            font-weight: bold;
            color: #718096;
            cursor: pointer;
        }}
        
        .close:hover {{
            color: #2d3748;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕊️ My Coptic Orthodox Events</h1>
            <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{len(events)}</div>
                    <div class="stat-label">Selected Events</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{len(set(e.church_name for e in events))}</div>
                    <div class="stat-label">Churches</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{len([e for e in events if e.date != 'TBD'])}</div>
                    <div class="stat-label">Scheduled</div>
                </div>
            </div>
        </div>
        
        <div class="events-grid">
            {event_cards}
        </div>
    </div>
    
    <div id="eventModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modalBody"></div>
        </div>
    </div>
    
    <script>
        function addToGoogleCalendar(title, church, date, time, location, description, url) {{
            // Format for Google Calendar
            let startDate = date !== 'TBD' ? date.replace(/-/g, '') : '';
            let startTime = time !== 'TBD' ? time.replace(/:/g, '') : '120000';
            
            // If no date, default to next month
            if (!startDate) {{
                let nextMonth = new Date();
                nextMonth.setMonth(nextMonth.getMonth() + 1);
                startDate = nextMonth.toISOString().split('T')[0].replace(/-/g, '');
            }}
            
            let fullTitle = encodeURIComponent(title + ' - ' + church);
            let fullLocation = encodeURIComponent(location);
            let fullDescription = encodeURIComponent(description + '\\n\\nSource: ' + url);
            
            let googleUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${{fullTitle}}&dates=${{startDate}}T${{startTime}}/${{startDate}}T${{startTime}}&location=${{fullLocation}}&details=${{fullDescription}}`;
            
            window.open(googleUrl, '_blank');
        }}
        
        function showDetails(eventData) {{
            let modal = document.getElementById('eventModal');
            let modalBody = document.getElementById('modalBody');
            
            let html = `
                <div class="modal-header">
                    <span class="close">&times;</span>
                    <h2 class="modal-title">${{eventData.title}}</h2>
                    <p style="color: #667eea; font-weight: 600;">${{eventData.church}}</p>
                </div>
                <div class="event-details">
                    <div class="detail-row"><span class="detail-icon">📅</span> ${{eventData.date}} at ${{eventData.time}}</div>
                    <div class="detail-row"><span class="detail-icon">📍</span> ${{eventData.location}}</div>
                    <div class="detail-row"><span class="detail-icon">🏷️</span> ${{eventData.type}}</div>
                    ${{eventData.distance ? '<div class="detail-row"><span class="detail-icon">📏</span> ' + eventData.distance + ' miles away</div>' : ''}}
                </div>
                <div style="margin: 20px 0;">
                    <h3 style="margin-bottom: 10px;">Description</h3>
                    <p style="color: #4a5568; line-height: 1.6;">${{eventData.description}}</p>
                </div>
                ${{eventData.contact ? '<div style="margin: 20px 0;"><h3 style="margin-bottom: 10px;">Contact</h3><p>' + eventData.contact + '</p></div>' : ''}}
                ${{eventData.url ? '<div style="margin: 20px 0;"><a href="' + eventData.url + '" target="_blank" style="color: #667eea;">View Source</a></div>' : ''}}
            `;
            
            modalBody.innerHTML = html;
            modal.style.display = 'block';
            
            // Close button
            modal.querySelector('.close').onclick = function() {{
                modal.style.display = 'none';
            }};
        }}
        
        // Close modal on outside click
        window.onclick = function(event) {{
            let modal = document.getElementById('eventModal');
            if (event.target == modal) {{
                modal.style.display = 'none';
            }}
        }}
    </script>
</body>
</html>"""
        
        return html
    
    def _build_event_card(self, event: ServiceEvent, index: int) -> str:
        """Build HTML for a single event card"""
        # Determine event type class
        type_class = 'type-social'
        if event.is_mission_trip or 'mission' in event.event_type:
            type_class = 'type-mission'
        elif 'service' in event.event_type or any(x in event.event_type for x in ['food', 'homeless', 'hospital', 'nursing']):
            type_class = 'type-service'
        elif 'festival' in event.event_type or 'feast' in event.event_type:
            type_class = 'type-festival'
        
        # Escape quotes for JavaScript
        def escape_js(text):
            if not text:
                return ''
            return str(text).replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
        
        description = event.description or "No description available"
        contact_info = ""
        if event.contact_email or event.contact_phone:
            contact_info = f"{event.contact_email or ''} {event.contact_phone or ''}".strip()
        
        card = f"""
        <div class="event-card">
            <span class="event-type {type_class}">{event.event_type.replace('_', ' ')}</span>
            <h3 class="event-title">{escape_js(event.title)}</h3>
            <div class="event-church">📍 {escape_js(event.church_name)}</div>
            <div class="event-details">
                <div class="detail-row">
                    <span class="detail-icon">📅</span>
                    {event.date} at {event.time}
                </div>
                <div class="detail-row">
                    <span class="detail-icon">📍</span>
                    {escape_js(event.location)}
                </div>
                {f'<div class="detail-row"><span class="detail-icon">📏</span>{event.distance_miles} miles away</div>' if hasattr(event, 'distance_miles') and event.distance_miles else ''}
            </div>
            <div class="event-description">
                {escape_js(description[:150])}{'...' if len(description) > 150 else ''}
            </div>
            <div class="event-actions">
                <button class="btn btn-calendar" onclick="addToGoogleCalendar('{escape_js(event.title)}', '{escape_js(event.church_name)}', '{event.date}', '{event.time}', '{escape_js(event.location)}', '{escape_js(description)}', '{escape_js(event.source_url or '')}')">
                    📅 Add to Calendar
                </button>
                <button class="btn btn-details" onclick='showDetails({{
                    "title": "{escape_js(event.title)}",
                    "church": "{escape_js(event.church_name)}",
                    "date": "{event.date}",
                    "time": "{event.time}",
                    "location": "{escape_js(event.location)}",
                    "type": "{event.event_type.replace('_', ' ')}",
                    "distance": "{getattr(event, 'distance_miles', '') or ''}",
                    "description": "{escape_js(description)}",
                    "contact": "{escape_js(contact_info)}",
                    "url": "{escape_js(event.source_url or '')}"
                }})'>
                    ℹ️ Details
                </button>
            </div>
        </div>
        """
        
        return card
