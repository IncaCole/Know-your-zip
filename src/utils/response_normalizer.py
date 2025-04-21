from typing import Any, Dict, Optional, Union
from fastapi import status

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