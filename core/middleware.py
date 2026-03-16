"""
Custom middleware for the MarketLink API.
"""
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPI(MiddlewareMixin):
    """
    Middleware to disable CSRF validation for API endpoints.
    
    Since the API uses JWT authentication (which is inherently CSRF-safe),
    we exempt all /api/ paths from CSRF validation.
    """
    
    def process_request(self, request):
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
