import os

import django
from django.db.models.functions import RowNumber

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_1.settings')
django.setup()
from cards.models import Categories
from humanize import naturaldelta
from django.db.models import Count, Case, When, Q, F, IntegerField, Window, Min, Sum, DateField

import logging
from random import randint

from django.db.models import Q, Subquery, Case, When, F, CharField, Count
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from cards.exceptions import DeckEmptyException
from cards.models import Mappings, Cards
from django.db.models.functions import Length
now = timezone.now()
review_date = Categories.objects.filter(slug='1').annotate(
    nearest_review_date=Min(
        'mappings__review_date',
        filter=Q(mappings__review_date__gte=now)
    )
)

# print(review_date)
# print(review_date.first().nearest_review_date)
#
# review_dat = review_date.filter(Q(mappings__review_date__lt=now))
#
# print()
# print(review_dat)
# # print(review_dat.first().nearest_review_date)
#
#
# review_date2 = Categories.objects.filter(slug='1').annotate(
#     nearest_review_date=Min(
#         'mappings__review_date',
#         filter=Q(mappings__review_date__lt=now)
#     )
# )
#
# print('ff')
# print(review_date2)
# print(review_date2.first().nearest_review_date)
# slug = '1'
# counts = Mappings.objects.filter(category__slug=slug).aggregate(
#     cards_review_count=Count(Case(
#         When(review_date__lt=now, study_mode='review', then=1),
#         output_field=IntegerField()
#     )),
#     new_cards_count=Count(Case(
#         When(study_mode='new', then=1),
#         output_field=IntegerField()
#     )),
#
# )
#
# if sum(counts.values()) != 0:
#     review_date = Mappings.objects.filter(Q(category__slug=slug) & Q(review_date__gte=now)).order_by('review_date').values_list('review_date').first()
# print(review_date)

# print(rd)

queryset = Categories.objects.filter().annotate(cards_count=Count('mappings'), reviews_count=Count(
    Case(
        When(mappings__review_date__lte=now().date(), then=1),
        output_field=IntegerField(),
    )
),
new_cards_count=Count(Case(
    When(mappings__study_mode='new', then=1),
    output_field=IntegerField()
))
                                                )


def deck_study_panel_stats(slug):
    stats_box = []
    now = timezone.now()
    counts = Mappings.objects.filter(category__slug=slug).aggregate(
        cards_review_count=Count(Case(
            When(review_date__lt=now, study_mode='review', then=1),
            output_field=IntegerField()
        )),
        new_cards_count=Count(Case(
            When(study_mode='new', then=1),
            output_field=IntegerField()
        )),

    )

    if sum(counts.values()) == 0:
        review_date = Mappings.objects.filter(Q(category__slug=slug) & Q(review_date__gte=now)).order_by(
            'review_date').values_list('review_date').first()
        next_review_date = review_date[0] if review_date else None
    else:
        next_review_date = None

    stats_box.append({
        'cards_review_count': counts['cards_review_count'],
        'new_cards_count': counts['new_cards_count'],
        'next_review_date': next_review_date,
        'current_time': now,
        'slug': slug
    })
    return ({"stats_box": stats_box})
