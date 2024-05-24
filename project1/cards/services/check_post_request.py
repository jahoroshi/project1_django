from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.views import View


class CheckReuqest(View):
    def post(self, request, *args, **kwargs):
        self.object = None
        token = request.POST.get('csrfmiddlewaretoken')
        if cache.get(token):
            print('double')
            return HttpResponseRedirect(self.request.path)
        cache.set(token, 'processed', timeout=50)

        return super().post(request, *args, **kwargs)

def is_post_unique(request):
    token = request.POST.get('csrfmiddlewaretoken')
    if not cache.get(token):
        cache.set(token, 'processed', timeout=50)
        return True
    print('DOOOOUBLE!!')
    return False