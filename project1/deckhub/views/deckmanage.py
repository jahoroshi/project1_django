from django.db.models import Count, Case, When, F, IntegerField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
)

from cards.services.check_post_request import CheckReuqest, is_post_unique
from cards.models import Cards, Categories, Card
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
import json

class DecksListView(ListView):
    model = Categories
    queryset = Categories.objects.annotate(cards_count=Count('mappings'), reviews_count=Count(
        Case(
            When(mappings__review_date__lte=now().date(), then=1),
            output_field=IntegerField(),
        )
    ))
    template_name = 'deckhub/decks_list.html'

    def get_ordering(self):
        return ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DeckCreateView(CheckReuqest, CreateView):
    model = Categories
    fields = ['name']
    template_name = 'deckhub/deck_form.html'
    success_url = reverse_lazy('decks_list')


class DeckUpdateView(DeckCreateView, UpdateView):
    model = Categories


def deck_delete(request, pk):
    deck = get_object_or_404(Categories, pk=pk)
    if request.method == 'POST' and is_post_unique(request):
        cards = Cards.objects.filter(mappings__isnull=True)
        deck.delete()
        cards.delete()
        return redirect(reverse('decks_list'))
    slug = Categories.objects.get(pk=pk).slug
    return render(request, 'cards/delete_object.html', {'deck_name': deck.name, 'slug': slug})


class DeckContentView(ListView):
    model = Cards
    template_name = 'deckhub/deck_content.html'

    def get_queryset(self):
        slug = self.kwargs['slug']
        queryset = Cards.objects.filter(
            mappings__category__slug=slug,
            mappings__is_back_side=False
        ).values(
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


