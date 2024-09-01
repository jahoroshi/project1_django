from django.shortcuts import render, redirect
from django.contrib import auth, messages

from cards.services.first_deck_fill import deck_filling
from users.forms import UserFirstStepLoginForm, UserSecondStepLoginForm
from users.models import User


def home(request):
    if request.user.is_authenticated:
        return redirect('decks_list')

    if request.method == 'POST':
        form = UserFirstStepLoginForm(request.POST)
        if form.is_valid():
            request.session['email'] = form.cleaned_data['email']
            return redirect('users:second_step')
    form = UserFirstStepLoginForm()
    return render(request, 'users/home.html', {'form': form})


def second_step(request):
    email = request.session.get('email')
    if not email:
        return redirect('users:home')

    if request.method == 'POST':
        form = UserSecondStepLoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user, created = User.objects.get_or_create(email=email)
            if created:
                user.set_password(password)
                user.save()
            user = auth.authenticate(email=email, password=password)
            if user:
                auth.login(request, user)
                language_code = request.META.get('LANG')
                language = 'ru' if 'ru' in language_code else 'en'
                deck_filling(user, language)
                messages.info(request,
                              "👋 | WELCOME<br><br>🎁 Мы сделали для вас тестовую категорию, чтобы вы могли познакомиться со всеми возможностями нашего приложения. <br><br>🤓 Когда освоитесь, можете удалить её и создать свои собственные уникальные категории.<br><br>🫶 Удачи! 😎",
                              extra_tags='decks-list')

                return redirect('decks_list')
            else:
                messages.error(request, 'There was an error with your authentication. Please try again.',
                               extra_tags='auth')
                return redirect('users:login')

    form = UserSecondStepLoginForm()
    return render(request, 'users/home.html', {'form': form, 'email': email})