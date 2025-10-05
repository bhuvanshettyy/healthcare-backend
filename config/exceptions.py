from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.exceptions import ValidationError, PermissionDenied
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': 'An error occurred',
                'details': []
            }
        }
        
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['error']['message'] = response.data['detail']
            else:
                custom_response_data['error']['details'] = response.data
        elif isinstance(response.data, list):
            custom_response_data['error']['details'] = response.data
        else:
            custom_response_data['error']['message'] = str(response.data)
        
        # Set specific error messages based on exception type
        if isinstance(exc, Http404):
            custom_response_data['error']['message'] = 'Resource not found'
        elif isinstance(exc, PermissionDenied):
            custom_response_data['error']['message'] = 'Permission denied'
        elif isinstance(exc, ValidationError):
            custom_response_data['error']['message'] = 'Validation error'
            
        response.data = custom_response_data
        
        # Log the error for debugging
        logger.error(f"API Error: {exc}", exc_info=True)
    
    return response


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    response_data = {
        'success': True,
        'message': message,
        'data': data
    }
    return Response(response_data, status=status_code)