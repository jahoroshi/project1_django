from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

import random

from django.db.models import Q
from django.db.models.functions import Length, Lower
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from cards.models import Cards, Mappings

class SimilarWordsAPI(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request, mappings_id, segment_length=3):
        mappings = Mappings.objects.filter(id=mappings_id).values(
            'is_back_side', 'card__side1', 'card__side2', 'category_id'
        )
        if not mappings:
            return Response({'error': 'Mappings not found'}, status=status.HTTP_404_NOT_FOUND)

        mappings = mappings[0]
        is_back_side = mappings['is_back_side']
        category_id = mappings['category_id']
        side_field = 'side1' if is_back_side else 'side2'
        text = mappings['card__side1'] if is_back_side else mappings['card__side2']
        text = text.lower()
        len_text = len(text)

        if segment_length == 3:
            segment = text[:(len(text) // 2)] if len(text) > 4 else text[:3]
        else:
            segment = text[:segment_length]

        filter_conditions = Q(**{f'{side_field}__icontains': segment}) & Q(mappings__category_id=category_id)
        exclude_conditions = Q(**{f'{side_field}__iexact': text})

        if segment_length < 0:
            random_words = list(
                Cards.objects.annotate(lower_side_field=Lower(side_field), text_length=Length(side_field)).filter(
                    text_length__gte=round(1), text_length__lte=round(len_text * 1.4)
                ).exclude(exclude_conditions).order_by('?').values_list('lower_side_field', flat=True)[:4])
            random_words.append(text)
            random.shuffle(random_words)

            data = {'back_side': text, 'similar_words': random_words}

            return Response(data, status=status.HTTP_200_OK)

        content = list(
            Cards.objects.annotate(lower_side_field=Lower(side_field), text_length=Length(side_field)).filter(
                filter_conditions).exclude(
                exclude_conditions).filter(text_length__gte=round(len_text * 0.5),
                                           text_length__lte=round(len_text * 1.4)).values_list('lower_side_field',
                                                                                               flat=True).distinct()[
            :4])

        if len(content) < 4 and segment_length >= 0:
            return self.get(request, mappings_id, segment_length - 1)

        content.append(text)
        random.shuffle(content)

        data = {'back_side': text, 'similar_words': content}
        return Response(data, status=status.HTTP_200_OK)