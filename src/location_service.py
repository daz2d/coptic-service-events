"""Location service for determining search area"""

import logging
from typing import Tuple, Optional
import requests
from geopy.geocoders import Nominatim
from uszipcode import SearchEngine

logger = logging.getLogger(__name__)


class LocationService:
    """Handles location detection and geocoding"""
    
    def __init__(self, config):
        self.config = config
        self.geolocator = Nominatim(user_agent="coptic-events-bot")
        self.zip_search = SearchEngine()
    
    def get_location(self) -> Tuple[float, float, str]:
        """
        Get location coordinates and name
        Returns: (latitude, longitude, location_name)
        """
        if self.config.get('location.use_current_location'):
            return self._get_current_location()
        else:
            zip_code = self.config.get('location.zip_code')
            if not zip_code:
                raise ValueError("No location configured")
            return self._get_location_from_zip(zip_code)
    
    def _get_current_location(self) -> Tuple[float, float, str]:
        """Get current location from IP address"""
        try:
            response = requests.get('https://ipapi.co/json/', timeout=5)
            data = response.json()
            
            lat = data.get('latitude')
            lon = data.get('longitude')
            city = data.get('city')
            region = data.get('region')
            
            location_name = f"{city}, {region}"
            logger.info(f"Detected location: {location_name}")
            
            return lat, lon, location_name
        except Exception as e:
            logger.error(f"Error getting current location: {e}")
            raise
    
    def _get_location_from_zip(self, zip_code: str) -> Tuple[float, float, str]:
        """Get location from ZIP code"""
        try:
            zipcode_info = self.zip_search.by_zipcode(zip_code)
            
            if not zipcode_info or not zipcode_info.lat:
                raise ValueError(f"Invalid ZIP code: {zip_code}")
            
            lat = zipcode_info.lat
            lon = zipcode_info.lng
            location_name = f"{zipcode_info.major_city}, {zipcode_info.state}"
            
            logger.info(f"Location for ZIP {zip_code}: {location_name}")
            
            return lat, lon, location_name
        except Exception as e:
            logger.error(f"Error getting location from ZIP: {e}")
            raise
    
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """Calculate distance between two points in miles"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 3959.0  # Earth radius in miles
        
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Convert address to coordinates"""
        try:
            location = self.geolocator.geocode(address, timeout=10)
            if location:
                return location.latitude, location.longitude
            return None
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None
