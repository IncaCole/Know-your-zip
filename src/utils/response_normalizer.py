"""
Response Normalizer Module

This module provides functions to standardize API responses across the application.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NormalizedResponse:
    success: bool
    data: Optional[Union[Dict, List, Any]] = None
    error: Optional[str] = None
    timestamp: str = datetime.now().isoformat()
    status_code: Optional[int] = None

def normalize_response(
    response_data: Any,
    status_code: int = 200,
    error: Optional[str] = None
) -> NormalizedResponse:
    """
    Normalize API response into a consistent format.
    
    Args:
        response_data: The raw response data from the API
        status_code: HTTP status code
        error: Error message if any
        
    Returns:
        NormalizedResponse object with standardized format
    """
    success = status_code < 400 and error is None
    
    return NormalizedResponse(
        success=success,
        data=response_data if success else None,
        error=error,
        status_code=status_code
    )

def normalize_error(
    error_message: str,
    status_code: int = 500
) -> NormalizedResponse:
    """
    Normalize error responses into a consistent format.
    
    Args:
        error_message: The error message to include
        status_code: HTTP status code
        
    Returns:
        NormalizedResponse object with error information
    """
    return NormalizedResponse(
        success=False,
        error=error_message,
        status_code=status_code
    )

def is_valid_response(response: NormalizedResponse) -> bool:
    """
    Validate if a normalized response is valid.
    
    Args:
        response: NormalizedResponse object to validate
        
    Returns:
        bool indicating if the response is valid
    """
    if not isinstance(response, NormalizedResponse):
        return False
    
    if response.success and response.error is not None:
        return False
    
    if not response.success and response.data is not None:
        return False
    
    return True

def success_response(message: str, data: dict = None) -> dict:
    """
    Create a standardized success response.
    
    Args:
        message: Success message
        data: Optional data to include in the response
        
    Returns:
        Dict containing the standardized success response
    """
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return response

def error_response(message: str, error_code: str = None) -> dict:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        error_code: Optional error code
        
    Returns:
        Dict containing the standardized error response
    """
    response = {
        'success': False,
        'message': message
    }
    if error_code is not None:
        response['error_code'] = error_code
    return response 