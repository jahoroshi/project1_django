
from django import forms
from .models import Mappings, Cards

class CardCheckForm(forms.Form):
    card_id = forms.IntegerField(required=True)
    solved = forms.BooleanField(required=False)


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
