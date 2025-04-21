"""
Data Extraction Module

This module provides functionality for extracting and processing ZIP code related data
from various sources including APIs and local files.
"""

import requests
import pandas as pd
from typing import Dict, List, Optional, Union
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataExtractor:
    """Class for handling data extraction operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DataExtractor.
        
        Args:
            api_key (str, optional): API key for external services
        """
        self.api_key = api_key
        self.session = requests.Session()
        
    def get_zip_code_data(self, zip_code: str) -> Dict:
        """
        Extract basic ZIP code information.
        
        Args:
            zip_code (str): The ZIP code to look up
            
        Returns:
            Dict: Dictionary containing ZIP code information
        """
        try:
            # Example API endpoint - replace with actual endpoint
            url = f"https://api.example.com/zip/{zip_code}"
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for ZIP code {zip_code}: {str(e)}")
            return {}
            
    def extract_from_csv(self, file_path: str) -> pd.DataFrame:
        """
        Extract data from a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: DataFrame containing the extracted data
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {str(e)}")
            return pd.DataFrame()
            
    def extract_from_excel(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Extract data from an Excel file.
        
        Args:
            file_path (str): Path to the Excel file
            sheet_name (str, optional): Specific sheet to extract
            
        Returns:
            pd.DataFrame: DataFrame containing the extracted data
        """
        try:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {str(e)}")
            return pd.DataFrame()
            
    def validate_zip_code(self, zip_code: str) -> bool:
        """
        Validate if a string is a valid US ZIP code.
        
        Args:
            zip_code (str): The ZIP code to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Basic US ZIP code validation (5 digits or 5+4 format)
        import re
        pattern = r'^\d{5}(-\d{4})?$'
        return bool(re.match(pattern, zip_code))
        
    def batch_extract(self, zip_codes: List[str]) -> List[Dict]:
        """
        Extract data for multiple ZIP codes.
        
        Args:
            zip_codes (List[str]): List of ZIP codes to process
            
        Returns:
            List[Dict]: List of dictionaries containing ZIP code information
        """
        results = []
        for zip_code in zip_codes:
            if self.validate_zip_code(zip_code):
                data = self.get_zip_code_data(zip_code)
                if data:
                    results.append(data)
            else:
                logger.warning(f"Invalid ZIP code format: {zip_code}")
        return results 