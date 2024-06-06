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
            # 'id': "floatingPassword",
            'placeholder': "Password",
            'required': True,
        }),
        label='Password'
    )

    class Meta:
        model = User
        fields = ('username', 'password')


# class UserRegistrationForm(forms.ModelForm):
#     """
#     A form that creates a user, with no privileges, from the given username and
#     password.
#     """
#     email = forms.CharField(
#         widget=forms.EmailInput(attrs={
#             'type': "email",
#             'class': "form-control",
#             'placeholder': "email@email.com",
#             'required': True,
#             # 'autocomplete': 'email',
#         }))
#
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             'class': "form-control",
#             'placeholder': "Password",
#             'required': True,
#             'autocomplete': 'off',
#         }),
#         label='Password'
#     )
#
#     class Meta:
#         model = User
#         # fields = ('username', 'email', 'password1', 'password2')
#         fields = ('username', 'email', 'password')
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self._meta.model.USERNAME_FIELD in self.fields:
#             self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
#                 "autofocus"
#             ] = True
#
#     # def clean_password2(self):
#     #     password = self.cleaned_data.get("password")
#     #
#     #     return password
#
#     def _post_clean(self):
#         super()._post_clean()
#         # Validate the password after self.instance is updated with form data
#         # by super().
#         password = self.cleaned_data.get("password")
#         if password:
#             try:
#                 password_validation.validate_password(password, self.instance)
#             except ValidationError as error:
#                 self.add_error("password", error)
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#             if hasattr(self, "save_m2m"):
#                 self.save_m2m()
#         return user


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
    # username = forms.CharField(
    #     widget=forms.TextInput(attrs={
    #         'type': "username",
    #         'class': "form-control",
    #         'required': True,
    #         'autocomplete': 'new-username',
    #     }))
    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            'type': "email",
            'class': "form-control",
            'required': True,
            # 'autocomplete': 'email',
        }))

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'required': True,
            'autocomplete': 'off',
        }),
        label='Password'
    )
    class Meta:
        model = User
        fields = ('email', 'password')
