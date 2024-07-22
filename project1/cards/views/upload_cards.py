from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from cards.forms import ImportCardsForm
from cards.services.check_permission import check_permission_with_slug
from cards.services.handle_card_import import import_handler


@login_required
@check_permission_with_slug
def import_cards(request, *args, **kwargs):
    slug = kwargs.get('slug')
    if request.method == 'POST':
        form = ImportCardsForm(request.POST)
        if form.is_valid():
            imports = import_handler(form.cleaned_data, slug)
            if imports:
                messages.success(request, f'{imports} cards imported successfully')
            return HttpResponseRedirect(reverse('deck_content', args=[slug]))
    else:
        form = ImportCardsForm()
    return render(request, 'cards/cards_import.html', {'form': form, 'slug': slug})
