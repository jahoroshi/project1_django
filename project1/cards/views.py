import json
import random

from django.db.models import Case, When, Count, F, CharField
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
)

from .forms import CardCheckForm, CardForm
from .models import Cards, Mappings, Categories, ActiveStudy
from django.core.cache import cache
from cards.check_post_request import CheckReuqest, is_post_unique
from django.db.models import Q



class CardsListView(ListView):
    model = Cards
    template_name = 'cards/cards_list.html'

    def get_queryset(self):
        slug = self.kwargs['slug']
        queryset = Cards.objects.filter(
            mappings__category__slug=slug,
            mappings__is_back_side=False
        ).values(
            'mappings__repetition', 'id', 'mappings', 'mappings__category__name', front_side=F('side1'), back_side=F('side2')
        ).order_by('mappings__repetition')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['slug'] = slug
        context['deck_name'] = Categories.objects.get(slug=slug)
        return context


# def add_card(request):
#     # if this is a POST request we need to process the form data
#     if request.method == 'POST':
#         # create a form instance and populate it with data from the request:
#         form = AddCardForm(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
#             data = form.cleaned_data
#             card = Cards.objects.create(side1=data['side1'], side2=data['side2'])
#             Mappings.objects.create(card=card, category_id=12, )
#             return HttpResponseRedirect(reverse_lazy('card_create'))
#
#     # if a GET (or any other method) we'll create a blank form
#     else:
#         form = AddCardForm()
#
#     return render(request, 'cards/card_form.html', {'form': form})


class CardCreateView(CreateView):
    model = Cards
    form_class = CardForm
    template_name = 'cards/card_form.html'
    success_url = reverse_lazy('card_create')

    def form_valid(self, form):
        if is_post_unique(self.request):
            self.object = form.save(commit=False)
            self.object.save()
            category = form.cleaned_data['category']
            Mappings.objects.create(card=self.object, category=category)
            if form.cleaned_data['is_two_sides']:
                Mappings.objects.create(card=self.object, category=category, is_back_side=True)
        return HttpResponseRedirect(self.request.path)

    def get_form_kwargs(self):
        kwargs = super(CardCreateView, self).get_form_kwargs()
        kwargs['slug'] = self.kwargs.get('slug')
        return kwargs




#
#
# class CardCreateView(CreateView):
#     model = Cards
#     fields = ['side1', 'side2']
#     success_url = reverse_lazy("card_create")
#     template_name = 'cards/card_form.html'
#
#     def form_valid(self, form):
#         self.object = form.save()
#         Mappings.objects.create(card=self.object, category_id=12)
#         return HttpResponseRedirect(self.get_success_url())
#

class CardUpdateView(CardCreateView, UpdateView):

    def form_valid(self, form):
        slug = self.kwargs['slug']
        if is_post_unique(self.request):
            self.object = form.save(commit=False)
            self.object.save()
            card = Mappings.objects.get(card=self.object)
            card.category = form.cleaned_data['category']
            card.save()
        return HttpResponseRedirect(reverse('deck_content', args=[slug]))


class CardDeleteView(CheckReuqest, DeleteView):
    template_name = 'cards/delete_object.html'
    model = Cards

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('deck_content', args=[slug])



def query_builder(*args, **kwargs):
    conditions = Q(category__slug=kwargs['slug'])

    if kwargs['study_mode'] == 'new':
        conditions &= Q(study_mode='new') | Q(mem_rating__range=(1, 4), study_mode='new')

    queryset = Mappings.objects.filter(conditions).order_by('mem_rating').limit(10).order_by('-upd_date')


class BoxView(ListView):
    model = Cards
    template_name = 'cards/box.html'
    form_class = CardCheckForm

    def get_queryset(self):
        conditions = Q(mappings__category__slug=self.kwargs['slug'])
        if self.request.GET.get('study_mode') == 'new':
            conditions &= Q(mappings__review_date__isnull=True)
        elif self.request.GET.get('study_mode') == 'review':
            conditions &= Q(mappings__review_date__lt=timezone.now(), mappings__review_date__isnull=False)
        # if 'rep' in self.kwargs:
        #     conditions &= Q(mappings__repetition=self.kwargs['rep'])
        self.kwargs['conditions'] = conditions
        queryset = Cards.objects.filter(conditions)

        queryset = queryset.annotate(
            front_side=Case(
                When(mappings__is_back_side=True, then=F('side2')),
                default=F('side1'),
                output_field=CharField(),
            ),
            back_side=Case(
                When(mappings__is_back_side=True, then=F('side1')),
                default=F('side2'),
                output_field=CharField(),
            ),
        ).values(
            'mappings__repetition', 'front_side', 'back_side', 'id', 'mappings', 'mappings__category__name'
        ).order_by('mappings__repetition')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['repetition'] = self.kwargs.setdefault('rep', 0)
        context['slug'] = self.kwargs['slug']
        context['conditions'] = self.kwargs['conditions']
        if self.object_list:
            context['check_card'] = random.choice(self.object_list)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid() and is_post_unique(request):
            mappings = get_object_or_404(Mappings, pk=form.cleaned_data['mappings'])
            mappings.move(form.cleaned_data['rating'])
        success_url = self.request.get_full_path()
        return HttpResponseRedirect(success_url)


class DecksListView(ListView):
    model = Categories
    queryset = Categories.objects.annotate(cards_count=Count('mappings'))
    template_name = 'cards/decks_list.html'

    def get_ordering(self):
        return ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DeckCreateView(CheckReuqest, CreateView):
    model = Categories
    fields = ['name']
    template_name = 'cards/deck_form.html'
    success_url = reverse_lazy('decks_list')


class DeckUpdateView(DeckCreateView, UpdateView):
    model = Categories


# class DeckDeleteView(DeleteView):
#     template_name = 'cards/delete_object.html'
#     model = Categories
#     fields = ['name']
#     success_url = reverse_lazy('decks_list')

def deck_delete(request, pk):
    deck = get_object_or_404(Categories, pk=pk)
    if request.method == 'POST' and is_post_unique(request):
        cards = Cards.objects.filter(mappings__isnull=True)
        deck.delete()
        cards.delete()
        return redirect(reverse('decks_list'))
    return render(request,'cards/delete_object.html', {'deck_name': deck.name})


def check_post_unique(view_func):
    def wrapper(request, *args, **kwargs):
        if request.POST:
            token = request.POST.get('csrfmiddlewaretoken')
            if cache.get(token):
                print('doooouble')
                request.POST = {}
            cache.set(token, 'processed', timeout=50)
        return view_func(request, *args, **kwargs)
    return wrapper

# @check_post_unique
def test_contact(request):
    if request.method == 'POST':
        print(request.POST)
        print(is_post_unique(request))
        # if is_post_unique(request):
        #     print('ok')
        # else:
        #     print('DOUBLE POST!!!!')
    return render(request, 'cards/test_contact.html', {})


# class CheckReuqest(View):
#     def post(self, request, *args, **kwargs):
#         self.object = None
#         token = request.POST.get('csrfmiddlewaretoken')
#         if cache.get(token):
#             return HttpResponseRedirect(self.request.path)
#         cache.set(token, 'processed', timeout=50)
#
#         return super().post(request, *args, **kwargs)






