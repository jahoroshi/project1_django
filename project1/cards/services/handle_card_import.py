from django.shortcuts import get_object_or_404
from cards.models import Categories, Cards, Mappings


def import_handler(data, slug):
    """
    Handles the import of card data into a specified category.

    :param data: A dictionary containing the card data and separators.
    :param slug: The slug of the category where the cards will be imported.
    :return: The number of successfully imported cards.
    """
    # Retrieve the category using the slug, or raise a 404 error if not found
    category = get_object_or_404(Categories, slug=slug)
    text = data['text']

    # Retrieve the separators from the input data
    words_separator = data['words_separator']
    cards_separator = data['cards_separator']
    words_separator_custom = data['words_separator_custom']
    cards_separator_custom = data['cards_separator_custom']

    # Define the mapping of separators
    separators = {
        'tab': '\t',
        'comma': ',',
        'words_custom': words_separator_custom,
        'new_line': '\n',
        'semicolon': ';',
        'cards_custom': cards_separator_custom,
    }

    # Adjust for Windows-style newlines
    if '\r\n' in text:
        separators['new_line'] = '\r\n'

    # Get the actual separators to be used
    words_sep = separators[words_separator]
    cards_sep = separators[cards_separator]
    cards = text.split(cards_sep)
    success_count = 0

    # Iterate over the card data and create card and mapping objects
    for card in cards:
        try:
            front_side, back_side = card.split(words_sep)
            object_card = Cards.objects.create(
                side1=front_side.strip()[:254],  # Truncate to fit the database field limit
                side2=back_side.strip()[:254]
            )
            Mappings.objects.create(card=object_card, category=category)
            success_count += 1
        except ValueError:
            continue  # Skip cards that don't have the correct format

    return success_count
