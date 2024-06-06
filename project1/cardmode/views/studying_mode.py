import random
import json
from django.urls import reverse
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from cards.models import Cards, Mappings
from cards.services.query_builder import build_card_view_queryset
from speech.views import synthesize_speech
from cards.services.check_permission import check_permission_with_slug
from django.contrib.auth.decorators import login_required



@login_required
@check_permission_with_slug
def get_card(request, *args, **kwargs):
    slug = kwargs['slug']

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        rating = body_data['rating']
        mappings_id = body_data['mappings_id']
        mappings = get_object_or_404(Mappings, pk=mappings_id)
        mappings.move(rating)
    study_mode = request.GET.get('mode')
    card, ratings_count = build_card_view_queryset(slug=slug, study_mode=study_mode)
    print(ratings_count)

    data = {
        'front_side': card.get('front_side'),
        'back_side': card.get('back_side'),
        'mappings_id': card.get('id'),
        'ratings_count': ratings_count,
    }

    return JsonResponse(data)

@login_required
def get_hint(request, card_id):
    card = get_object_or_404(Cards, id=card_id)
    return JsonResponse({'hint': card.hint})

@login_required
def submit_answer(request, card_id):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        rating = body_data['rating']
        print(rating)
        new_card = random.choice(Cards.objects.all())
        return JsonResponse({'new_card_id': new_card.id, 'front_side': new_card.front_side})



@login_required
@check_permission_with_slug
def study_view(request, *args, **kwargs):
    study_mode = request.GET.get('mode')
    slug = kwargs.get('slug')

    buttons_to_show = {
        'show_back': True,
        'show_hint': True,
        'show_similar': True,
        'show_first_letters': True,
        'scramble_letters': True,
        'speech': True
    }
    context_data = {
        'csrf_token': request.COOKIES.get('csrftoken'),
        'slug': slug,
        'study_mode': study_mode,
        'urls': {
            'get_card': reverse('get_card', kwargs={'slug': slug}),
            'get_hint': reverse('get_hint', kwargs={'mappings_id': 'dummy_mappings_id'}),
            'get_similar_words': reverse('get_similar_words', kwargs={'mappings_id': 'dummy_mappings_id'}),
            'get_sound': reverse('get_sound', kwargs={'mappings_id': 'dummy_mappings_id'})
        }
    }
    context = {
        'context_json': json.dumps(context_data),
        'buttons_to_show': buttons_to_show
    }
    return render(request, 'cardmode/studying_mode.html', context)



@login_required
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
