from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from fastapi import status

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

class APIResponse:
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        status_code: int = status.HTTP_200_OK,
        error_code: Optional[str] = None
    ):
        self.success = success
        self.message = message
        self.data = data
        self.status_code = status_code
        self.error_code = error_code

    def to_dict(self) -> Dict[str, Any]:
        response = {
            "success": self.success,
            "message": self.message,
        }
        
        if self.data is not None:
            response["data"] = self.data
            
        if self.error_code is not None:
            response["error_code"] = self.error_code
            
        return response

def success_response(
    message: str = "Operation successful",
    data: Optional[Union[Dict[str, Any], list, Any]] = None,
    status_code: int = status.HTTP_200_OK
) -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        message: Success message
        data: Response data
        status_code: HTTP status code
        
    Returns:
        Dict containing the standardized response
    """
    response = APIResponse(
        success=True,
        message=message,
        data=data,
        status_code=status_code
    )
    return response.to_dict()

def error_response(
    message: str = "Operation failed",
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error_code: Optional[str] = None,
    data: Optional[Union[Dict[str, Any], list, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Optional error code for specific error types
        data: Additional error data if needed
        
    Returns:
        Dict containing the standardized error response
    """
    response = APIResponse(
        success=False,
        message=message,
        data=data,
        status_code=status_code,
        error_code=error_code
    )
    return response.to_dict() 