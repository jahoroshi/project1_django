import logging
from random import randint

from django.db.models import Q, Subquery, Case, When, F, CharField, Count
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from cards.exceptions import DeckEmptyException
from cards.models import Mappings, Cards
from django.core.cache import cache

# logger = logging.getLogger('cards.query_builder')
def my_debug(subquery, map_id):
    queryset = Mappings.objects.filter(id__in=Subquery(subquery)).order_by('easiness')
    for el in queryset:
        data = (
            f'Map.ID {el.id}',
            f'Card.ID {el.card_id}',
            f'Repetition {el.repetition}',
            f'Easiness {el.easiness:.4f}',
            f'Mem_rating {el.mem_rating}',
            f'Upd date {el.upd_date}',
        )
        if el.id != map_id:
            print('\033[33;40;1m %-15s %-15s %-20s %-20s %-35s %-35s \033[0m' % data)
        else:
            print('\033[13;26;1m %-15s %-15s %-20s %-20s %-35s %-35s \033[0m' % data)


def cards_counter(queryset):
    query_rating_count = Mappings.objects.filter(id__in=(Subquery(queryset))).values('mem_rating').annotate(count=Count('mem_rating')).order_by('mem_rating')
    dic = {}.fromkeys(range(1, 5), 0)
    dic.update({el['mem_rating']: el['count'] for el in query_rating_count})
    return dic


def get_card_queryset(*args, **kwargs):
    study_mode = kwargs['study_mode']
    if study_mode.endswith('all'):
        study_mode, tg_id, _ = study_mode.split('-')
        conditions = Q(category__user__telegram_id=tg_id)
    else:
        conditions = Q(category__slug=kwargs['slug'])

    if study_mode == 'new':
        conditions &= Q(study_mode='new')
    elif study_mode == 'review':
        conditions &= Q(study_mode='review') & (
                Q(review_date__lt=timezone.now()) | Q(mem_rating__gt=0))

    subquery1 = Mappings.objects.filter(conditions).order_by('-mem_rating').values('id')[:10]

    ratings_count_dict = cards_counter(subquery1)
    cards_in_process = sum(ratings_count_dict.values())
    max_limit = randint(1, cards_in_process + 1) if cards_in_process <= 5 else round(cards_in_process * 0.4)

    subquery2 = Mappings.objects.filter(id__in=Subquery(subquery1)).order_by('upd_date').values('id')[:max_limit]
    # subquery3 = Mappings.objects.filter(id__in=Subquery(subquery2)).order_by('easiness', 'upd_date').values('card_id')

    card = (
            Mappings.objects.filter(id__in=Subquery(subquery2))
            .order_by('easiness', 'upd_date')
            .annotate(
                front_side=F('card__side1'),
                back_side=F('card__side2')
            )
            .values(
                'review_date', 'front_side', 'back_side',
                'card__id', 'id', 'category__name', 'easiness'
            )
            .first() or {}
    )


    ####
    my_debug(subquery1, card.get('id'))
    ####
    if not card.get('easiness') and study_mode == 'new':
        ratings_count_dict[5] = 1
    ratings_count_dict.pop(0, None)

    return card, ratings_count_dict


