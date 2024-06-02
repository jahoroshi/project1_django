from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from cards.forms import CardCheckForm, CardForm
from cards.models import Cards, Mappings
from cards.services.check_post_request import CheckReuqest, is_post_unique
from cards.services.query_builder import build_card_view_queryset


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

    def get_context_data(self, **kwargs):
        slug = self.kwargs.get('slug')
        context = super(CardCreateView, self).get_context_data(**kwargs)
        context['slug'] = slug
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)





class CardUpdateView(CardCreateView, UpdateView):

    def form_valid(self, form):
        slug = self.kwargs['slug']
        if is_post_unique(self.request):
            self.object = form.save(commit=False)
            self.object.save()
            card = Mappings.objects.get(card=self.object)
            card.category = form.cleaned_data['category']
            card.save()
        return HttpResponseRedirect(reverse('deck_content', kwargs={'slug': slug}))

    def get_context_data(self, **kwargs):
        context = super(CardUpdateView, self).get_context_data(**kwargs)
        context['is_update'] = True
        return context


class CardDeleteView(CheckReuqest, DeleteView):
    template_name = 'cards/delete_object.html'
    model = Cards

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('deck_content', args=[slug])

    def get_context_data(self, **kwargs):
        context = super(CardDeleteView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        return context




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



