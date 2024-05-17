from django import template
from django.db.models import Count, Case, When, IntegerField, Min, Q
from django.utils import timezone

from cards.models import Categories, Cards, Mappings

register = template.Library()


@register.simple_tag(takes_context=True)
def boxes_of_rating(context):
    boxes = []
    slug = context.get('slug')
    study_mode = context.get('study_mode')
    # rating_scale = ('again', 'hard', 'good', 'easy')
    # rep = (rep,) if rep != 0 else (1, 2, 3, 4)
    for rating in range(1, 5):
        # card_count = Cards.objects.filter(conditions, mappings__mem_rating=rating).count()
        card_count = Mappings.objects.filter(study_mode=study_mode, mem_rating=rating, category__slug=slug).count()
        boxes.append({
            # "name": rating_scale[rating-1].capitalize(),
            "card_count": card_count,
            "number": rating
        })

    return ({"rating_boxes": boxes})


@register.inclusion_tag("cards/box_repeat_links.html")
def box_repeat_links(slug):
    boxes = []
    for rep in range(0, 5):
        card_count = Mappings.objects.filter(repetition=rep, category__slug=slug).count()
        boxes.append({
            "repetition": rep,
            "card_count": card_count,
            "slug": slug,
        })

    return ({"repetition_boxes": boxes})


@register.inclusion_tag("cards/box_categories_links.html")
def boxes_of_categories():
    categories = Categories.objects.values('slug', 'name').order_by('pk')
    boxes = []
    for cat in categories:
        cat_count = Cards.objects.filter(mappings__category__slug=cat['slug']).count()
        boxes.append({
            "slug": cat['slug'],
            "name": cat['name'],
            "cat_count": cat_count
        })

    return ({"categories_boxes": boxes})


@register.inclusion_tag('cards/deck_study_panel.html')
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


@register.filter
def sum_values(dictionary):
    return sum(dictionary.values())
