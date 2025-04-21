/**
 * Standard API response interface
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  timestamp: number;
}

/**
 * Creates a successful API response
 * @param data The data to include in the response
 * @returns A standardized successful API response
 */
export function createSuccessResponse<T>(data: T): ApiResponse<T> {
  return {
    success: true,
    data,
    timestamp: Date.now(),
  };
}

/**
 * Creates an error API response
 * @param code Error code
 * @param message Error message
 * @param details Optional error details
 * @returns A standardized error API response
 */
export function createErrorResponse(
  code: string,
  message: string,
  details?: unknown
): ApiResponse<never> {
  return {
    success: false,
    error: {
      code,
      message,
      details,
    },
    timestamp: Date.now(),
  };
}

/**
 * Type guard to check if a response is successful
 * @param response The API response to check
 * @returns Whether the response is successful
 */
export function isSuccessResponse<T>(
  response: ApiResponse<T>
): response is ApiResponse<T> & { success: true; data: T } {
  return response.success && 'data' in response;
}

/**
 * Type guard to check if a response is an error
 * @param response The API response to check
 * @returns Whether the response is an error
 */
export function isErrorResponse<T>(
  response: ApiResponse<T>
): response is ApiResponse<T> & { success: false; error: NonNullable<ApiResponse<T>['error']> } {
  return !response.success && 'error' in response;
} 