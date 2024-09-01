import csv
from pathlib import Path

from cards.models import Categories
from cards.services.handle_card_import import import_handler
from users.models import User


def deck_filling(user: User, language: str) -> int:
    """
    Creates a test deck for a user and populates it with cards from a CSV file.

    :param user: The user for whom the deck is being created.
    :param language: The language code ('en' for English, other codes for respective languages).
    :return: The number of successfully imported cards.
    """
    # Determine the deck name based on the language
    deck_name = 'First Deck for Test' if language == 'en' else 'Первая тестовая категория'

    # Create the deck (category) for the user
    deck = Categories.objects.create(name=deck_name, user=user)

    # Determine the path to the CSV file
    cur_dir = Path(__file__).parent.parent.parent.absolute()
    data_fill = cur_dir / f'static/services/deck_data_first_fill/{language}.csv'

    # Read the CSV file and prepare the text for import
    text = ''
    with open(data_fill, 'r', encoding='utf-8') as f:
        cards_data = csv.reader(f)
        for row in cards_data:
            text += ';'.join(row) + '\n'

    # Prepare the data for import_handler
    data = {
        'text': text,
        'cards_separator': 'new_line',
        'words_separator': 'semicolon',
        'words_separator_custom': '',
        'cards_separator_custom': '',
    }

    # Import the cards into the newly created deck
    slug = deck.slug
    success_count = import_handler(data, slug)

    return success_count
