from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        host = request.get_host() or request.META.get('HTTP_ORIGIN')
        if host in settings.ALLOWED_HOSTS:
            return None, None

        api_key = request.headers.get('X-API-Key')

        if not api_key:
            api_key = request.query_params.get('api_key')

        if not api_key:
            raise AuthenticationFailed('API key required')

        if api_key != settings.BOT_API_KEY:
            raise AuthenticationFailed('Invalid API key')

        return None, None