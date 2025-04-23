"""
This module contains geographic data API implementations for various services.
It provides interfaces for flood zones, evacuation routes, and bus routes data.
"""

from typing import Dict, Any
import requests
from infrastructure import APIInfrastructure

class GeoDataAPI(APIInfrastructure):
    """Class for handling geographic data-related API operations."""
    
    def __init__(self):
        """Initialize the geographic data API with appropriate base URLs."""
        super().__init__(
            base_url="https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services"
        )
        self.flood_zones_url = f"{self.base_url}/FEMAFloodZone_gdb/FeatureServer/0/query"
        self.evacuation_routes_url = f"{self.base_url}/PrimaryEvacuationRoute_gdb/FeatureServer/0/query"
        self.bus_routes_url = f"{self.base_url}/BusRoutes/FeatureServer/0/query"
    
    def get_flood_zones(self) -> Dict[str, Any]:
        """
        Get flood zones data from the Miami-Dade County GIS service.
        
        Returns:
            Dict[str, Any]: GeoJSON data containing flood zone information
        """
        params = {
            'outFields': '*',
            'where': '1=1',
            'f': 'geojson'
        }
        
        response = requests.get(self.flood_zones_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_evacuation_routes(self) -> Dict[str, Any]:
        """
        Get evacuation routes data from the Miami-Dade County GIS service.
        
        Returns:
            Dict[str, Any]: GeoJSON data containing evacuation route information
        """
        params = {
            'outFields': '*',
            'where': '1=1',
            'f': 'geojson'
        }
        
        response = requests.get(self.evacuation_routes_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_bus_routes(self) -> Dict[str, Any]:
        """
        Get all bus routes from the Miami-Dade County GIS service.
        
        Returns:
            Dict[str, Any]: The bus routes data in GeoJSON format
        """
        params = {
            'outFields': '*',
            'where': '1=1',
            'f': 'geojson'
        }
        
        response = requests.get(self.bus_routes_url, params=params)
        response.raise_for_status()
        return response.json()

# Example usage:
# geo_api = GeoDataAPI()
# flood_zones = geo_api.get_flood_zones()
# evacuation_routes = geo_api.get_evacuation_routes()
# bus_routes = geo_api.get_bus_routes() 