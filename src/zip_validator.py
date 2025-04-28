import re
from typing import Dict, Optional, Tuple, List, Set
import pandas as pd
from geopy.distance import geodesic
import requests
import json
from shapely.geometry import Polygon, MultiPolygon, Point

class ZIPValidator:
    def __init__(self):
        # Basic ZIP code pattern (5 digits)
        self.zip_pattern = re.compile(r'^\d{5}$')
        
        # Miami-Dade County API endpoint
        self.api_endpoint = 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/ZipCode_gdb/FeatureServer/0/query'
        
        # Initialize ZIP code database
        self.zip_database: Dict[str, Dict] = {}
        self.refresh_zip_database()

    def fetch_zip_data(self) -> List[Dict]:
        """
        Fetch ZIP code data from Miami-Dade County API.
        
        Returns:
            List[Dict]: List of ZIP code data dictionaries
        """
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'geojson'
        }
        
        try:
            response = requests.get(self.api_endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'features' in data:
                return data['features']
        except Exception as e:
            print(f"Error fetching ZIP data: {str(e)}")
        
        return []

    def calculate_polygon_centroid(self, coordinates: List[List[float]]) -> Tuple[float, float]:
        """Calculate the centroid of a polygon"""
        lats = []
        lons = []
        for coord in coordinates:
            if isinstance(coord[0], list):
                # Handle nested coordinates (polygons)
                for point in coord:
                    lons.append(point[0])
                    lats.append(point[1])
            else:
                # Handle flat coordinates (points)
                lons.append(coord[0])
                lats.append(coord[1])
        
        return sum(lats) / len(lats), sum(lons) / len(lons)

    def refresh_zip_database(self):
        """Refresh the ZIP code database with latest data from API"""
        features = self.fetch_zip_data()
        
        for feature in features:
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            
            if 'ZIPCODE' in props and geom.get('coordinates'):
                zip_code = str(props['ZIPCODE'])
                coords = geom['coordinates']
                
                try:
                    # Calculate centroid based on geometry type
                    if geom['type'] == 'Polygon':
                        center_lat, center_lon = self.calculate_polygon_centroid(coords[0])
                    elif geom['type'] == 'Point':
                        center_lat, center_lon = coords[1], coords[0]
                    elif geom['type'] == 'MultiPolygon':
                        # Use the first polygon for the centroid
                        center_lat, center_lon = self.calculate_polygon_centroid(coords[0][0])
                    else:
                        print(f"Unsupported geometry type: {geom['type']}")
                        continue
                    
                    self.zip_database[zip_code] = {
                        'zipcode': zip_code,
                        'geometry': geom,
                        'center': (center_lat, center_lon),
                        'properties': props
                    }
                except Exception as e:
                    print(f"Error processing ZIP code {zip_code}: {str(e)}")

    def validate_format(self, zip_code: str) -> bool:
        """
        Validate if the ZIP code matches the standard 5-digit format.
        
        Args:
            zip_code (str): The ZIP code to validate
            
        Returns:
            bool: True if valid format, False otherwise
        """
        return bool(self.zip_pattern.match(zip_code))

    def get_zip_info(self, zip_code: str) -> Optional[Dict]:
        """
        Get information about a ZIP code if it exists in Miami-Dade County.
        
        Args:
            zip_code (str): The ZIP code to look up
            
        Returns:
            Optional[Dict]: Dictionary containing ZIP code information if found, None otherwise
        """
        if not self.validate_format(zip_code):
            return None
            
        return self.zip_database.get(zip_code)

    def get_nearby_zips(self, zip_code: str, radius_miles: float = 5.0) -> List[str]:
        """
        Get nearby ZIP codes within specified radius.
        
        Args:
            zip_code (str): The center ZIP code
            radius_miles (float): Radius in miles to search
            
        Returns:
            List[str]: List of nearby ZIP codes
        """
        if not self.validate_format(zip_code) or zip_code not in self.zip_database:
            return []
            
        center = self.zip_database[zip_code]['center']
        nearby = []
        
        for other_zip, data in self.zip_database.items():
            if other_zip != zip_code:
                distance = geodesic(center, data['center']).miles
                if distance <= radius_miles:
                    nearby.append(other_zip)
        
        return nearby

    def validate_zip(self, zip_code: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Comprehensive validation of a ZIP code.
        
        Args:
            zip_code (str): The ZIP code to validate
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: 
                - bool: Whether the ZIP code is valid
                - str: Message explaining the validation result
                - Optional[Dict]: ZIP code information if valid and found
        """
        if not self.validate_format(zip_code):
            return False, "Invalid ZIP code format. Must be 5 digits.", None
            
        info = self.get_zip_info(zip_code)
        if info is None:
            return False, "ZIP code not found in Miami-Dade County.", None
            
        return True, f"Valid Miami-Dade County ZIP code.", info

    def get_all_zip_codes(self) -> Set[str]:
        """
        Get all valid Miami-Dade County ZIP codes.
        
        Returns:
            Set[str]: Set of all valid ZIP codes
        """
        return set(self.zip_database.keys())

    def get_zip_coordinates(self, zip_code: str) -> Optional[Tuple[float, float]]:
        """
        Get the center coordinates of a ZIP code area.
        
        Args:
            zip_code (str): The ZIP code to look up
            
        Returns:
            Optional[Tuple[float, float]]: (latitude, longitude) if found, None otherwise
        """
        info = self.get_zip_info(zip_code)
        if info:
            return info['center']
        return None

    def get_zip_area(self, zip_code: str) -> float:
        """
        Get the approximate area of a ZIP code in square miles.
        
        Args:
            zip_code (str): The ZIP code to calculate area for
            
        Returns:
            float: Area in square miles, or 1.0 if calculation fails
        """
        info = self.get_zip_info(zip_code)
        if not info or 'geometry' not in info:
            return 1.0
            
        try:
            geom = info['geometry']
            if geom['type'] == 'Polygon':
                coords = geom['coordinates'][0]
                polygon = Polygon(coords)
                # Convert square degrees to approximate square miles
                # at Miami's latitude (25.7617° N)
                return polygon.area * 4000
            elif geom['type'] == 'MultiPolygon':
                total_area = 0
                for poly_coords in geom['coordinates']:
                    polygon = Polygon(poly_coords[0])
                    total_area += polygon.area
                return total_area * 4000
        except Exception as e:
            print(f"Error calculating area for ZIP {zip_code}: {str(e)}")
        
        return 1.0  # Default area if calculation fails

    def is_point_in_zip(self, lat: float, lon: float, zip_code: str) -> bool:
        """
        Check if a point falls within a ZIP code's boundaries.
        
        Args:
            lat (float): Latitude of the point
            lon (float): Longitude of the point
            zip_code (str): ZIP code to check
            
        Returns:
            bool: True if point is within ZIP code boundaries, False otherwise
        """
        info = self.get_zip_info(zip_code)
        if not info or 'geometry' not in info:
            return False
            
        try:
            point = Point(lon, lat)  # GeoJSON uses (lon, lat) order
            geom = info['geometry']
            
            if geom['type'] == 'Polygon':
                polygon = Polygon(geom['coordinates'][0])
                return polygon.contains(point)
            elif geom['type'] == 'MultiPolygon':
                for poly_coords in geom['coordinates']:
                    polygon = Polygon(poly_coords[0])
                    if polygon.contains(point):
                        return True
            
        except Exception as e:
            print(f"Error checking point in ZIP {zip_code}: {str(e)}")
        
        return False

    def get_zip_geojson(self) -> dict:
        """
        Get a GeoJSON object containing all ZIP code boundaries.
        
        Returns:
            dict: GeoJSON object with all ZIP code boundaries
        """
        features = []
        for zip_code, data in self.zip_database.items():
            if 'geometry' in data:
                feature = {
                    'type': 'Feature',
                    'properties': {
                        'ZIP_Code': zip_code
                    },
                    'geometry': data['geometry']
                }
                features.append(feature)
        
        return {
            'type': 'FeatureCollection',
            'features': features
        }

    def get_closest_zip(self, coordinates: Tuple[float, float]) -> Optional[str]:
        """
        Find the closest ZIP code to the given coordinates.
        
        Args:
            coordinates (Tuple[float, float]): (latitude, longitude) coordinates
            
        Returns:
            Optional[str]: The closest ZIP code if found, None otherwise
        """
        if not coordinates or len(coordinates) != 2:
            return None
            
        lat, lon = coordinates
        # Check if coordinates are within Miami-Dade County bounds (with some padding)
        if not (24.8 <= lat <= 26.2 and -81.0 <= lon <= -79.8):
            return None
            
        closest_zip = None
        min_distance = float('inf')
        
        for zip_code, data in self.zip_database.items():
            if 'center' not in data:
                continue
                
            zip_center = data['center']
            try:
                distance = geodesic(coordinates, zip_center).miles
                if distance < min_distance:
                    min_distance = distance
                    closest_zip = zip_code
            except Exception as e:
                print(f"Error calculating distance for ZIP {zip_code}: {str(e)}")
                continue
        
        # Only return if we found a reasonably close ZIP code (within 10 miles)
        if closest_zip and min_distance <= 10:
            return closest_zip
        return None 