"""
This module contains emergency services-specific API implementations and utilities.
It provides interfaces for various emergency services-related APIs and data processing.
"""

from typing import Dict, Any, List, Optional
from infrastructure import APIInfrastructure
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class EmergencyServicesAPI(APIInfrastructure):
    """Class for handling emergency services-related API operations."""
    
    def __init__(self):
        """Initialize the emergency services API with appropriate base URL and authentication."""
        super().__init__(
            base_url=os.getenv('EMERGENCY_SERVICES_API_BASE_URL', 'https://api.emergency.example.com'),
            api_key=os.getenv('EMERGENCY_SERVICES_API_KEY')
        )
        self.police_stations_url = "https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/PoliceStation_gdb/FeatureServer/0/query"
        self.fire_stations_url = "https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/FireStation_gdb/FeatureServer/0/query"
    
    def get_emergency_services(self, 
                             zip_code: str, 
                             service_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get emergency services available in a specific zip code.
        
        Args:
            zip_code (str): The zip code to search in
            service_type (Optional[str]): Type of emergency service to filter by
            
        Returns:
            List[Dict[str, Any]]: List of emergency services
        """
        params = {'zip_code': zip_code}
        if service_type:
            params['service_type'] = service_type
            
        response = self.make_request(
            endpoint='services',
            params=params
        )
        return response.json()
    
    def get_emergency_response_times(self, 
                                   zip_code: str, 
                                   incident_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get emergency response times for a specific zip code.
        
        Args:
            zip_code (str): The zip code to get response times for
            incident_type (Optional[str]): Type of emergency incident to filter by
            
        Returns:
            Dict[str, Any]: Emergency response time data
        """
        params = {'zip_code': zip_code}
        if incident_type:
            params['incident_type'] = incident_type
            
        response = self.make_request(
            endpoint='response-times',
            params=params
        )
        return response.json()
    
    def get_emergency_facilities(self, 
                               zip_code: str, 
                               facility_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get emergency facilities in a specific zip code.
        
        Args:
            zip_code (str): The zip code to search in
            facility_type (Optional[str]): Type of emergency facility to filter by
            
        Returns:
            List[Dict[str, Any]]: List of emergency facilities
        """
        params = {'zip_code': zip_code}
        if facility_type:
            params['facility_type'] = facility_type
            
        response = self.make_request(
            endpoint='facilities',
            params=params
        )
        return response.json()
    
    def get_emergency_contacts(self, 
                             zip_code: str, 
                             contact_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get emergency contact information for a specific zip code.
        
        Args:
            zip_code (str): The zip code to get contacts for
            contact_type (Optional[str]): Type of emergency contact to filter by
            
        Returns:
            List[Dict[str, Any]]: List of emergency contacts
        """
        params = {'zip_code': zip_code}
        if contact_type:
            params['contact_type'] = contact_type
            
        response = self.make_request(
            endpoint='contacts',
            params=params
        )
        return response.json()
    
    def get_police_stations(self) -> Dict[str, Any]:
        """
        Get police stations data from the Miami-Dade County GIS service.
        
        Returns:
            Dict[str, Any]: GeoJSON data containing police station information
        """
        params = {
            'outFields': '*',
            'where': '1=1',
            'f': 'geojson'
        }
        
        response = requests.get(self.police_stations_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_fire_stations(self) -> Dict[str, Any]:
        """
        Get fire stations data from the Miami-Dade County GIS service.
        
        Returns:
            Dict[str, Any]: GeoJSON data containing fire station information
        """
        params = {
            'outFields': '*',
            'where': '1=1',
            'f': 'geojson'
        }
        
        response = requests.get(self.fire_stations_url, params=params)
        response.raise_for_status()
        return response.json()

# Example usage:
# emergency_api = EmergencyServicesAPI()
# services = emergency_api.get_emergency_services('12345', service_type='fire')
# response_times = emergency_api.get_emergency_response_times('12345', incident_type='medical')
# facilities = emergency_api.get_emergency_facilities('12345', facility_type='fire_station')
# contacts = emergency_api.get_emergency_contacts('12345', contact_type='police')
# police_stations = emergency_api.get_police_stations()
# fire_stations = emergency_api.get_fire_stations() 