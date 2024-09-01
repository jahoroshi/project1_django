from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from cards.forms import CardCheckForm, CardForm
from cards.models import Cards, Mappings
from cards.services.check_permission import CheckPermission
from cards.services.check_post_request import CheckReuqest, is_post_unique
from cards.services.query_builder import get_card_queryset
from cards.services.second_side_creator import create_second_side


class CardCreateView(LoginRequiredMixin, CheckPermission, CreateView):
    """
    View for creating a new card. Ensures the user has permission to create the card
    and that the card content is unique.
    """
    model = Cards
    form_class = CardForm
    template_name = 'cards/card_form.html'
    success_url = reverse_lazy('card_create')

    def form_valid(self, form):
        """
        Save the card and create a mapping. If the card has two sides, create the second side.
        """
        if is_post_unique(self.request):
            category = form.cleaned_data['category']
            user = self.request.user
            if category.user != user:
                raise PermissionDenied

            self.object = form.save(commit=False)
            self.object.save()

            mapping_object = Mappings.objects.create(card=self.object, category=category)

            if form.cleaned_data['is_two_sides']:
                create_second_side(category, mapping_object, side1=self.object.side1, side2=self.object.side2)

        return HttpResponseRedirect(self.request.path)

    def get_form_kwargs(self):
        """
        Add slug and user information to form kwargs.
        """
        kwargs = super().get_form_kwargs()
        kwargs['slug'] = self.kwargs.get('slug')
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Add slug to context data.
        """
        context = super().get_context_data(**kwargs)
        context['slug'] = self.kwargs.get('slug')
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests by ensuring the object is None before passing to the parent method.
        """
        self.object = None
        return super().post(request, *args, **kwargs)


class CardUpdateView(CardCreateView, UpdateView):
    """
    View for updating an existing card. Inherits from CardCreateView and adds additional logic
    for handling updates.
    """

    def form_valid(self, form):
        """
        Update the card and its mapping. If the card is marked as having two sides,
        create the second side if it doesn't already exist.
        """
        slug = self.kwargs['slug']
        category = form.cleaned_data['category']
        if is_post_unique(self.request):
            self.object = form.save(commit=False)
            self.object.save()
            mapping_object = Mappings.objects.get(card=self.object)
            mapping_object.category = category
            mapping_object.save()

            if form.cleaned_data['is_two_sides'] and not mapping_object.has_two_sides:
                create_second_side(category, mapping_object, side1=self.object.side1, side2=self.object.side2)

        return HttpResponseRedirect(reverse('deck_content', kwargs={'slug': slug}))

    def get_context_data(self, **kwargs):
        """
        Add update flag to context data.
        """
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context


class CardDeleteView(LoginRequiredMixin, CheckPermission, CheckReuqest, DeleteView):
    """
    View for deleting a card. Ensures the user has permission to delete the card.
    """
    template_name = 'cards/delete_object.html'
    model = Cards

    def get_success_url(self):
        """
        Return the URL to redirect to after a successful deletion.
        """
        slug = self.kwargs['slug']
        return reverse_lazy('deck_content', args=[slug])

    def get_context_data(self, **kwargs):
        """
        Add slug to context data.
        """
        context = super().get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context


class BoxView(ListView):
    """
    View for displaying a list of cards in a study box. Handles filtering by study mode.
    """
    model = Cards
    template_name = 'cards/box.html'
    form_class = CardCheckForm

    def get_queryset(self):
        """
        Retrieve the queryset based on the study mode and slug. Handles exceptions if no cards are found.
        """
        study_mode = self.request.GET.get('study_mode')
        self.kwargs['study_mode'] = study_mode
        slug = self.kwargs['slug']
        try:
            queryset, self.kwargs['ratings_count'] = get_card_queryset(slug=slug, study_mode=study_mode)
        except Cards.DoesNotExist:
            queryset = Cards.objects.none()

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add additional context data related to the ratings count, slug, and study mode.
        """
        context = super().get_context_data(**kwargs)
        context['ratings_count'] = self.kwargs.get('ratings_count', {})
        context['slug'] = self.kwargs['slug']
        context['study_mode'] = self.kwargs['study_mode']
        context['check_card'] = self.object_list
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to update the rating of a card. Redirects to the same page after processing.
        """
        form = self.form_class(request.POST)
        if form.is_valid() and is_post_unique(request):
            mappings = get_object_or_404(Mappings, pk=form.cleaned_data['mappings'])
            mappings.move(form.cleaned_data['rating'])
        success_url = self.request.get_full_path()
        return HttpResponseRedirect(success_url)
