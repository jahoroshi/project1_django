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
            When(review_date__lt=now, review_date__isnull=False, then=1),
            output_field=IntegerField()
        )),
        new_cards_count=Count(Case(
            When(review_date__isnull=True, then=1),
            output_field=IntegerField()
        )),

    )

    review_date = Categories.objects.filter(slug=slug).annotate(
        nearest_review_date=Min(
            'mappings__review_date',
            filter=Q(mappings__review_date__gte=now)
        )
    ).filter(
        ~Q(mappings__review_date__lt=now)
    )
    next_review_date = review_date.first().nearest_review_date if review_date.exists() else None
    stats_box.append({
        'cards_review_count': counts['cards_review_count'],
        'new_cards_count': counts['new_cards_count'],
        'next_review_date': next_review_date,
        'current_time': now,
        'slug': slug
    })
    return ({"stats_box": stats_box})