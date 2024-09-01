import logging
from django.shortcuts import redirect
from .exceptions import DeckEmptyException

logger = logging.getLogger(__name__)

class DeckEmptyMiddleware:
    """
    Middleware to catch DeckEmptyException and redirect the user to the specified URL.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the request and catch DeckEmptyException to handle redirection.
        """
        logger.debug('DeckEmptyMiddleware: processing request')
        try:
            response = self.get_response(request)
            return response
        except DeckEmptyException as e:
            logger.warning(f'DeckEmptyException caught in __call__: Redirecting to {e.redirect_url}')
            return redirect(e.redirect_url)

    def process_exception(self, request, exception):
        """
        Handle exceptions of type DeckEmptyException.
        If such an exception is caught, redirect to the provided URL.
        """
        if isinstance(exception, DeckEmptyException):
            logger.warning(f'DeckEmptyException caught in process_exception: Redirecting to {exception.redirect_url}')
            return redirect(exception.redirect_url)
        return None
