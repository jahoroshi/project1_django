import csv
from pathlib import Path

from django.db.models import Count, Case, When, IntegerField, Q, Min
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cards.models import Categories
from cards.models import Mappings
from deckhub.serializers import DeckSetSerializer, DeckContentSerializer
from cards.services.handle_card_import import import_handler
from users.models import User


@api_view(['GET'])
def first_deck_fill(request, *args, **kwargs):
    tg_id = kwargs.get('telegram_id')
    language = kwargs.get('language')
    deck_name = 'First Deck for Test' if language == 'en' else 'Первая тестовая категория'
    user = User.objects.get(telegram_id=tg_id)
    deck = Categories.objects.create(name=deck_name, user=user)

    cur_dir = Path(__file__).parent.parent.parent.parent.absolute()
    data_fill = f'{cur_dir}/static/services/deck_data_first_fill/{language}.csv'
    text = ''
    with open(data_fill, 'r', encoding='utf-8') as f:
        cards_data = csv.reader(f)
        for row in cards_data:
            text += ';'.join(row) + '\n'

    data = {
        'text': text,
        'cards_separator': 'new_line',
        'words_separator': 'semicolon',
        'words_separator_custom': '',
        'cards_separator_custom': '',

    }
    slug = deck.slug
    success_count = import_handler(data, slug)
    if success_count > 1:
        return Response(data={'detail': f'Have been added: {success_count}'}, status=status.HTTP_201_CREATED)
    else:
        return Response(data={'detail': f'Cards have not been added.'}, status=status.HTTP_400_BAD_REQUEST)





class DeckViewSetApi(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    serializer_class = DeckSetSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user
        if self.kwargs.get('tg_user') or self.kwargs.get('slug'):
            current_time = timezone.now()

            queryset = Categories.objects.filter().annotate(cards_count=Count('mappings'),
                                                            reviews_count=Count(
                                                                Case(
                                                                    When(mappings__review_date__lte=current_time,
                                                                         then=1),
                                                                    output_field=IntegerField(),
                                                                )),
                                                            new_cards_count=Count(Case(
                                                                When(mappings__study_mode='new', then=1),
                                                                output_field=IntegerField()
                                                            )),
                                                            min_review_date=Min('mappings__review_date'))
            return queryset
        else:
            return Categories.objects.none()

    def list(self, request, *args, **kwargs):
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
                return Response({'detail': 'Decks Not found. User Not exist.'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({'name': response.data.get('name'), 'slug': response.data.get('slug')})


class DeckContentViewApi(viewsets.ModelViewSet):
    serializer_class = DeckContentSerializer

    def get_queryset(self):
        tg_user = self.kwargs.get('tg_user')
        slug = self.kwargs.get('slug')

        mappings = Mappings.objects.filter(
            category__user__telegram_id=tg_user,
            category__slug=slug, is_back_side=False
        ).select_related('card').only('card__side1', 'card__side2')
        cards = [mapping.card for mapping in mappings]

        return cards
