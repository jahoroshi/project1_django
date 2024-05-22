import os

import django
from django.db.models.functions import RowNumber

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_1.settings')
django.setup()
from cards.models import Categories
from humanize import naturaldelta
from django.db.models import Count, Case, When, Q, F, IntegerField, Window

import logging
from random import randint

from django.db.models import Q, Subquery, Case, When, F, CharField, Count
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from cards.exceptions import DeckEmptyException
from cards.models import Mappings, Cards
from django.db.models.functions import Length


# logger = logging.getLogger('cards.query_builder')
# def my_debug(subquery2):
#     queryset = subquery2.all()._clone()
#     subquery = Mappings.objects.filter(id__in=queryset).order_by('easiness', 'upd_date')
#     for el in subquery:
#         data = (
#             f'Map.ID {el.id}',
#             f'Card.ID {el.card_id}',
#             f'Repetition {el.repetition}',
#             f'Easiness {el.easiness:.4f}',
#             f'Mem_rating {el.mem_rating}',
#             f'Upd date {el.upd_date}',
#         )
#         print('\033[33;40;1m %-15s %-15s %-20s %-20s %-35s %-35s \033[0m' % data)
#
#
# # def my_debug(queryset):
# #     for obj in queryset:
# #         for el in obj.mappings_set.all():
# #             data = (
# #                 f'Map.ID {el.id}',
# #                 f'Repetition {el.repetition}',
# #                 f'Easiness {el.easiness:.4f}',
# #                 f'Mem_rating {el.mem_rating}',
# #                 f'Upd date {el.upd_date}',
# #             )
# #             print('\033[33;40;1m %-15s %-20s %-20s %-35s %-35s \033[0m' % data, '\n')
#
# def cards_counter(queryset):
#     query_rating_count = queryset.values('mem_rating').annotate(count=Count('mem_rating')).order_by('mem_rating')
#     dic = {}.fromkeys(range(1, 6), 0)
#     dic.update({el['mem_rating']: el['count'] for el in query_rating_count})
#     return dic
#
#
# def build_card_view_queryset(*args, **kwargs):
#     study_mode = 'new'
#     conditions = Q(category__slug='category-1')
#
#     if study_mode == 'new':
#         conditions &= Q(study_mode='new')
#     elif study_mode == 'review':
#         conditions &= Q(study_mode='review') & (
#                 Q(review_date__lt=timezone.now()) | Q(mem_rating__gt=0))
#
#     subquery = Mappings.objects.filter(conditions).order_by('-mem_rating').values_list('id', flat=True)[:10]
#     subquery2 = Mappings.objects.filter(id__in=subquery).order_by('upd_date').values_list('id', flat=True)[:4]
#     subquery3 = Mappings.objects.filter(id__in=subquery2).order_by('easiness', 'upd_date').values_list('card_id', flat=True)
#     queryset = Cards.objects.filter(id__in=Subquery(subquery3))
#     # print(subquery2)
#     # print(subquery3)
#
#     # ratings_count_dict = cards_counter(subquery2)
#     # cards_in_process = sum(ratings_count_dict.values())
#     cards_in_process = 10
#
#     # if not cards_in_process:
#     #     raise DeckEmptyException('/')
#
#     # max_limit = randint(1, cards_in_process + 1) if cards_in_process <= 5 else round(cards_in_process * 0.4)
#
#
#     queryset = Cards.objects.filter(id__in=Subquery(subquery3))
#     # for i in queryset:
#     #     print(i.id)
#     # # logger.debug('Queryset: %s', queryset)
#     # # for i in queryset:
#     # #     print(i.id, i.mappings__easiness, i.upd_date)
#     # # [print(i.id, i.mappings_set.values('id', 'easiness', 'upd_date')) for i in queryset]
#     # my_debug(subquery)
#     #
#     # queryset = queryset.annotate(
#     #     front_side=Case(
#     #         When(mappings__is_back_side=True, then=F('side2')),
#     #         default=F('side1'),
#     #         output_field=CharField(),
#     #     ),
#     #     back_side=Case(
#     #         When(mappings__is_back_side=True, then=F('side1')),
#     #         default=F('side2'),
#     #         output_field=CharField(),
#     #     ),
#     # ).values(
#     #     'mappings__repetition', 'front_side', 'back_side', 'id', 'mappings', 'mappings__category__name', 'mappings__easiness'
#     # )
#     return queryset
#
# def run_query_and_measure_time(query):
#     from django.db import connection
#     with connection.cursor() as cursor:
#         cursor.execute("EXPLAIN ANALYZE " + str(query.query))
#         for row in cursor.fetchall():
#             print(row)
# q = build_card_view_queryset()
# run_query_and_measure_time(q)
def get_similar_words(mappings_id, segment_length=3):

    mappings = Mappings.objects.filter(id=mappings_id).values('is_back_side', 'card__side1', 'card__side2')

    mappings = mappings[0]
    is_back_side = mappings['is_back_side']
    side_field = 'side2' if is_back_side else 'side1'
    text = mappings['card__side2'] if is_back_side else mappings['card__side1']
    len_text = len(text)

    if segment_length == 0:
        random_words = list(Cards.objects.order_by('?').values_list(side_field, flat=True)[:4])
        random_words.append(text)
        return random_words

    if segment_length == 3:
        segment = text[:0]
    else:
        segment = text[:0]

    filter_conditions = Q(**{f'{side_field}__icontains': segment})
    exclude_conditions = Q(**{side_field: segment})

    content = list(Cards.objects.annotate(text_length=Length(side_field)).filter(filter_conditions).exclude(exclude_conditions).filter(text_lenght__gte=round(len_text * 0.5), text_length__lte=round(len_text * 1.4)).values_list(side_field, flat=True).distinct()[:4])

    if len(content) < 4 and segment_length > 0:
        return get_similar_words(mappings_id, segment_length - 1)

    content.append(text)
    return content

print(get_similar_words(231))
