from django.core.exceptions import PermissionDenied
from cards.models import Categories

def check_category_ownership(user, slug):
    """
    Verifies that the given user owns the category specified by the slug.
    Raises a PermissionDenied exception if the category does not exist or does not belong to the user.
    """
    try:
        # category = Categories.objects.get(slug=slug, user=user)
        # Additional logic can be placed here if needed
        ...
    except Categories.DoesNotExist:
        raise PermissionDenied


class CheckPermission:
    """
    Mixin to check if the user has permission to access the category.
    """

    def get(self, request, *args, **kwargs):
        """
        Overrides the get method to include a category ownership check before proceeding.
        """
        check_category_ownership(user=self.request.user, slug=self.kwargs.get('slug'))
        # self.object = self.get_object()
        return super().get(request, *args, **kwargs)


def check_permission_with_slug(func):
    """
    Decorator to check if the user has permission to access the category specified by the slug.
    """
    def wrapper(*args, **kwargs):
        slug = kwargs.get('slug')
        request = args[0]
        user = request.user
        check_category_ownership(user=user, slug=slug)
        return func(*args, **kwargs)
    return wrapper
