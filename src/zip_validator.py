import re
from typing import Dict, Optional, Tuple

class ZIPValidator:
    def __init__(self):
        # Basic ZIP code pattern (5 digits)
        self.zip_pattern = re.compile(r'^\d{5}$')
        
        # South Florida ZIP code database
        self.zip_database = {
            # Miami-Dade County
            '33101': {'city': 'Miami', 'state': 'FL', 'county': 'Miami-Dade', 'area': 'Downtown Miami'},
            '33139': {'city': 'Miami Beach', 'state': 'FL', 'county': 'Miami-Dade', 'area': 'South Beach'},
            '33156': {'city': 'Miami', 'state': 'FL', 'county': 'Miami-Dade', 'area': 'Pinecrest'},
            '33180': {'city': 'Miami', 'state': 'FL', 'county': 'Miami-Dade', 'area': 'Aventura'},
            
            # Broward County
            '33301': {'city': 'Fort Lauderdale', 'state': 'FL', 'county': 'Broward', 'area': 'Downtown'},
            '33304': {'city': 'Fort Lauderdale', 'state': 'FL', 'county': 'Broward', 'area': 'Beach Area'},
            '33023': {'city': 'Hollywood', 'state': 'FL', 'county': 'Broward', 'area': 'West Hollywood'},
            '33324': {'city': 'Plantation', 'state': 'FL', 'county': 'Broward', 'area': 'Central Plantation'},
            
            # Palm Beach County
            '33401': {'city': 'West Palm Beach', 'state': 'FL', 'county': 'Palm Beach', 'area': 'Downtown'},
            '33432': {'city': 'Boca Raton', 'state': 'FL', 'county': 'Palm Beach', 'area': 'Downtown Boca'},
            '33480': {'city': 'Palm Beach', 'state': 'FL', 'county': 'Palm Beach', 'area': 'Palm Beach Island'},
            '33458': {'city': 'Jupiter', 'state': 'FL', 'county': 'Palm Beach', 'area': 'Jupiter'},
        }

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
        Get basic information about a ZIP code if it exists in the database.
        
        Args:
            zip_code (str): The ZIP code to look up
            
        Returns:
            Optional[Dict]: Dictionary containing ZIP code information if found, None otherwise
        """
        if not self.validate_format(zip_code):
            return None
            
        return self.zip_database.get(zip_code)

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
            return False, "ZIP code not found in South Florida database.", None
            
        return True, f"Valid South Florida ZIP code in {info['county']} County.", info 