from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from cards.forms import ImportCardsForm
from cards.models import Cards, Mappings, Categories
from cards.services.check_permission import check_permission_with_slug

@login_required
@check_permission_with_slug
def import_cards(request, *args, **kwargs):
    slug = kwargs.get('slug')
    if request.method == 'POST':
        form = ImportCardsForm(request.POST)
        if form.is_valid():
            category = Categories.objects.get(slug=slug)
            text = form.cleaned_data['text']

            words_separator = form.cleaned_data['words_separator']
            cards_separator = form.cleaned_data['cards_separator']
            words_separator_custom = form.cleaned_data['words_separator_custom']
            cards_separator_custom = form.cleaned_data['cards_separator_custom']

            separators = {'tab': '\t', 'comma': ',', 'words_custom': words_separator_custom, 'new_line': '\r\n',
                          'semicolon': ';', 'cards_custom': cards_separator_custom}

            words_sep = separators[words_separator]
            cards_sep = separators[cards_separator]
            cards = text.split(cards_sep)
            for card in cards:
                try:
                    front_side, back_side = card.split(words_sep)
                    object_card = Cards.objects.create(side1=front_side.strip(), side2=back_side.strip())
                    Mappings.objects.create(card=object_card, category=category)
                except ValueError:
                    continue
            return HttpResponseRedirect(reverse('deck_content', args=[slug]))
    else:
        form = ImportCardsForm()
    return render(request, 'cards/cards_import.html', {'form': form, 'slug': slug})