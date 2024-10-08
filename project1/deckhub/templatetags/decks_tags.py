from django import template
from django.db.models import Count, Case, When, IntegerField, Min, Q
from django.utils import timezone

from cards.models import Categories, Cards, Mappings

register = template.Library()

@register.inclusion_tag('deckhub/deck_study_panel.html')
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