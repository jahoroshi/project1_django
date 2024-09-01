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
    """
    Handles the import of cards into a specific deck.
    Displays a form to upload the cards and handles the form submission.
    """
    slug = kwargs.get('slug')

    if request.method == 'POST':
        form = ImportCardsForm(request.POST)

        if form.is_valid():
            count = Mappings.objects.filter(category__slug=slug).count()

            # Restrict import if the deck has more than 500 cards and the input is too large
            if count > 500 and len(form.cleaned_data['text']) > 400:
                messages.error(
                    request,
                    "Import isn't possible right now because the deck has over 500 cards. "
                    "However, you can import the cards into other decks.",
                    extra_tags='import'
                )
                return redirect('import_cards', slug=slug)

            # Handle the import and provide feedback to the user
            imports = import_handler(form.cleaned_data, slug)
            if imports:
                messages.success(request, f'{imports} cards imported successfully')
            return HttpResponseRedirect(reverse('deck_content', args=[slug]))

    else:
        form = ImportCardsForm()

    return render(request, 'cards/cards_import.html', {'form': form, 'slug': slug})
