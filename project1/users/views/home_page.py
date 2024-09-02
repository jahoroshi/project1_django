from django.shortcuts import render, redirect
from django.contrib import auth, messages

from cards.services.first_deck_fill import deck_filling
from users.forms import UserFirstStepLoginForm, UserSecondStepLoginForm
from users.models import User


def home(request):
    """
    Handles the initial login step. If the user is authenticated, redirects to the decks list.
    Otherwise, processes the first step of the login form.
    """
    if request.user.is_authenticated:
        return redirect('decks_list')

    if request.method == 'POST':
        form = UserFirstStepLoginForm(request.POST)
        if form.is_valid():
            # Store email in session and proceed to the second step of login
            request.session['email'] = form.cleaned_data['email']
            return redirect('users:second_step')

    form = UserFirstStepLoginForm()
    return render(request, 'users/home.html', {'form': form})


def second_step(request):
    """
    Handles the second step of login, where the user enters their password.
    Authenticates the user and performs deck filling if the user is new.
    """
    email = request.session.get('email')
    if not email:
        return redirect('users:home')

    if request.method == 'POST':
        form = UserSecondStepLoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user, created = User.objects.get_or_create(email=email)
            if created:
                # Set password for the newly created user
                user.set_password(password)
                user.save()
            user = auth.authenticate(email=email, password=password)
            if user:
                auth.login(request, user)

                if request.META:
                    language_code = request.META.get('LANG', 'en')
                else:
                    language_code = 'en'

                language = 'ru' if 'ru' in language_code else 'en'
                deck_filling(user, language)
                messages.info(
                    request,
                    "👋 | WELCOME<br><br>🎁 We've created a sample deck "
                    "for you to explore all the features of our app. "
                    "Feel free to delete it and create your own unique categories once you're familiar with everything."
                    "<br><br>🤓 Take your time, and enjoy!<br><br>🫶 Good luck! 😎",
                    extra_tags='decks-list'
                )

                return redirect('decks_list')
            else:
                messages.error(
                    request,
                    'There was an error with your authentication. Please try again.',
                    extra_tags='auth'
                )
                return redirect('users:login')

    form = UserSecondStepLoginForm()
    return render(request, 'users/home.html', {'form': form, 'email': email})
