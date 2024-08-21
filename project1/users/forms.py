from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from users.models import User


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': "login",
            'class': "form-control",
            'placeholder': "name",
            'required': True,
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'placeholder': "Password",
            'required': True,
        }),
        label='Password'
    )

    class Meta:
        model = User
        fields = ('username', 'password')



class UserRegistrationForm(UserCreationForm):
    # username = forms.CharField(
    #     widget=forms.TextInput(attrs={
    #         'type': "username",
    #         'class': "form-control",
    #         'placeholder': "name",
    #         'required': True,
    #         'autocomplete': 'new-username',
    #     }))
    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            'type': "email",
            'class': "form-control",
            'placeholder': "email@email.com",
            'required': True,
            # 'autocomplete': 'email',
        }))

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'placeholder': "Password",
            'required': True,
            'autocomplete': 'off',
        }),
        label='Password'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password fields from the form
        # self.fields.pop('password1', None)
        self.fields.pop('password2', None)
        self.fields.pop('username', None)
    class Meta:

        model = User
        # fields = ('username', 'email', 'password1', 'password2')
        fields = ('email', 'password1')




class UserProfileForm(UserChangeForm):
    email = forms.CharField(
        required=False,
        widget=forms.EmailInput(attrs={
            'type': "email",
            'class': "form-control",
            # 'autocomplete': 'email',
        }))

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'autocomplete': 'off',
        }),
        label='Password'
    )

    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'autocomplete': 'off',
        }),
        label='New password'
    )
    class Meta:
        model = User
        fields = ('email', 'password', 'new_password')


class TelegramUserForm(forms.Form):
    id = forms.IntegerField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    auth_date = forms.IntegerField()
    hash = forms.CharField()
