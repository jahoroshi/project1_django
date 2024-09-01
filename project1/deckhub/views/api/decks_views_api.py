from django.db.models import IntegerField, Min, Q, Case, When, F, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cards.models import Categories, Mappings
from cards.services.first_deck_fill import deck_filling
from deckhub.serializers import DeckSetSerializer, DeckContentSerializer
from users.models import User


@api_view(['GET'])
def reset_deck_progress(request, *args, **kwargs):
    """
    Resets the progress of all cards in a given category (deck) to their initial state.

    :param request: HTTP request object.
    :param args: Additional arguments.
    :param kwargs: Keyword arguments including 'tg_user' (Telegram user ID) and 'slug' (category slug).
    :return: HTTP response indicating the success or failure of the reset operation.
    """
    tg_id = kwargs.get('tg_user')
    slug = kwargs.get('slug')
    mappings = Mappings.objects.filter(category__slug=slug, category__user__telegram_id=tg_id)

    if not mappings.exists():
        return Response({'detail': 'Category is empty'}, status=status.HTTP_204_NO_CONTENT)

    mappings.update(
        repetition=0,
        mem_rating=0,
        easiness=0.0,
        study_mode='new',
        review_params=None,
        review_date=None
    )
    return Response(data={'detail': 'Category was reset'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def first_deck_fill(request, *args, **kwargs):
    """
    Fills a user's first deck with initial card data based on the specified language.

    :param request: HTTP request object.
    :param args: Additional arguments.
    :param kwargs: Keyword arguments including 'tg_user' (Telegram user ID) and 'language' (optional, default 'en').
    :return: HTTP response indicating the number of cards successfully added.
    """
    tg_id = kwargs.get('tg_user')
    language = kwargs.get('language', 'en')
    user = get_object_or_404(User, telegram_id=tg_id)
    success_count = deck_filling(user, language)

    if success_count > 1:
        return Response(data={'detail': f'{success_count} cards have been added.'}, status=status.HTTP_201_CREATED)
    else:
        return Response(data={'detail': 'No cards have been added.'}, status=status.HTTP_400_BAD_REQUEST)


class DeckViewSetApi(viewsets.ModelViewSet):
    """
    API viewset for managing decks (categories).
    """
    serializer_class = DeckSetSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        """
        Retrieves the queryset of categories (decks) with annotated counts for cards, reviews, and new cards.

        :return: Queryset of categories with additional annotation fields.
        """
        user = self.request.user
        if self.kwargs.get('tg_user') or self.kwargs.get('slug'):
            current_time = timezone.now()

            queryset = Categories.objects.filter().annotate(
                cards_count=Count(
                    Case(
                        When(Q(mappings__study_mode='new') | Q(mappings__study_mode='review'), then=1),
                        output_field=IntegerField()
                    )
                ),
                reviews_count=Count(
                    Case(
                        When(mappings__review_date__lte=current_time, then=1),
                        output_field=IntegerField(),
                    )
                ),
                new_cards_count=Count(
                    Case(
                        When(mappings__study_mode='new', then=1),
                        output_field=IntegerField(),
                    )
                ),
                min_review_date=Min('mappings__review_date')
            )

            return queryset
        else:
            return Categories.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Lists the categories (decks) for a given Telegram user.

        :param request: HTTP request object.
        :param args: Additional arguments.
        :param kwargs: Keyword arguments including 'tg_user' (Telegram user ID).
        :return: HTTP response with the serialized deck data or an appropriate error message.
        """
        tg_user = self.kwargs.get('tg_user')
        conditions = Q(user__telegram_id=tg_user)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        queryset = queryset.filter(conditions)
        serializer = self.get_serializer(queryset, many=True)

        if serializer.data:
            return Response(serializer.data)
        else:
            is_exist = User.objects.filter(telegram_id=tg_user).exists()
            if is_exist:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'detail': 'Decks not found. User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """
        Updates the name and slug of a category (deck).

        :param request: HTTP request object.
        :param args: Additional arguments.
        :param kwargs: Keyword arguments including the category slug.
        :return: HTTP response with the updated name and slug.
        """
        response = super().update(request, *args, **kwargs)
        return Response({'name': response.data.get('name'), 'slug': response.data.get('slug')})

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a specific category (deck) based on the slug.

        :param request: HTTP request object.
        :param args: Additional arguments.
        :param kwargs: Keyword arguments including the category slug.
        :return: HTTP response with the serialized deck data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class DeckContentViewApi(viewsets.ModelViewSet):
    """
    API viewset for retrieving the content of a specific deck (category).
    """
    serializer_class = DeckContentSerializer

    def get_queryset(self):
        """
        Retrieves the cards associated with a specific deck for a Telegram user.

        :return: Queryset of cards with annotations for side1 and side2.
        """
        tg_user = self.kwargs.get('tg_user')
        slug = self.kwargs.get('slug')

        cards = Mappings.objects.filter(
            category__user__telegram_id=tg_user,
            category__slug=slug,
        ).annotate(
            side1=F('card__side1'),
            side2=F('card__side2')
        ).values('side1', 'side2', 'card_id')

        return cards
