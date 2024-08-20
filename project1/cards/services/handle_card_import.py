from django.shortcuts import get_object_or_404

from cards.models import Categories, Cards, Mappings


# from cards.permissions import check_permission_with_slug



def import_handler(data, slug):
    category = get_object_or_404(Categories, slug=slug)
    text = data['text']

    words_separator = data['words_separator']
    cards_separator = data['cards_separator']
    words_separator_custom = data['words_separator_custom']
    cards_separator_custom = data['cards_separator_custom']

    separators = {
        'tab': '\t',
        'comma': ',',
        'words_custom': words_separator_custom,
        'new_line': '\n',
        'semicolon': ';',
        'cards_custom': cards_separator_custom
    }

    if '\r\n' in text:
        separators['new_line'] = '\r\n'

    words_sep = separators[words_separator]
    cards_sep = separators[cards_separator]
    cards = text.split(cards_sep)
    success_count = 0

    for card in cards:
        try:
            front_side, back_side = card.split(words_sep)
            object_card = Cards.objects.create(side1=front_side.strip()[:256], side2=back_side.strip()[:256])
            Mappings.objects.create(card=object_card, category=category)
            success_count += 1
        except ValueError:
            continue

    return success_count


