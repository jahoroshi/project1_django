from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from cards.services.check_post_request import CheckReuqest, is_post_unique
from cards.services.query_builder import build_card_view_queryset
from cards.forms import CardCheckForm, CardForm, ImportCardsForm
from cards.models import Cards, Mappings, Categories


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



class CardUpdateView(CardCreateView, UpdateView):

    def form_valid(self, form):
        slug = self.kwargs['slug']
        if is_post_unique(self.request):
            self.object = form.save(commit=False)
            self.object.save()
            card = Mappings.objects.get(card=self.object)
            card.category = form.cleaned_data['category']
            card.save()
        return HttpResponseRedirect(reverse('decks_list'))


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
        try:
            queryset, self.kwargs['ratings_count'] = build_card_view_queryset(slug=slug, study_mode=study_mode)
        except Cards.DoesNotExist:
            print('s')


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



