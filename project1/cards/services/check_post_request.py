from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.views import View

class CheckReuqest(View):
    """
    View mixin to prevent duplicate form submissions.
    It checks if the CSRF token has already been processed and, if so, prevents re-processing.
    """

    def post(self, request, *args, **kwargs):
        """
        Overrides the post method to check for duplicate submissions.
        If the CSRF token is found in the cache, it redirects to the same page.
        Otherwise, it processes the request as usual.
        """
        self.object = None
        token = request.POST.get('csrfmiddlewaretoken')

        if cache.get(token):
            return HttpResponseRedirect(self.request.path)

        cache.set(token, 'processed', timeout=50)  # Store the token in the cache for 50 seconds
        return super().post(request, *args, **kwargs)


def is_post_unique(request):
    """
    Utility function to check if a POST request is unique based on the CSRF token.
    :param request: The incoming HTTP request.
    :return: True if the request is unique, False if it's a duplicate submission.
    """
    token = request.POST.get('csrfmiddlewaretoken')

    if not cache.get(token):
        cache.set(token, 'processed', timeout=50)  # Store the token in the cache for 50 seconds
        return True

    return False
