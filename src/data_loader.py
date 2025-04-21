"""
Data Loader Module

This module provides functionality for loading and caching ZIP code related data
from various sources including APIs, local files, and cached data.
"""

import pandas as pd
import json
import os
from typing import Dict, List, Optional, Union, Any
import logging
from datetime import datetime, timedelta
import pickle
from pathlib import Path
import zipfile
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataLoader:
    """Class for handling data loading and caching operations."""
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize the DataLoader.
        
        Args:
            cache_dir (str): Directory to store cached data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_expiry = timedelta(days=1)  # Cache expiry time
        
    def _get_cache_path(self, key: str) -> Path:
        """Get the cache file path for a given key."""
        return self.cache_dir / f"{key}.pkl"
        
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if the cache is still valid."""
        if not cache_path.exists():
            return False
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - cache_time < self.cache_expiry
        
    def load_from_cache(self, key: str) -> Optional[Any]:
        """
        Load data from cache if available and valid.
        
        Args:
            key (str): Cache key identifier
            
        Returns:
            Optional[Any]: Cached data if available and valid, None otherwise
        """
        cache_path = self._get_cache_path(key)
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading cache for {key}: {str(e)}")
        return None
        
    def save_to_cache(self, key: str, data: Any) -> None:
        """
        Save data to cache.
        
        Args:
            key (str): Cache key identifier
            data (Any): Data to cache
        """
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving cache for {key}: {str(e)}")
            
    def load_zip_codes_from_file(self, file_path: str) -> List[str]:
        """
        Load ZIP codes from a text file.
        
        Args:
            file_path (str): Path to the text file containing ZIP codes
            
        Returns:
            List[str]: List of ZIP codes
        """
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error loading ZIP codes from file {file_path}: {str(e)}")
            return []
            
    def load_zip_dataframe(self, file_path: str, cache_key: Optional[str] = None) -> pd.DataFrame:
        """
        Load ZIP code data from a CSV or Excel file with optional caching.
        
        Args:
            file_path (str): Path to the data file
            cache_key (str, optional): Cache key to use for caching
            
        Returns:
            pd.DataFrame: DataFrame containing the ZIP code data
        """
        if cache_key:
            cached_data = self.load_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
                
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
                
            if cache_key:
                self.save_to_cache(cache_key, df)
                
            return df
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            return pd.DataFrame()
            
    def load_api_response(self, response_data: Dict, cache_key: Optional[str] = None) -> Dict:
        """
        Load and optionally cache API response data.
        
        Args:
            response_data (Dict): API response data
            cache_key (str, optional): Cache key to use for caching
            
        Returns:
            Dict: Processed API response data
        """
        if cache_key:
            cached_data = self.load_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
                
        try:
            # Process the response data as needed
            processed_data = {
                'timestamp': datetime.now().isoformat(),
                'data': response_data
            }
            
            if cache_key:
                self.save_to_cache(cache_key, processed_data)
                
            return processed_data
        except Exception as e:
            logger.error(f"Error processing API response: {str(e)}")
            return {}
            
    def clear_cache(self, key: Optional[str] = None) -> None:
        """
        Clear cache for a specific key or all cache.
        
        Args:
            key (str, optional): Specific cache key to clear
        """
        try:
            if key:
                cache_path = self._get_cache_path(key)
                if cache_path.exists():
                    cache_path.unlink()
            else:
                for cache_file in self.cache_dir.glob("*.pkl"):
                    cache_file.unlink()
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")

    def load_zip_archive(self, archive_path: str, file_pattern: str = "*.csv") -> Dict[str, pd.DataFrame]:
        """
        Load multiple data files from a ZIP archive.
        
        Args:
            archive_path (str): Path to the ZIP archive
            file_pattern (str): Pattern to match files within the archive
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping filenames to DataFrames
        """
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                dataframes = {}
                for file in zip_ref.namelist():
                    if file.endswith(('.csv', '.xlsx', '.xls')):
                        with zip_ref.open(file) as f:
                            if file.endswith('.csv'):
                                df = pd.read_csv(io.BytesIO(f.read()))
                            else:
                                df = pd.read_excel(io.BytesIO(f.read()))
                        dataframes[file] = df
                return dataframes
        except Exception as e:
            logger.error(f"Error loading ZIP archive {archive_path}: {str(e)}")
            return {}

    def load_zip_code_boundaries(self, file_path: str, cache_key: Optional[str] = None) -> Dict:
        """
        Load ZIP code boundary data (geographic boundaries).
        
        Args:
            file_path (str): Path to the boundary data file
            cache_key (str, optional): Cache key to use for caching
            
        Returns:
            Dict: Dictionary containing boundary data
        """
        if cache_key:
            cached_data = self.load_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        try:
            if file_path.endswith('.geojson') or file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
            elif file_path.endswith('.shp'):
                import geopandas as gpd
                data = gpd.read_file(file_path)
            else:
                raise ValueError(f"Unsupported boundary file format: {file_path}")

            if cache_key:
                self.save_to_cache(cache_key, data)

            return data
        except Exception as e:
            logger.error(f"Error loading boundary data from {file_path}: {str(e)}")
            return {}

    def load_zip_code_metadata(self, file_path: str, cache_key: Optional[str] = None) -> pd.DataFrame:
        """
        Load ZIP code metadata (population, demographics, etc.).
        
        Args:
            file_path (str): Path to the metadata file
            cache_key (str, optional): Cache key to use for caching
            
        Returns:
            pd.DataFrame: DataFrame containing ZIP code metadata
        """
        if cache_key:
            cached_data = self.load_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        try:
            df = self.load_zip_dataframe(file_path, cache_key)
            # Ensure ZIP code column is properly formatted
            if 'zip_code' in df.columns:
                df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)
            return df
        except Exception as e:
            logger.error(f"Error loading ZIP code metadata from {file_path}: {str(e)}")
            return pd.DataFrame()

    def merge_zip_data(self, 
                      primary_df: pd.DataFrame, 
                      secondary_df: pd.DataFrame, 
                      on: str = 'zip_code',
                      how: str = 'left') -> pd.DataFrame:
        """
        Merge two ZIP code datasets.
        
        Args:
            primary_df (pd.DataFrame): Primary dataset
            secondary_df (pd.DataFrame): Secondary dataset to merge
            on (str): Column to merge on
            how (str): Type of merge to perform
            
        Returns:
            pd.DataFrame: Merged dataset
        """
        try:
            return pd.merge(primary_df, secondary_df, on=on, how=how)
        except Exception as e:
            logger.error(f"Error merging ZIP code datasets: {str(e)}")
            return primary_df 