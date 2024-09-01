from rest_framework import viewsets, status
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSetSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions for User model, with additional
    logic for handling users identified by their Telegram ID.
    """
    queryset = User.objects.all()
    serializer_class = UserSetSerializer
    lookup_field = 'telegram_id'
    tg_user_is_created = False

    def retrieve(self, request, *args, **kwargs):
        """
        Handles the retrieval of a User object. Returns a 201 status if the user was newly created.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        if self.tg_user_is_created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data)

    def get_object(self):
        """
        Overrides the get_object method to include custom logic for getting or creating
        a User object based on the Telegram ID. Also updates the username if provided.
        """
        self.tg_user_is_created = False
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        telegram_username = self.request.query_params.get('username')
        obj, self.tg_user_is_created = queryset.get_or_create(telegram_id=self.kwargs[lookup_url_kwarg])

        if telegram_username and obj.username != telegram_username:
            obj.username = telegram_username
            obj.save()

        self.check_object_permissions(self.request, obj)

        return obj
