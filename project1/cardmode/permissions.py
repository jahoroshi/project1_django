from rest_framework import permissions
from cards.models import Categories


class IsOwner(permissions.BasePermission):
    """
    Custom permission to allow access only to the owner of a category.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the category based on ownership.
        :param view: The view object
        :return: True if the user is the owner, False otherwise
        """
        slug = view.kwargs.get('slug')

        try:
            category = Categories.objects.get(slug=slug)
        except Categories.DoesNotExist:
            return False

        # Check if the logged-in user is the owner of the category
        return category.user == request.user
