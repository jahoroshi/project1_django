from django import template
from cards.models import Categories, Cards, Mappings

register = template.Library()

@register.simple_tag(takes_context=True)
def boxes_of_rating(context):
    """
    Generates a list of dictionaries containing card counts by rating for a given study mode and category slug.
    :param context: Template context containing 'slug' and 'study_mode'
    :return: A dictionary with a list of rating boxes, each containing the rating number and the count of cards
    """
    boxes = []
    slug = context.get('slug')
    study_mode = context.get('study_mode')

    for rating in range(1, 5):
        card_count = Mappings.objects.filter(study_mode=study_mode, mem_rating=rating, category__slug=slug).count()
        boxes.append({
            "card_count": card_count,
            "number": rating
        })

    return {"rating_boxes": boxes}


@register.inclusion_tag("cards/box_repeat_links.html")
def box_repeat_links(slug):
    """
    Generates a list of dictionaries containing card counts by repetition for a given category slug.
    :param slug: The category slug
    :return: A dictionary with a list of repetition boxes for rendering in the 'cards/box_repeat_links.html' template
    """
    boxes = []
    for rep in range(0, 5):
        card_count = Mappings.objects.filter(repetition=rep, category__slug=slug).count()
        boxes.append({
            "repetition": rep,
            "card_count": card_count,
            "slug": slug,
        })

    return {"repetition_boxes": boxes}


@register.inclusion_tag("cards/box_categories_links.html")
def boxes_of_categories():
    """
    Generates a list of dictionaries containing card counts for each category.
    :return: A dictionary with a list of category boxes for rendering in the 'cards/box_categories_links.html' template
    """
    categories = Categories.objects.values('slug', 'name').order_by('pk')
    boxes = []
    for cat in categories:
        cat_count = Cards.objects.filter(mappings__category__slug=cat['slug']).count()
        boxes.append({
            "slug": cat['slug'],
            "name": cat['name'],
            "cat_count": cat_count
        })

    return {"categories_boxes": boxes}


@register.filter
def sum_values(dictionary):
    """
    Sums the values of a dictionary.
    :param dictionary: A dictionary with numerical values
    :return: The sum of the dictionary's values
    """
    return sum(dictionary.values())
