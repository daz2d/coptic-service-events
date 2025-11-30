"""
Example: Mock event data for testing
This demonstrates the event structure and can be used for initial testing
"""

from datetime import datetime, timedelta
from src.event_model import ServiceEvent


def get_mock_events():
    """Generate mock events for testing"""
    
    today = datetime.now()
    
    events = [
        ServiceEvent(
            title="Food Pantry Service",
            church_name="St. Mark Coptic Orthodox Church",
            date=(today + timedelta(days=7)).strftime("%Y-%m-%d"),
            time="09:00",
            end_time="12:00",
            location="123 Church St, Los Angeles, CA 90001",
            event_type="food_pantry",
            description="Help distribute food to families in need. We serve approximately 100 families each week.",
            contact_person="Deacon John",
            contact_email="service@stmark.org",
            contact_phone="(555) 123-4567",
            registration_link="https://stmark.org/register/food-pantry",
            capacity=20,
            spots_available=8,
            requirements="Please wear comfortable clothes and closed-toe shoes",
            materials_needed=["Gloves", "Face mask"],
            diocese="Southern California Diocese",
            latitude=34.0522,
            longitude=-118.2437
        ),
        
        ServiceEvent(
            title="Homeless Outreach Downtown",
            church_name="St. Mary & St. Athanasius Coptic Orthodox Church",
            date=(today + timedelta(days=10)).strftime("%Y-%m-%d"),
            time="18:00",
            end_time="21:00",
            location="Downtown LA - Meeting at church",
            event_type="homeless_outreach",
            description="Join us as we provide meals, clothing, and spiritual support to our homeless brothers and sisters in downtown LA.",
            contact_person="Fr. Antonios",
            contact_email="outreach@stmary.org",
            registration_deadline=(today + timedelta(days=8)).strftime("%Y-%m-%d"),
            capacity=15,
            spots_available=5,
            requirements="Must be 16+ years old. Parental consent required for minors.",
            age_restrictions="16+",
            materials_needed=["Warm jacket", "Comfortable walking shoes"],
            diocese="Southern California Diocese",
            latitude=34.0407,
            longitude=-118.2468
        ),
        
        ServiceEvent(
            title="Hospital Visitation Team",
            church_name="St. George Coptic Orthodox Church",
            date=(today + timedelta(days=14)).strftime("%Y-%m-%d"),
            time="14:00",
            end_time="17:00",
            location="City Hospital, 456 Medical Ave, LA, CA 90002",
            event_type="hospital_visits",
            description="Visit and pray with Coptic Orthodox patients at City Hospital. Bring joy and comfort to those who are sick.",
            contact_person="Tasoni Mary",
            contact_email="hospital@stgeorge.org",
            contact_phone="(555) 234-5678",
            capacity=10,
            spots_available=10,
            requirements="Training session required before first visit",
            diocese="Southern California Diocese",
            latitude=34.0489,
            longitude=-118.2543
        ),
        
        ServiceEvent(
            title="Mexico Mission Trip - Orphanage Service",
            church_name="St. Peter & St. Paul Coptic Orthodox Church",
            date=(today + timedelta(days=60)).strftime("%Y-%m-%d"),
            time="08:00",
            location="Tijuana, Mexico (Departing from church)",
            event_type="mission_trips_international",
            description="Join us for a week-long mission trip to serve at an orphanage in Tijuana. We'll be helping with construction, teaching, and organizing activities for children.",
            contact_person="Mission Coordinator - Michael",
            contact_email="missions@stpeter.org",
            contact_phone="(555) 345-6789",
            registration_link="https://stpeter.org/mexico-mission",
            registration_deadline=(today + timedelta(days=45)).strftime("%Y-%m-%d"),
            capacity=30,
            spots_available=12,
            is_mission_trip=True,
            trip_duration_days=7,
            destination="Tijuana, Mexico",
            cost="$450 (includes transportation, accommodation, and meals)",
            requirements="Valid passport required. Must attend 3 preparation meetings.",
            age_restrictions="16+ (12+ with parent/guardian)",
            materials_needed=["Passport", "Sleeping bag", "Work clothes"],
            diocese="Southern California Diocese"
        ),
        
        ServiceEvent(
            title="Nursing Home Ministry",
            church_name="St. Mina Coptic Orthodox Church",
            date=(today + timedelta(days=5)).strftime("%Y-%m-%d"),
            time="15:00",
            end_time="17:00",
            location="Sunset Senior Living, 789 Elder Rd, LA, CA 90003",
            event_type="nursing_home",
            description="Spend time with elderly residents, play games, sing hymns, and share the love of Christ.",
            contact_person="Youth Servant - Christina",
            contact_email="youth@stmina.org",
            spots_available=15,
            age_restrictions="All ages welcome (children must be accompanied by parent)",
            diocese="Southern California Diocese",
            latitude=34.0355,
            longitude=-118.2712
        ),
        
        ServiceEvent(
            title="Appalachia Mission Trip",
            church_name="Coptic Orthodox Diocese of Southern USA",
            date=(today + timedelta(days=90)).strftime("%Y-%m-%d"),
            time="06:00",
            location="Kentucky (Departing from Atlanta)",
            event_type="mission_trips_domestic",
            description="Annual mission trip to serve impoverished communities in Appalachia. Home repair, food distribution, and community building.",
            contact_person="Diocese Mission Coordinator",
            contact_email="missions@suscopts.org",
            registration_link="https://suscopts.org/appalachia-mission",
            registration_deadline=(today + timedelta(days=70)).strftime("%Y-%m-%d"),
            capacity=50,
            spots_available=20,
            is_mission_trip=True,
            trip_duration_days=10,
            destination="Eastern Kentucky",
            cost="$350 (financial assistance available)",
            requirements="Must be 14+ and attend orientation",
            age_restrictions="14+",
            diocese="Southern USA Diocese"
        )
    ]
    
    return events


if __name__ == "__main__":
    # Demo: Print mock events
    events = get_mock_events()
    
    print(f"\n{'='*60}")
    print(f"MOCK EVENTS FOR TESTING ({len(events)} events)")
    print(f"{'='*60}\n")
    
    for i, event in enumerate(events, 1):
        print(f"{i}. {event.title}")
        print(f"   Church: {event.church_name}")
        print(f"   Date: {event.date} at {event.time}")
        print(f"   Type: {event.event_type}")
        if event.is_mission_trip:
            print(f"   🌍 MISSION TRIP - {event.destination} ({event.trip_duration_days} days)")
        print()
