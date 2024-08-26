from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Case, When, F, IntegerField, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
)

from cards.models import Cards, Categories
from cards.services.check_permission import check_permission_with_slug, CheckPermission
from cards.services.check_post_request import CheckReuqest, is_post_unique


class DecksListView(LoginRequiredMixin, ListView):
    model = Categories
    template_name = 'deckhub/decks_list.html'

    def get_queryset(self):
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
        return ['name']


class DeckCreateView(LoginRequiredMixin, CheckReuqest, CreateView):
    model = Categories
    fields = ['name']
    template_name = 'deckhub/deck_form.html'
    success_url = reverse_lazy('decks_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs.update({
            'class': "form-control",
            'placeholder': "Deck Name",
            'required': True,
        })
        form.fields['name'].label = "Deck Name"
        return form


class DeckUpdateView(DeckCreateView, UpdateView):
    model = Categories


class DeckContentView(LoginRequiredMixin, CheckPermission, ListView):
    model = Cards
    template_name = 'deckhub/deck_content.html'

    def get_queryset(self):
        slug = self.kwargs['slug']
        # check_permission_with_slug(user=self.request.user, slug=slug)

        queryset = Cards.objects.filter(
            mappings__category__slug=slug,
        ).filter(~Q(mappings__study_mode='known')).values(
            'mappings__review_date', 'id', 'mappings', 'mappings__category__name', front_side=F('side1'),
            back_side=F('side2')
        ).order_by('mappings__repetition')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['slug'] = slug
        context['deck_name'] = Categories.objects.get(slug=slug)
        return context


@login_required
@check_permission_with_slug
def deck_delete(request, slug):
    deck = get_object_or_404(Categories, slug=slug)
    if request.method == 'POST' and is_post_unique(request):
        cards = Cards.objects.filter(mappings__isnull=True)
        deck.delete()
        cards.delete()
        return redirect(reverse('decks_list'))
    return render(request, 'cards/delete_object.html', {'deck_name': deck.name, 'slug': slug})
