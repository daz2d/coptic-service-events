"""Event data model"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List


@dataclass
class ServiceEvent:
    """Represents a service/volunteer event"""
    
    # Required fields
    title: str
    church_name: str
    date: str  # ISO format YYYY-MM-DD
    time: str  # HH:MM format
    location: str
    event_type: str
    
    # Optional fields
    description: Optional[str] = None
    end_time: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    registration_link: Optional[str] = None
    registration_deadline: Optional[str] = None
    capacity: Optional[int] = None
    spots_available: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    requirements: Optional[str] = None
    age_restrictions: Optional[str] = None
    materials_needed: Optional[List[str]] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    diocese: Optional[str] = None
    
    # Mission trip specific
    is_mission_trip: bool = False
    trip_duration_days: Optional[int] = None
    destination: Optional[str] = None
    cost: Optional[str] = None
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)
    
    def to_calendar_event(self):
        """Convert to Google Calendar event format"""
        start_datetime = f"{self.date}T{self.time}:00"
        
        # Calculate end time (default 2 hours if not specified)
        if self.end_time:
            end_datetime = f"{self.date}T{self.end_time}:00"
        else:
            from datetime import datetime, timedelta
            start = datetime.fromisoformat(start_datetime)
            end = start + timedelta(hours=2)
            end_datetime = end.isoformat()
        
        description_parts = []
        if self.description:
            description_parts.append(self.description)
        
        description_parts.append(f"\n\n📍 Location: {self.location}")
        
        if self.contact_person:
            description_parts.append(f"👤 Contact: {self.contact_person}")
        if self.contact_email:
            description_parts.append(f"📧 Email: {self.contact_email}")
        if self.contact_phone:
            description_parts.append(f"📞 Phone: {self.contact_phone}")
        if self.registration_link:
            description_parts.append(f"🔗 Register: {self.registration_link}")
        if self.registration_deadline:
            description_parts.append(f"⏰ Registration Deadline: {self.registration_deadline}")
        if self.capacity and self.spots_available:
            description_parts.append(f"👥 Spots: {self.spots_available}/{self.capacity}")
        if self.requirements:
            description_parts.append(f"📋 Requirements: {self.requirements}")
        if self.materials_needed:
            description_parts.append(f"🎒 Bring: {', '.join(self.materials_needed)}")
        
        if self.is_mission_trip:
            description_parts.append(f"\n✈️ MISSION TRIP")
            if self.destination:
                description_parts.append(f"Destination: {self.destination}")
            if self.trip_duration_days:
                description_parts.append(f"Duration: {self.trip_duration_days} days")
            if self.cost:
                description_parts.append(f"Cost: {self.cost}")
        
        calendar_event = {
            'summary': f"{self.title} - {self.church_name}",
            'location': self.location,
            'description': '\n'.join(description_parts),
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'America/New_York',  # TODO: Make configurable
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'America/New_York',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 60},  # 1 hour before
                ],
            },
        }
        
        return calendar_event
