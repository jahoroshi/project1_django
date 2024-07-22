from rest_framework import permissions
from cards.models import Categories


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        slug = view.kwargs.get('slug')
        try:
            category = Categories.objects.get(slug=slug)
        except Categories.DoesNotExist:
            return False

        return category.user == request.user