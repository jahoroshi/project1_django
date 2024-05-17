from random import randint

from django.db.models import Q, Subquery, Case, When, F, CharField, Count
from django.utils import timezone

from cards.models import Mappings, Cards


def my_debug(subquery2):
    queryset = subquery2.all()._clone()
    subquery2 = queryset.order_by('easiness')
    for el in subquery2:
        data = (
            f'Map.ID {el.id}',
            f'Card.ID {el.card_id}',
            f'Repetition {el.repetition}',
            f'Easiness {el.easiness:.4f}',
            f'Mem_rating {el.mem_rating}',
            f'Upd date {el.upd_date}',
        )
        print('\033[33;40;1m %-15s %-15s %-20s %-20s %-35s %-35s \033[0m' % data)


# def my_debug(queryset):
#     for obj in queryset:
#         for el in obj.mappings_set.all():
#             data = (
#                 f'Map.ID {el.id}',
#                 f'Repetition {el.repetition}',
#                 f'Easiness {el.easiness:.4f}',
#                 f'Mem_rating {el.mem_rating}',
#                 f'Upd date {el.upd_date}',
#             )
#             print('\033[33;40;1m %-15s %-20s %-20s %-35s %-35s \033[0m' % data, '\n')

def cards_counter(queryset):
    query_rating_count = queryset.values('mem_rating').annotate(count=Count('mem_rating')).order_by('mem_rating')
    dic = {}.fromkeys(range(1, 6), 0)
    dic.update({el['mem_rating']: el['count'] for el in query_rating_count})
    return dic


def build_card_view_queryset(*args, **kwargs):
    study_mode = kwargs['study_mode']
    conditions = Q(category__slug=kwargs['slug'])

    if study_mode == 'new':
        conditions &= Q(study_mode='new')
    elif study_mode == 'review':
        conditions &= Q(study_mode='review') & (
                Q(review_date__lt=timezone.now()) | Q(mem_rating__gt=0))

    subquery = Mappings.objects.filter(conditions).order_by('-mem_rating').values_list('id', flat=True)[:10]
    subquery2 = Mappings.objects.filter(id__in=subquery).order_by('upd_date')

    ratings_count_dict = cards_counter(subquery2)
    cards_in_process = sum(ratings_count_dict.values())

    if not cards_in_process:
        return
    max_limit = randint(1, cards_in_process + 1) if cards_in_process <= 5 else round(cards_in_process * 0.4)

    queryset = Cards.objects.filter(
        id__in=Subquery(subquery2[:max_limit].values_list('card_id', flat=True))).order_by('mappings__easiness',
                                                                                           'mappings__upd_date')
    [print(i.id, i.mappings_set.values('id', 'easiness', 'upd_date')) for i in queryset]
    my_debug(subquery2)

    queryset = queryset.annotate(
        front_side=Case(
            When(mappings__is_back_side=True, then=F('side2')),
            default=F('side1'),
            output_field=CharField(),
        ),
        back_side=Case(
            When(mappings__is_back_side=True, then=F('side1')),
            default=F('side2'),
            output_field=CharField(),
        ),
    ).values(
        'mappings__repetition', 'front_side', 'back_side', 'id', 'mappings', 'mappings__category__name', 'mappings__easiness'
    )
    return queryset, ratings_count_dict

# def build_card_view_queryset(*args, **kwargs):
#     study_mode = kwargs['study_mode']
#     conditions = Q(mappings__category__slug=kwargs['slug'])
#
#     if study_mode == 'new':
#         conditions &= Q(mappings__study_mode='new')
#         subquery = Cards.objects.filter(conditions).order_by('-mappings__mem_rating').values('mappings__id')[:10]
#         print(subquery)
#         queryset = Cards.objects.filter(mappings__id__in=Subquery(subquery)).order_by('mappings__easiness', 'mappings__upd_date')
#         my_debug(queryset)
#     elif study_mode == 'review':
#         conditions &= Q(mappings__study_mode='review') & (Q(mappings__review_date__lt=timezone.now()) | Q(mappings__mem_rating__gt=0))
#
#         subquery = Cards.objects.filter(conditions).order_by('-mappings__mem_rating', '-mappings__review_date').values('mappings__id')[:10]
#         queryset = Cards.objects.filter(mappings__id__in=Subquery(subquery)).order_by('mappings__mem_rating', 'mappings__review_date')
#         my_debug(queryset)
#
#     queryset = queryset.annotate(
#             front_side=Case(
#                 When(mappings__is_back_side=True, then=F('side2')),
#                 default=F('side1'),
#                 output_field=CharField(),
#             ),
#             back_side=Case(
#                 When(mappings__is_back_side=True, then=F('side1')),
#                 default=F('side2'),
#                 output_field=CharField(),
#             ),
#         ).values(
#             'mappings__repetition', 'front_side', 'back_side', 'id', 'mappings', 'mappings__category__name'
#         )
#     return queryset
#
#
