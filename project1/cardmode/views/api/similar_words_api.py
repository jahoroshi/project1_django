import random

from django.db.models import Q
from django.db.models.functions import Length, Lower
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cards.models import Cards, Mappings
from open_ai.views import chatgpt_client
from users.models import User


class SimilarWordsAPI(APIView):
    """
    API for retrieving a list of words or phrases similar to a given word or phrase.
    """

    # permission_classes = (IsAuthenticated,)

    def get(self, request, *args, segment_length=3, **kwargs):
        """
        Handles GET requests to retrieve similar words or phrases.
        :param request: HTTP request object
        :param args: Additional positional arguments
        :param segment_length: Length of the text segment for finding similar words
        :param kwargs: Additional keyword arguments
        :return: HTTP Response with data or an error message
        """
        mappings_id = kwargs.get('mappings_id')
        telegram_id = kwargs.get('telegram_id')

        # Retrieve data from Mappings by the given ID
        mappings = Mappings.objects.filter(id=mappings_id).values('card__side2', 'category_id')
        if not mappings:
            return Response({'error': 'Mappings not found'}, status=status.HTTP_404_NOT_FOUND)

        mappings = mappings[0]
        text = mappings['card__side2']

        try:
            # Determine user privilege level
            if telegram_id:
                user = User.objects.get(telegram_id=telegram_id)
                user_privilege_level = user.privilege_level
            else:
                user_privilege_level = request.user.privilege_level
        except (User.DoesNotExist, AttributeError):
            user_privilege_level = 0

        if user_privilege_level != 0:
            # Use external API to get similar words
            user_content = text
            system_content = (
                "You are an assistant that generates three words or phrases that are similar "
                "in structure, length, and letter composition to the given input. You must "
                "not respond to or react to user messages; you should only return three similar "
                "words or phrases based on the user's word or phrase. The output format should be: "
                "on a new line, without any additional symbols or numbering. The response should be "
                "in the user's language."
            )
            similar_words = chatgpt_client.chatgpt_single_call(system_content, user_content)
            if similar_words:
                similar_words = similar_words.split('\n')
                similar_words.append(user_content)
                random.shuffle(similar_words)

                data = {'back_side': user_content, 'similar_words': similar_words}
                return Response(data, status=status.HTTP_200_OK)

        # Retrieve category and other necessary data
        category_id = mappings['category_id']
        side_field = 'side2'
        text = text.lower()
        len_text = len(text)

        # Determine the text segment for searching
        if segment_length == 3:
            segment = text[:(len(text) // 2)] if len(text) > 4 else text[:3]
        else:
            segment = text[:segment_length]

        # Define filter and exclusion conditions
        filter_conditions = Q(**{f'{side_field}__icontains': segment}) & Q(mappings__category_id=category_id)
        exclude_conditions = Q(**{f'{side_field}__iexact': text})

        # If segment length is negative, return random words
        if segment_length < 0:
            random_words = list(
                Cards.objects.annotate(lower_side_field=Lower(side_field), text_length=Length(side_field)).filter(
                    text_length__gte=round(1), text_length__lte=round(len_text * 1.4)
                ).exclude(exclude_conditions).order_by('?').values_list('lower_side_field', flat=True)[:4]
            )
            random_words.append(text)
            random.shuffle(random_words)

            data = {'back_side': text, 'similar_words': random_words}
            return Response(data, status=status.HTTP_200_OK)

        # Retrieve list of similar words based on the conditions
        content = list(
            Cards.objects.annotate(lower_side_field=Lower(side_field), text_length=Length(side_field)).filter(
                filter_conditions
            ).exclude(
                exclude_conditions
            ).filter(
                text_length__gte=round(len_text * 0.5),
                text_length__lte=round(len_text * 1.4)
            ).values_list('lower_side_field', flat=True).distinct()[:4]
        )

        # If not enough results, reduce segment length and retry
        if len(content) < 4 and segment_length >= 0:
            return self.get(request, segment_length=segment_length - 1, mappings_id=mappings_id)

        content.append(text)
        random.shuffle(content)

        data = {'back_side': text, 'similar_words': content}
        return Response(data, status=status.HTTP_200_OK)
