import csv
from pathlib import Path

from cards.models import Categories
from cards.services.handle_card_import import import_handler
from users.models import User


def deck_filling(user: User, language):
    deck_name = 'First Deck for Test' if language == 'en' else 'Первая тестовая категория'
    deck = Categories.objects.create(name=deck_name, user=user)

    cur_dir = Path(__file__).parent.parent.parent.absolute()
    data_fill = f'{cur_dir}/static/services/deck_data_first_fill/{language}.csv'
    text = ''
    with open(data_fill, 'r', encoding='utf-8') as f:
        cards_data = csv.reader(f)
        for row in cards_data:
            text += ';'.join(row) + '\n'

    data = {
        'text': text,
        'cards_separator': 'new_line',
        'words_separator': 'semicolon',
        'words_separator_custom': '',
        'cards_separator_custom': '',

    }
    slug = deck.slug
    success_count = import_handler(data, slug)
    return success_count