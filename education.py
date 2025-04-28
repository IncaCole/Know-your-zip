"""
Education API Module

This module provides functionality for accessing and processing education-related data
from various APIs, including school information, ratings, and statistics.
"""

import requests
import pandas as pd
from typing import Dict, List, Optional, Union, Any
import logging
from datetime import datetime
from src.utils.response_normalizer import success_response, error_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoints for education data
EDUCATION_API_ENDPOINTS = {
    'public_schools': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/SchoolSite_gdb/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson',
    'private_schools': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/PrivateSchool_gdb/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson',
    'charter_schools': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/CharterSchool_gdb/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson',
    'school_ratings': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/SchoolRatings/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson',
    'school_boundaries': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/SchoolBoundaries/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson'
}

class EducationAPI:
    """Class for handling education-related API operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the EducationAPI.
        
        Args:
            api_key (str, optional): API key for external services
        """
        self.api_key = api_key
        self.session = requests.Session()
        
    def fetch_data_with_retry(self, endpoint: str, max_retries: int = 3, retry_delay: int = 2) -> Optional[Dict[str, Any]]:
        """
        Fetch data from API with retry mechanism.
        
        Args:
            endpoint: API endpoint URL
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Dict containing the API response data or None if all attempts fail
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to fetch data from {endpoint} (attempt {attempt + 1}/{max_retries})")
                response = self.session.get(endpoint)
                response.raise_for_status()
                logger.info(f"Successfully fetched data from {endpoint}")
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to fetch data from {endpoint}: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"All {max_retries} attempts failed for {endpoint}")
                    return None

    def get_schools_by_zip(self, zip_code: str, school_type: str = 'all') -> Dict[str, Any]:
        """
        Get schools within a specific ZIP code.
        
        Args:
            zip_code: The ZIP code to search for schools
            school_type: Type of schools to return ('public', 'private', 'charter', or 'all')
            
        Returns:
            Dict containing school information
        """
        try:
            schools = []
            
            if school_type in ['public', 'all']:
                public_data = self.fetch_data_with_retry(EDUCATION_API_ENDPOINTS['public_schools'])
                if public_data and 'features' in public_data:
                    for feature in public_data['features']:
                        properties = feature.get('properties', {})
                        # Include schools in the target ZIP code and adjacent ones
                        feature_zip = str(properties.get('ZIPCODE', '')).strip()
                        if feature_zip and (feature_zip == str(zip_code) or 
                            # Include schools with similar ZIP codes (first 3 digits match)
                            (len(feature_zip) == 5 and len(str(zip_code)) == 5 and 
                             feature_zip[:3] == str(zip_code)[:3])):
                            properties['school_type'] = 'public'
                            schools.append(properties)
            
            if school_type in ['private', 'all']:
                private_data = self.fetch_data_with_retry(EDUCATION_API_ENDPOINTS['private_schools'])
                if private_data and 'features' in private_data:
                    for feature in private_data['features']:
                        properties = feature.get('properties', {})
                        # Include schools in the target ZIP code and adjacent ones
                        feature_zip = str(properties.get('ZIPCODE', '')).strip()
                        if feature_zip and (feature_zip == str(zip_code) or 
                            # Include schools with similar ZIP codes (first 3 digits match)
                            (len(feature_zip) == 5 and len(str(zip_code)) == 5 and 
                             feature_zip[:3] == str(zip_code)[:3])):
                            properties['school_type'] = 'private'
                            schools.append(properties)
            
            if school_type in ['charter', 'all']:
                charter_data = self.fetch_data_with_retry(EDUCATION_API_ENDPOINTS['charter_schools'])
                if charter_data and 'features' in charter_data:
                    for feature in charter_data['features']:
                        properties = feature.get('properties', {})
                        # Include schools in the target ZIP code and adjacent ones
                        feature_zip = str(properties.get('ZIPCODE', '')).strip()
                        if feature_zip and (feature_zip == str(zip_code) or 
                            # Include schools with similar ZIP codes (first 3 digits match)
                            (len(feature_zip) == 5 and len(str(zip_code)) == 5 and 
                             feature_zip[:3] == str(zip_code)[:3])):
                            properties['school_type'] = 'charter'
                            schools.append(properties)
            
            return success_response(
                message=f"Found {len(schools)} schools in and around ZIP code {zip_code}",
                data={'schools': schools}
            )
        except Exception as e:
            logger.error(f"Error getting schools for ZIP code {zip_code}: {str(e)}")
            return error_response(
                message=f"Error processing school data: {str(e)}",
                error_code="PROCESSING_ERROR"
            )

    def get_school_by_name(self, name: str, school_type: str = 'all') -> Dict[str, Any]:
        """
        Get school information by name.
        
        Args:
            name: The name of the school to search for
            school_type: Type of schools to search ('public', 'private', or 'all')
            
        Returns:
            Dict containing school information
        """
        try:
            schools = []
            
            if school_type in ['public', 'all']:
                public_data = self.fetch_data_with_retry(EDUCATION_API_ENDPOINTS['public_schools'])
                if public_data and 'features' in public_data:
                    for feature in public_data['features']:
                        properties = feature.get('properties', {})
                        if name.lower() in properties.get('NAME', '').lower():
                            properties['school_type'] = 'public'
                            schools.append(properties)
            
            if school_type in ['private', 'all']:
                private_data = self.fetch_data_with_retry(EDUCATION_API_ENDPOINTS['private_schools'])
                if private_data and 'features' in private_data:
                    for feature in private_data['features']:
                        properties = feature.get('properties', {})
                        if name.lower() in properties.get('NAME', '').lower():
                            properties['school_type'] = 'private'
                            schools.append(properties)
            
            if schools:
                return success_response(
                    message=f"Found {len(schools)} schools matching '{name}'",
                    data={'schools': schools}
                )
            return error_response(
                message=f"No schools found matching '{name}'",
                error_code="NOT_FOUND"
            )
        except Exception as e:
            logger.error(f"Error searching for school '{name}': {str(e)}")
            return error_response(
                message=f"Error processing school search: {str(e)}",
                error_code="PROCESSING_ERROR"
            )

    def get_school_ratings(self, school_id: str) -> Dict[str, Any]:
        """
        Get ratings for a specific school.
        
        Args:
            school_id: The ID of the school to get ratings for
            
        Returns:
            Dict containing school ratings
        """
        try:
            data = self.fetch_data_with_retry(EDUCATION_API_ENDPOINTS['school_ratings'])
            if data and 'features' in data:
                for feature in data['features']:
                    properties = feature.get('properties', {})
                    if properties.get('SCHOOL_ID') == school_id:
                        return success_response(
                            message=f"Found ratings for school {school_id}",
                            data={'ratings': properties}
                        )
                return error_response(
                    message=f"No ratings found for school {school_id}",
                    error_code="NOT_FOUND"
                )
            return error_response(
                message="Failed to fetch school ratings",
                error_code="API_ERROR"
            )
        except Exception as e:
            logger.error(f"Error getting ratings for school {school_id}: {str(e)}")
            return error_response(
                message=f"Error processing school ratings: {str(e)}",
                error_code="PROCESSING_ERROR"
            )

    def get_school_boundary(self, school_id: str) -> Dict[str, Any]:
        """
        Get boundary information for a specific school.
        
        Args:
            school_id: The ID of the school to get boundary for
            
        Returns:
            Dict containing school boundary information
        """
        try:
            data = self.fetch_data_with_retry(EDUCATION_API_ENDPOINTS['school_boundaries'])
            if data and 'features' in data:
                for feature in data['features']:
                    properties = feature.get('properties', {})
                    if properties.get('SCHOOL_ID') == school_id:
                        return success_response(
                            message=f"Found boundary for school {school_id}",
                            data={'boundary': properties}
                        )
                return error_response(
                    message=f"No boundary found for school {school_id}",
                    error_code="NOT_FOUND"
                )
            return error_response(
                message="Failed to fetch school boundaries",
                error_code="API_ERROR"
            )
        except Exception as e:
            logger.error(f"Error getting boundary for school {school_id}: {str(e)}")
            return error_response(
                message=f"Error processing school boundary: {str(e)}",
                error_code="PROCESSING_ERROR"
            )

    def get_charter_schools_by_zip(self, zip_code: str) -> Dict[str, Any]:
        """
        Get charter schools within a specific ZIP code.
        
        Args:
            zip_code: The ZIP code to search for charter schools
            
        Returns:
            Dict containing charter school information
        """
        try:
            data = self.fetch_data_with_retry(EDUCATION_API_ENDPOINTS['charter_schools'])
            if data and 'features' in data:
                charter_schools = []
                for feature in data['features']:
                    properties = feature.get('properties', {})
                    if str(properties.get('ZIPCODE')) == str(zip_code):
                        properties['school_type'] = 'charter'
                        charter_schools.append(properties)
                
                return success_response(
                    message=f"Found {len(charter_schools)} charter schools in ZIP code {zip_code}",
                    data={'charter_schools': charter_schools}
                )
            return error_response(
                message="Failed to fetch charter school data",
                error_code="API_ERROR"
            )
        except Exception as e:
            logger.error(f"Error getting charter schools for ZIP code {zip_code}: {str(e)}")
            return error_response(
                message=f"Error processing charter school data: {str(e)}",
                error_code="PROCESSING_ERROR"
            )

def main():
    """Example usage of the EducationAPI class."""
    api = EducationAPI()
    
    # Example: Get all schools in a ZIP code
    zip_code = "33101"
    schools_response = api.get_schools_by_zip(zip_code)
    if schools_response['success']:
        print(f"Found {len(schools_response['data']['schools'])} schools in ZIP code {zip_code}")
    else:
        print(f"Error: {schools_response['message']}")
    
    # Example: Search for a school by name
    school_name = "Miami"
    search_response = api.get_school_by_name(school_name)
    if search_response['success']:
        print(f"Found {len(search_response['data']['schools'])} schools matching '{school_name}'")
    else:
        print(f"Error: {search_response['message']}")

if __name__ == "__main__":
    main() 