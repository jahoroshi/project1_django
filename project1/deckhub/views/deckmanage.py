from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Case, When, F, IntegerField, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.views.generic import ListView, CreateView, UpdateView

from cards.models import Cards, Categories
from cards.services.check_permission import check_permission_with_slug, CheckPermission
from cards.services.check_post_request import CheckReuqest, is_post_unique


class DecksListView(LoginRequiredMixin, ListView):
    """
    Displays a list of decks (categories) for the logged-in user with additional
    annotations for the number of cards and the number of reviews due.
    """
    model = Categories
    template_name = 'deckhub/decks_list.html'

    def get_queryset(self):
        """
        Returns the queryset of categories belonging to the logged-in user,
        annotated with the count of cards and reviews due.
        """
        user = self.request.user
        queryset = Categories.objects.filter(user=user).annotate(
            cards_count=Count(
                Case(
                    When(~Q(mappings__isnull=True) & ~Q(mappings__study_mode='known'), then=1),
                    output_field=IntegerField()
                )
            ),
            reviews_count=Count(
                Case(
                    When(
                        mappings__review_date__lte=now().date(),
                        then=1
                    ),
                    output_field=IntegerField(),
                )
            )
        )
        return queryset

    def get_ordering(self):
        """
        Returns the ordering of the queryset, sorted by deck name.
        """
        return ['name']


class DeckCreateView(LoginRequiredMixin, CheckReuqest, CreateView):
    """
    Handles the creation of a new deck (category) for the logged-in user.
    """
    model = Categories
    fields = ['name']
    template_name = 'deckhub/deck_form.html'
    success_url = reverse_lazy('decks_list')

    def form_valid(self, form):
        """
        Associates the new deck with the logged-in user before saving.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        """
        Customizes the form's appearance and labels.
        """
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs.update({
            'class': "form-control",
            'placeholder': "Deck Name",
            'required': True,
        })
        form.fields['name'].label = "Deck Name"
        return form


class DeckUpdateView(DeckCreateView, UpdateView):
    """
    Handles updating an existing deck (category) for the logged-in user.
    Inherits behavior from DeckCreateView.
    """
    model = Categories


class DeckContentView(LoginRequiredMixin, CheckPermission, ListView):
    """
    Displays the content (cards) of a specific deck, filtering out cards with the study mode 'known'.
    """
    model = Cards
    template_name = 'deckhub/deck_content.html'

    def get_queryset(self):
        """
        Returns the queryset of cards associated with the specified deck (slug).
        Filters out cards that are already marked as 'known'.
        """
        slug = self.kwargs['slug']
        queryset = Cards.objects.filter(
            mappings__category__slug=slug,
        ).filter(~Q(mappings__study_mode='known')).values(
            'mappings__review_date', 'id', 'mappings', 'mappings__category__name', front_side=F('side1'),
            back_side=F('side2')
        ).order_by('mappings__repetition')
        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds additional context data including the deck slug and name.
        """
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['slug'] = slug
        context['deck_name'] = Categories.objects.get(slug=slug)
        return context


@login_required
@check_permission_with_slug
def deck_delete(request, slug):
    """
    Handles the deletion of a specific deck. Deletes the deck and any cards
    that are not associated with any mappings.

    :param request: HTTP request object.
    :param slug: Slug of the deck to be deleted.
    :return: Redirects to the list of decks after deletion, or renders the deletion confirmation page.
    """
    deck = get_object_or_404(Categories, slug=slug)
    if request.method == 'POST':
        # Delete the deck and any orphaned cards (cards with no associated mappings)
        cards = Cards.objects.filter(mappings__isnull=True)
        deck.delete()
        cards.delete()
        return redirect(reverse('decks_list'))

    return render(request, 'cards/delete_object.html', {'deck_name': deck.name, 'slug': slug})
