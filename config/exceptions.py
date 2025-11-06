from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler that wraps DRF exceptions in a consistent format.
    Does not expose internal error messages in production.
    """
    from django.conf import settings

    response = exception_handler(exc, context)

    if response is not None:
        # Don't expose internal error messages in production
        if settings.DEBUG:
            message = str(exc)
        else:
            # Generic messages for production
            if response.status_code == 400:
                message = "Bad request. Please check your input."
            elif response.status_code == 401:
                message = "Authentication required."
            elif response.status_code == 403:
                message = "You do not have permission to perform this action."
            elif response.status_code == 404:
                message = "Resource not found."
            elif response.status_code == 500:
                message = "An internal server error occurred."
            else:
                message = "An error occurred."

        custom_response_data = {
            "error": True,
            "message": message,
            "status_code": response.status_code,
            "details": response.data,
        }
        response.data = custom_response_data

    return response
