from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from cards.models import Cards, Mappings
from users.models import TelegramUser, User

from django.db.models import Q, Subquery, Case, When, F, CharField, Count

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import logging
from django.db import models




from cards.services.query_builder import get_card_queryset
from cardmode.permissions import IsOwner
from speech.views import synthesize_speech


class GetCardAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsOwner]
    def post(self, request, slug, *args, **kwargs):
        body_data = request.data
        rating = body_data['rating']
        mappings_id = body_data['mappings_id']
        mappings = get_object_or_404(Mappings, pk=mappings_id)
        mappings.move(rating)
        return self.get(request, slug, *args, **kwargs)

    def get(self, request, slug, *args, **kwargs):
        study_mode = kwargs.get('mode')
        card, ratings_count = get_card_queryset(slug=slug, study_mode=study_mode)
        print(ratings_count)



        data = {
            'front_side': card.get('front_side'),
            'back_side': card.get('back_side'),
            'mappings_id': card.get('id'),
            'ratings_count': ratings_count,
        }

        return Response(data, status=status.HTTP_200_OK)


class GetStartConfigAPI(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        study_mode = kwargs.get('mode')
        study_format = kwargs.get('st_format')
        slug = kwargs.get('slug')
        telegram_id = kwargs.get('telegram_id')
        if telegram_id is not None:
            if telegram_id.isdigit():
                telegram_id = int(telegram_id)
                if slug and study_mode:
                    session_config = {
                        'slug': slug,
                        'study_mode': study_mode,
                        'study_format': study_format
                    }
                    # user = User.objects.get(telegram_id=telegram_id)
                    # user.session_config = session_config
                    user, created = User.objects.update_or_create(
                        telegram_id=telegram_id,
                        defaults={'session_config': session_config}
                    )

                else:
                    telegram_user = User.objects.get(telegram_id=telegram_id)
                    config = telegram_user.session_config
                    if config:
                        slug = config.get('slug')
                        study_mode = config.get('study_mode')
                        study_format = config.get('study_format')

            else:
                return Response({"detail": "telegram_id must be a digit"}, status=status.HTTP_400_BAD_REQUEST)



        buttons_to_show = {
            'show_back': True,
            'show_hint': True,
            'show_similar': True,
            'show_first_letters': True,
            'scramble_letters': True,
            'speech': True
        }

        start_config = {
            'csrf_token': request.COOKIES.get('csrftoken'),
            'slug': slug,
            'study_mode': study_mode,
            'study_format': study_format,
            'urls': {
                'get_card': reverse('get_card', kwargs={'slug': slug, 'mode': study_mode}),
                'get_hint': reverse('get_hint', kwargs={'mappings_id': 'dummy_mappings_id'}),
                'get_similar_words': reverse('get_similar_words', kwargs={'mappings_id': 'dummy_mappings_id'}),
                'get_sound': reverse('get_sound', kwargs={'mappings_id': 'dummy_mappings_id'})
            },
            'buttons_to_show': buttons_to_show
        }
        return Response(start_config, status=status.HTTP_200_OK)


class GetSoundAPI(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, mappings_id, *args, **kwargs):
        card = Mappings.objects.annotate(
            front_side=Case(
                When(is_back_side=True, then=F('card__side2')),
                default=F('card__side1'),
                output_field=CharField()
            ),
            audio=Case(
                When(is_back_side=True, then=F('card__audio_side2')),
                default=F('card__audio_side1'),
                output_field=CharField()
            )
        ).values(
            'front_side', 'audio', 'card_id', 'is_back_side'
        ).get(pk=mappings_id)

        is_back_side = card.get('is_back_side')
        sound_file_path = card.get('audio')

        if sound_file_path is None:
            text = card.get('front_side')
            card_id = card.get('card_id')
            sound_file_path = synthesize_speech(text=text, card_id=f"{card_id}_side_{(1,2)[is_back_side]}")
            if not is_back_side:
                Cards.objects.filter(id=card_id).update(audio_side1=sound_file_path)
            else:
                Cards.objects.filter(id=card_id).update(audio_side2=sound_file_path)


        try:
            with open(sound_file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type="audio/mpeg")
                response['Content-Disposition'] = 'inline; filename=sound_file.mp3'
                response.status = status.HTTP_200_OK
                return response
        except FileNotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetHintAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        mappings_id = int(kwargs.get('mappings_id'))
        print(mappings_id)
        card = Mappings.objects.filter(id=mappings_id).values_list('card__side1').first()
        print(card)
        return Response(card, status=status.HTTP_200_OK)