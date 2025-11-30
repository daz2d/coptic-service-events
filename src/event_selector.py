"""Interactive event selector with HTML output"""

import logging
from typing import List
from src.event_model import ServiceEvent

logger = logging.getLogger(__name__)


class EventSelector:
    """Lets user interactively select events they're interested in"""
    
    def select_events(self, events: List[ServiceEvent]) -> List[ServiceEvent]:
        """Interactive selection of events"""
        if not events:
            print("\nNo events found.")
            return []
        
        # Deduplicate events by title + church + date
        unique_events = self._deduplicate_events(events)
        
        print(f"\n{'='*60}")
        print(f"FOUND {len(unique_events)} UNIQUE EVENTS")
        print(f"{'='*60}\n")
        
        # Display events with numbers
        for i, event in enumerate(unique_events, 1):
            print(f"{i}. {event.title}")
            print(f"   📍 {event.church_name}")
            print(f"   📅 {event.date} at {event.time}")
            print(f"   🏷️  {event.event_type}")
            if hasattr(event, 'distance_miles') and event.distance_miles:
                print(f"   📏 {event.distance_miles} miles away")
            print()
        
        # Ask user for selection
        print("Which events are you interested in?")
        print("Enter numbers separated by commas (e.g., 1,3,5-7,10)")
        print("Or press Enter to select ALL events")
        print("Or type 'none' to skip")
        
        selection = input("\nYour selection: ").strip()
        
        if selection.lower() == 'none':
            return []
        
        if not selection:
            # Select all
            return unique_events
        
        # Parse selection
        selected_indices = self._parse_selection(selection, len(unique_events))
        selected_events = [unique_events[i] for i in selected_indices]
        
        print(f"\n✅ Selected {len(selected_events)} events")
        return selected_events
    
    def _deduplicate_events(self, events: List[ServiceEvent]) -> List[ServiceEvent]:
        """Remove duplicate events based on title, church, and date"""
        seen = set()
        unique = []
        
        for event in events:
            # Create a unique key
            key = (
                event.title.lower().strip(),
                event.church_name.lower().strip(),
                event.date,
                event.time
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(event)
        
        logger.info(f"Deduplicated {len(events)} events to {len(unique)} unique events")
        return unique
    
    def _parse_selection(self, selection: str, max_index: int) -> List[int]:
        """Parse user selection like '1,3,5-7,10' into list of indices"""
        indices = set()
        
        parts = selection.split(',')
        for part in parts:
            part = part.strip()
            
            if '-' in part:
                # Range like 5-7
                try:
                    start, end = part.split('-')
                    start = int(start.strip())
                    end = int(end.strip())
                    
                    for i in range(start, end + 1):
                        if 1 <= i <= max_index:
                            indices.add(i - 1)  # Convert to 0-based
                except ValueError:
                    continue
            else:
                # Single number
                try:
                    num = int(part)
                    if 1 <= num <= max_index:
                        indices.add(num - 1)  # Convert to 0-based
                except ValueError:
                    continue
        
        return sorted(list(indices))
