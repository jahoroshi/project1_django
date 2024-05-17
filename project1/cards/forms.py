from django import forms
from django.shortcuts import get_object_or_404

from .models import Cards, Categories


class CardCheckForm(forms.Form):
    mappings = forms.IntegerField(required=True)
    rating = forms.IntegerField(required=False)


class AddCardForm(forms.Form):
    side1 = forms.CharField()
    side2 = forms.CharField()
    # category = forms.IntegerField()
    # status = forms.IntegerField()
    # repetition = forms.IntegerField()


class MappingsForm(forms.ModelForm):
    # side1 = forms.CharField()
    # side2 = forms.CharField()
    #
    # class Meta:
    #     model = Mappings
    #     fields = ['repetition', 'side1', 'side2', 'status']
    #
    # def save(self, commit=True):
    #     instance = super(MappingsForm, self).save(commit=False)
    #     card = Cards(side1=self.cleaned_data['side1'], side2=self.cleaned_data['side2'])
    #     card.save()
    #     instance.card = card
    #     if commit:
    #         instance.save()
    #     return instance
    ...


class CardForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Categories.objects.all().order_by('pk'))
    is_two_sides = forms.BooleanField(required=False, label='Two sides')

    class Meta:
        model = Cards
        fields = ['side1', 'side2', 'category', 'is_two_sides']

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug', None)
        super(CardForm, self).__init__(*args, **kwargs)

        if self.slug:
            category = get_object_or_404(Categories, slug=self.slug)
            self.fields['category'].initial = category.pk
        elif self.slug is None and kwargs.get('instance'):
            category = get_object_or_404(Categories, mappings__card=kwargs.get('instance'))
            self.fields['category'].initial = category.pk


class ImportCardsForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea,
        label='Import your data. Copy and paste your data here from Quizlet, Google doc, spreadsheet, etc.'
    )

    WORDS_CHOICES = [
        ('tab', 'Tab'),
        ('comma', 'Comma'),
        ('words_custom', 'Custom'),
        ]

    CARDS_CHOICES = [
        ('new_line', 'New line'),
        ('semicolon', 'Semicolon'),
        ('cards_custom', 'Custom'),
    ]
    words_separator = forms.ChoiceField(
        choices=WORDS_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'inline-radio'}),
        initial='tab',
        label='Between Front and Back sides'
    )
    words_separator_custom = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Custom: e.g. -', 'class': 'inline-text'}),
        label=False,

    )
    cards_separator = forms.ChoiceField(
        choices=CARDS_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'inline-radio'}),
        initial='new_line',
        label='Between cards'
    )
    cards_separator_custom = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Custom: e.g. -', 'class': 'inline-text'}),
        label=False,

    )
