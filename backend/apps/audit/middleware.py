import logging

logger = logging.getLogger(__name__)


class AuditMiddleware:
    """Request logging middleware."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/api/") and request.user.is_authenticated:
            logger.debug("api_request path=%s user=%s status=%s", request.path, request.user.email, response.status_code)
        return response
