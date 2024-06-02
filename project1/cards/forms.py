from django import forms
from django.shortcuts import get_object_or_404

from .models import Cards, Categories


class CardCheckForm(forms.Form):
    mappings = forms.IntegerField(required=True)
    rating = forms.IntegerField(required=False)


class CardForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Categories.objects.all().order_by('pk'),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'aria-label': 'Category choose',
    }),
        required=False
    )
    is_two_sides = forms.BooleanField(
        required=False, label='Two sides',
        widget=forms.CheckboxInput(attrs={
            'class': "form-check-input",
            'type': "checkbox",
            'role': "switch",
            'id': "flexSwitchCheckDefault"
        }))

    class Meta:
        model = Cards
        fields = ['side1', 'side2', 'category', 'is_two_sides']
        widgets = {
            'side1': forms.Textarea(attrs={
                'class': 'form-control w-75',
                'aria-labal': 'Side 1',
                'rows': 3,

            }),
            'side2': forms.Textarea(attrs={
                'class': 'form-control w-75',
                'aria-labal': 'Side 2',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug', None)
        super(CardForm, self).__init__(*args, **kwargs)

        if self.slug:
            category = get_object_or_404(Categories, slug=self.slug)
            self.fields['category'].initial = category.pk
        elif self.slug is None and kwargs.get('instance'):
            category = get_object_or_404(Categories, mappings__card=kwargs.get('instance'))
            self.fields['category'].initial = category.pk

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')

        # Устанавливаем категорию по умолчанию, если она не пришла от клиента
        if not category:
            slug = self.slug
            category = Categories.objects.get(slug=slug)
            cleaned_data['category'] = category

        return cleaned_data


class ImportCardsForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'class': "form-control w-100", 'rows': 10}),
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
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='tab',
        label='Between Front and Back sides'
    )
    words_separator_custom = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Custom: e.g. -', 'class': 'form-control w-25'}),
        label=False,
        strip=False,

    )
    cards_separator = forms.ChoiceField(
        choices=CARDS_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='new_line',
        label='Between cards'
    )
    cards_separator_custom = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Custom: e.g. -', 'class': 'form-control w-25'}),
        label=False,
        strip=False

    )
