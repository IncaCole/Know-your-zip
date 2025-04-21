import re
from typing import Dict, Optional, Tuple

class ZIPValidator:
    def __init__(self):
        # Basic ZIP code pattern (5 digits)
        self.zip_pattern = re.compile(r'^\d{5}$')
        
        # Simple in-memory database of ZIP codes and their basic info
        # This is just a sample - in a real application, you'd want to use a proper database
        self.zip_database = {
            '10001': {'city': 'New York', 'state': 'NY', 'country': 'USA'},
            '90210': {'city': 'Beverly Hills', 'state': 'CA', 'country': 'USA'},
            '94105': {'city': 'San Francisco', 'state': 'CA', 'country': 'USA'},
            '60601': {'city': 'Chicago', 'state': 'IL', 'country': 'USA'},
            '75201': {'city': 'Dallas', 'state': 'TX', 'country': 'USA'},
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
            return False, "ZIP code not found in database.", None
            
        return True, "Valid ZIP code.", info 