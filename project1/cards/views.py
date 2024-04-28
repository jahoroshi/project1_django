from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
)

from .models import Card, Cards, Mappings
import random
from django.shortcuts import get_object_or_404, redirect
from .forms import CardCheckForm, MappingsForm, AddCardForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse




class CardsListView(ListView):
    model = Mappings
    queryset = Mappings.objects.filter(category_id=12).select_related('card').values(
        'repetition', 'card__side1', 'card__side2', 'id', 'card__id'
    ).order_by('repetition')
    template_name = 'cards/cards_list.html'



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
    fields = ['side1', 'side2']
    success_url = reverse_lazy("card_create")
    template_name = 'cards/card_form.html'
    def form_valid(self, form):
        self.object = form.save()
        Mappings.objects.create(card=self.object, category_id=12)
        return HttpResponseRedirect(self.get_success_url())


class CardUpdateView(UpdateView):
    model = Cards
    fields = ['side1', 'side2']
    template_name = 'cards/card_form.html'
    success_url = reverse_lazy('cards_list')


    # def form_valid(self, form):
    #     self.object = form.save()
    #     Mappings.objects.create(card=self.object, category_id=12)
    #     return HttpResponseRedirect(self.get_success_url())


class BoxView(CardsListView):
    template_name = 'cards/box.html'
    form_class = CardCheckForm

    def get_queryset(self):
        return Card.objects.filter(box=self.kwargs['box_num'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['box_number'] = self.kwargs['box_num']
        if self.object_list:
            context['check_card'] = random.choice(self.object_list)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            card = get_object_or_404(Card, id=form.cleaned_data['card_id'])
            card.move(form.cleaned_data['solved'])

        return redirect(request.META.get('HTTP_REFERER'))
