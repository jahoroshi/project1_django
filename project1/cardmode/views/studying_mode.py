import json
import random

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from cards.models import Cards, Mappings
from cards.services.query_builder import build_card_view_queryset
from speech.views import synthesize_speech


# logger = logging.getLogger('cards.views')
def get_card(request, *args, **kwargs):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        rating = body_data['rating']
        mappings_id = body_data['mappings_id']
        mappings = get_object_or_404(Mappings, pk=mappings_id)
        mappings.move(rating)
    slug = kwargs['slug']
    study_mode = request.GET.get('study_mode')
    card, ratings_count = build_card_view_queryset(slug=slug, study_mode=study_mode)

    data = {
        'front_side': card.get('front_side'),
        'back_side': card.get('back_side'),
        'mappings_id': card.get('id')
    }

    return JsonResponse(data)


def get_hint(request, card_id):
    card = get_object_or_404(Cards, id=card_id)
    return JsonResponse({'hint': card.hint})


def submit_answer(request, card_id):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        rating = body_data['rating']
        print(rating)
        new_card = random.choice(Cards.objects.all())
        return JsonResponse({'new_card_id': new_card.id, 'front_side': new_card.front_side})


def study_view(request, *args, **kwargs):
    study_mode = request.GET.get('study_mode')
    slug = kwargs.get('slug')
    buttons_to_show = {
        'show_back': True,
        'show_hint': True,
        'show_similar': True,
        'show_first_letters': True,
        'scramble_letters': True,
        'speech': True
    }
    context = {
        'csrf_token': request.COOKIES.get('csrftoken'),
        'slug': slug,
        'study_mode': study_mode,
        'buttons_to_show': buttons_to_show,
    }
    return render(request, 'cardmode/studying_mode.html', context)


def get_sound(request, mappings_id):
    mappings = Mappings.objects.filter(pk=mappings_id).values(
        'card__side1', 'card__audio', 'card_id'
    )
    card = tuple(mappings)
    sound_file_path = card[0].get('card__audio')

    if sound_file_path is None:
        text = card[0].get('card__side1')
        card_id = card[0].get('card_id')
        sound_file_path = synthesize_speech(text=text, card_id=card_id)
        Cards.objects.filter(id=card_id).update(audio=sound_file_path)

    with open(sound_file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type="audio/mpeg")
        response['Content-Disposition'] = 'inline; filename= sound_file.mp3'
        return response
