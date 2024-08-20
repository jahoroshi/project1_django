from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
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
from cards.models import Cards, Mappings, Categories
from cards.services.check_permission import CheckPermission
from cards.services.check_post_request import CheckReuqest, is_post_unique
from cards.services.query_builder import get_card_queryset
from cards.services.second_side_creator import create_second_side


class CardCreateView(LoginRequiredMixin, CheckPermission, CreateView):
    model = Cards
    form_class = CardForm
    template_name = 'cards/card_form.html'
    success_url = reverse_lazy('card_create')


    def form_valid(self, form):

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
        kwargs = super(CardCreateView, self).get_form_kwargs()
        kwargs['slug'] = self.kwargs.get('slug')
        kwargs['user'] = self.request.user
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

    # def get(self, request, *args, **kwargs):
    #     check_permission_with_slug(user=self.request.user, slug=self.kwargs.get('slug'))
    #     self.object = self.get_object()
    #     return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        slug = self.kwargs['slug']
        category = form.cleaned_data['category']
        if is_post_unique(self.request):
            self.object = form.save(commit=False)
            self.object.save()
            mapping_object = Mappings.objects.get(card=self.object)
            mapping_object.category = category
            mapping_object.save()

            if form.cleaned_data['is_two_sides'] is True and mapping_object.has_two_sides is False:
                create_second_side(category, mapping_object, side1=self.object.side1, side2=self.object.side2)

        return HttpResponseRedirect(reverse('deck_content', kwargs={'slug': slug}))

    def get_context_data(self, **kwargs):
        context = super(CardUpdateView, self).get_context_data(**kwargs)
        context['is_update'] = True
        return context


class CardDeleteView(LoginRequiredMixin, CheckPermission, CheckReuqest, DeleteView):
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
            queryset, self.kwargs['ratings_count'] = get_card_queryset(slug=slug, study_mode=study_mode)
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
