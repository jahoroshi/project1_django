from django.core.cache import cache
from django.db.models import Count, Case, When, Q, F, IntegerField
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from cards.check_post_request import CheckReuqest, is_post_unique
from cards.query_builder import build_card_view_queryset
from .forms import CardCheckForm, CardForm, ImportCardsForm
from .models import Cards, Mappings, Categories
from django.utils.timezone import now



class CardsListView(ListView):
    model = Cards
    template_name = 'cards/cards_list.html'

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


def import_cards(request, *args, **kwargs):
    if request.method == 'POST':
        form = ImportCardsForm(request.POST)
        if form.is_valid():
            slug = kwargs['slug']
            category = Categories.objects.get(slug=slug)
            text = form.cleaned_data['text']
            words_separator = form.cleaned_data['words_separator']
            cards_separator = form.cleaned_data['cards_separator']
            words_separator_custom = form.cleaned_data['words_separator_custom']
            cards_separator_custom = form.cleaned_data['cards_separator_custom']
            separators = {'tab': '  ', 'comma': ',', 'words_custom': words_separator_custom, 'new_line': '\r\n',
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
    return render(request, 'cards/cards_import.html', {'form': form})


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


class BoxView(ListView):
    model = Cards
    template_name = 'cards/box.html'
    form_class = CardCheckForm

    def get_queryset(self):
        study_mode = self.request.GET.get('study_mode')
        self.kwargs['study_mode'] = study_mode
        slug = self.kwargs['slug']
        queryset, self.kwargs['ratings_count'] = build_card_view_queryset(slug=slug, study_mode=study_mode)
        queryset = queryset.first()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ratings_count'] = self.kwargs.get('ratings_count', {})
        context['slug'] = self.kwargs['slug']
        context['study_mode'] = self.kwargs['study_mode']
        if self.object_list:
            # context['my_debug'] = Mappings.objects.filter(id=self.object_list['mappings']).values('id', 'repetition',
            #                                                                                       'mem_rating',
            #                                                                                       'easiness',
            #                                                                                       'study_mode')
            context['check_card'] = self.object_list
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
    queryset = Categories.objects.annotate(cards_count=Count('mappings'), reviews_count=Count(
        Case(
            When(mappings__review_date__lte=now().date(), then=1),
            output_field=IntegerField(),
        )
    ))
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
    return render(request, 'cards/delete_object.html', {'deck_name': deck.name})


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
