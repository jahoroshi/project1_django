from django.core.exceptions import PermissionDenied

from cards.models import Categories
def check_category_ownership(user, slug):
    try:
        # category = Categories.objects.get(slug=slug, user=user)
        ...
    except Categories.DoesNotExist:
        raise PermissionDenied

class CheckPermission:
    def get(self, request, *args, **kwargs):
        check_category_ownership(user=self.request.user, slug=self.kwargs.get('slug'))
        # self.object = self.get_object()
        return super().get(request, *args, **kwargs)


def check_permission_with_slug(func):
    def wrapper(*args, **kwargs):
        slug = kwargs.get('slug')
        request = args[0]
        user = request.user
        check_category_ownership(user=user, slug=slug)
        return func(*args, **kwargs)
    return wrapper