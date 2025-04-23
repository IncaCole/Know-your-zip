"""
This module contains healthcare-specific API implementations and utilities.
It provides interfaces for various healthcare-related APIs and data processing.
"""

from typing import Dict, Any, List, Optional
from infrastructure import APIInfrastructure
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class HealthcareAPI(APIInfrastructure):
    """Class for handling healthcare-related API operations."""
    
    def __init__(self):
        """Initialize the healthcare API with appropriate base URL and authentication."""
        super().__init__(
            base_url=os.getenv('HEALTHCARE_API_BASE_URL', 'https://api.healthcare.example.com'),
            api_key=os.getenv('HEALTHCARE_API_KEY')
        )
    
    def get_healthcare_providers(self, 
                               zip_code: str, 
                               radius: int = 10, 
                               provider_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get healthcare providers near a specific zip code.
        
        Args:
            zip_code (str): The zip code to search around
            radius (int): Search radius in miles
            provider_type (Optional[str]): Type of healthcare provider to filter by
            
        Returns:
            List[Dict[str, Any]]: List of healthcare providers
        """
        params = {
            'zip_code': zip_code,
            'radius': radius
        }
        if provider_type:
            params['provider_type'] = provider_type
            
        response = self.make_request(
            endpoint='providers/search',
            params=params
        )
        return response.json()
    
    def get_healthcare_metrics(self, 
                             zip_code: str, 
                             metric_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get healthcare metrics for a specific zip code.
        
        Args:
            zip_code (str): The zip code to get metrics for
            metric_type (Optional[str]): Specific type of metrics to retrieve
            
        Returns:
            Dict[str, Any]: Healthcare metrics data
        """
        params = {'zip_code': zip_code}
        if metric_type:
            params['metric_type'] = metric_type
            
        response = self.make_request(
            endpoint='metrics',
            params=params
        )
        return response.json()
    
    def get_healthcare_facilities(self, 
                                zip_code: str, 
                                facility_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get healthcare facilities in a specific zip code.
        
        Args:
            zip_code (str): The zip code to search in
            facility_type (Optional[str]): Type of healthcare facility to filter by
            
        Returns:
            List[Dict[str, Any]]: List of healthcare facilities
        """
        params = {'zip_code': zip_code}
        if facility_type:
            params['facility_type'] = facility_type
            
        response = self.make_request(
            endpoint='facilities',
            params=params
        )
        return response.json()

    def get_mental_health_centers(self) -> List[Dict[str, Any]]:
        """
        Get mental health centers from the ArcGIS API.
        
        Returns:
            List[Dict[str, Any]]: List of mental health centers with their details
        """
        url = "https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/MentalHealthCenter_gdb/FeatureServer/0/query"
        params = {
            'outFields': '*',
            'where': '1=1',
            'f': 'geojson'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('features', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching mental health centers: {e}")
            return []

    def get_free_standing_clinics(self) -> List[Dict[str, Any]]:
        """
        Get free-standing clinics from the ArcGIS API.
        
        Returns:
            List[Dict[str, Any]]: List of free-standing clinics with their details
        """
        url = "https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/FreeStandingClinic_gdb/FeatureServer/0/query"
        params = {
            'outFields': '*',
            'where': '1=1',
            'f': 'geojson'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('features', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching free-standing clinics: {e}")
            return []

# Example usage:
# healthcare_api = HealthcareAPI()
# providers = healthcare_api.get_healthcare_providers('12345', radius=5, provider_type='primary_care')
# metrics = healthcare_api.get_healthcare_metrics('12345')
# facilities = healthcare_api.get_healthcare_facilities('12345', facility_type='hospital')
# mental_health_centers = healthcare_api.get_mental_health_centers()
# free_standing_clinics = healthcare_api.get_free_standing_clinics() 