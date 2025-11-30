"""Database for storing events"""

import logging
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.event_model import ServiceEvent

logger = logging.getLogger(__name__)


class EventDatabase:
    """Manages event storage and retrieval"""
    
    def __init__(self, db_path: str = 'coptic_events.db'):
        self.db_path = Path(db_path)
        self.conn = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                church_name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                location TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT,
                end_time TEXT,
                contact_person TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                registration_link TEXT,
                registration_deadline TEXT,
                capacity INTEGER,
                spots_available INTEGER,
                address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                latitude REAL,
                longitude REAL,
                requirements TEXT,
                age_restrictions TEXT,
                materials_needed TEXT,
                source_url TEXT,
                image_url TEXT,
                diocese TEXT,
                is_mission_trip INTEGER DEFAULT 0,
                trip_duration_days INTEGER,
                destination TEXT,
                cost TEXT,
                created_at TEXT,
                updated_at TEXT,
                UNIQUE(title, church_name, date, time)
            )
        ''')
        
        self.conn.commit()
        logger.info("Database initialized")
    
    def event_exists(self, event: ServiceEvent) -> bool:
        """Check if event already exists"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM events 
            WHERE title = ? AND church_name = ? AND date = ? AND time = ?
        ''', (event.title, event.church_name, event.date, event.time))
        
        count = cursor.fetchone()[0]
        return count > 0
    
    def add_event(self, event: ServiceEvent) -> int:
        """Add new event to database"""
        cursor = self.conn.cursor()
        
        now = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO events (
                    title, church_name, date, time, location, event_type,
                    description, end_time, contact_person, contact_email, contact_phone,
                    registration_link, registration_deadline, capacity, spots_available,
                    address, city, state, zip_code, latitude, longitude,
                    requirements, age_restrictions, materials_needed,
                    source_url, image_url, diocese,
                    is_mission_trip, trip_duration_days, destination, cost,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.title, event.church_name, event.date, event.time, 
                event.location, event.event_type,
                event.description, event.end_time, event.contact_person, 
                event.contact_email, event.contact_phone,
                event.registration_link, event.registration_deadline, 
                event.capacity, event.spots_available,
                event.address, event.city, event.state, event.zip_code, 
                event.latitude, event.longitude,
                event.requirements, event.age_restrictions,
                json.dumps(event.materials_needed) if event.materials_needed else None,
                event.source_url, event.image_url, event.diocese,
                1 if event.is_mission_trip else 0, event.trip_duration_days, 
                event.destination, event.cost,
                now, now
            ))
            
            self.conn.commit()
            event_id = cursor.lastrowid
            logger.info(f"Added event to database: {event.title} (ID: {event_id})")
            return event_id
            
        except sqlite3.IntegrityError:
            logger.warning(f"Event already exists: {event.title}")
            return -1
    
    def get_all_events(self) -> list:
        """Get all events from database"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM events ORDER BY date, time')
        return cursor.fetchall()
    
    def get_upcoming_events(self, days: int = 30) -> list:
        """Get upcoming events within specified days"""
        cursor = self.conn.cursor()
        today = datetime.now().date().isoformat()
        
        cursor.execute('''
            SELECT * FROM events 
            WHERE date >= ? 
            ORDER BY date, time
            LIMIT ?
        ''', (today, days))
        
        return cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
