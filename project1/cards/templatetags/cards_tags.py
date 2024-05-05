
from django import template

from cards.models import Categories, Cards, Mappings

register = template.Library()

@register.inclusion_tag("cards/mem_rating_in_card.html")
def boxes_of_rating(rep, slug):
    boxes = []
    rating_scale = ('again', 'hard', 'good', 'easy')
    rep = (rep,) if rep != 0 else (1, 2, 3, 4)
    for rating in range(1, 5):
        card_count = Mappings.objects.filter(repetition__in=rep, mem_rating=rating, category__slug=slug).count()
        boxes.append({
            "name": rating_scale[rating-1].capitalize(),
            "card_count": card_count,
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



