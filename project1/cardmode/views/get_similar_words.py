import random

from django.db.models import Q
from django.db.models.functions import Length, Lower
from django.http import JsonResponse

from cards.models import Cards, Mappings


def get_similar_words(request, mappings_id, segment_length=3):
    """
    Retrieves a list of words or phrases similar to the word or phrase on the card's 'side2'.

    :param mappings_id: ID of the Mappings object
    :param segment_length: Length of the text segment used for finding similar words
    :return: JsonResponse with the original text and a list of similar words
    """

    # Fetch the relevant mapping object by its ID
    mappings = Mappings.objects.filter(id=mappings_id).values('card__side2', 'category_id')

    mappings = mappings[0]
    category_id = mappings['category_id']
    side_field = 'side2'
    text = mappings['card__side2'].lower()
    len_text = len(text)

    # Determine the segment of the text to use for searching similar words
    if segment_length == 3:
        segment = text[:(len(text) // 2)] if len(text) > 4 else text[:3]
    else:
        segment = text[:segment_length]

    # Define conditions for filtering and excluding certain results
    filter_conditions = Q(**{f'{side_field}__icontains': segment}) & Q(mappings__category_id=category_id)
    exclude_conditions = Q(**{f'{side_field}__iexact': text})

    if segment_length < 0:
        # Return random words if the segment length is negative
        random_words = list(
            Cards.objects.annotate(lower_side_field=Lower(side_field), text_length=Length(side_field))
            .filter(text_length__gte=round(len_text * 0.5), text_length__lte=round(len_text * 1.4))
            .exclude(exclude_conditions)
            .order_by('?')
            .values_list('lower_side_field', flat=True)[:4]
        )
        random_words.append(text)
        random.shuffle(random_words)
        return JsonResponse({'back_side': text, 'similar_words': random_words})

    # Fetch similar words based on the defined segment and conditions
    content = list(
        Cards.objects.annotate(lower_side_field=Lower(side_field), text_length=Length(side_field))
        .filter(filter_conditions)
        .exclude(exclude_conditions)
        .filter(text_length__gte=round(len_text * 0.5), text_length__lte=round(len_text * 1.4))
        .values_list('lower_side_field', flat=True)
        .distinct()[:4]
    )

    # If not enough similar words are found, reduce the segment length and retry
    if len(content) < 4 and segment_length >= 0:
        return get_similar_words(request, mappings_id, segment_length - 1)

    content.append(text)
    random.shuffle(content)

    return JsonResponse({'back_side': text, 'similar_words': content})
