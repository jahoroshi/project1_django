from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from cards.forms import ImportCardsForm
from cards.services.check_permission import check_permission_with_slug
from cards.services.handle_card_import import import_handler
from cards.models import Mappings


@login_required
@check_permission_with_slug
def import_cards(request, *args, **kwargs):
    slug = kwargs.get('slug')
    if request.method == 'POST':
        form = ImportCardsForm(request.POST)
        if form.is_valid():
            count = Mappings.objects.filter(category__slug=slug).count()
            if count > 500 and len(form.cleaned_data) > 400:
                messages.error(request, 'Import isn\'t possible right now because the deck has over 500 cards. However, you can import the cards into other decks.',
                               extra_tags='import')
                return redirect('import_cards', slug=slug)

            imports = import_handler(form.cleaned_data, slug)
            if imports:
                messages.success(request, f'{imports} cards imported successfully')
            return HttpResponseRedirect(reverse('deck_content', args=[slug]))
    else:
        form = ImportCardsForm()
    return render(request, 'cards/cards_import.html', {'form': form, 'slug': slug})
