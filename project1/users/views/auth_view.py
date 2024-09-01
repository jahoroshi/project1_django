from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse

from cards.models import Categories
from cards.services.first_deck_fill import deck_filling
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm, TelegramUserForm, DeleteUserForm, \
    EmptyUserProfileForm
from users.models import User
from deckhub.views import first_deck_fill


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(email=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('decks_list'))
        else:
            messages.error(request, 'There was an error with your authentication. Please try again.', extra_tags='auth')

    form = UserLoginForm()
    context = {'form': form, 'page_mode': 'login'}
    return render(request, 'users/user_auth_base.html', context)


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = auth.authenticate(email=email, password=password)
            if user:
                auth.login(request, user)

                language_code = request.META.get('LANG')
                language = 'ru' if 'ru' in language_code else 'en'
                deck_filling(user, language)
                messages.info(request, "👋 | WELCOME<br><br>🎁 Мы сделали для вас тестовую категорию, чтобы вы могли познакомиться со всеми возможностями нашего приложения. <br><br>🤓 Когда освоитесь, можете удалить её и создать свои собственные уникальные категории.<br><br>🫶 Удачи! 😎", extra_tags='decks-list')
                return HttpResponseRedirect(reverse('decks_list'))
        else:
            messages.error(request, 'There was an error with your registration. Please try again.', extra_tags='auth')
    form = UserRegistrationForm()
    context = {'form': form, 'page_mode': 'registration'}
    return render(request, 'users/user_auth_base.html', context)


@login_required
def profile(request):
    has_credentials = True if request.user.password != 'knowledge' else False
    if request.method == 'POST':
        if has_credentials:
            form = UserProfileForm(instance=request.user, data=request.POST)
        else:
            form = EmptyUserProfileForm(instance=request.user, data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get('new_password')
            current_password = form.cleaned_data.get('current_password')
            first_password = form.cleaned_data.get('first_password')
            if current_password and new_password:
                user.set_password(new_password)
                user.save()
                if 'email' in form.changed_data:
                    messages.success(request, 'Email was successfully changed.', extra_tags='profile')
                messages.success(request, 'Password was successfully changed.', extra_tags='profile')
                auth.login(request, user)
            elif 'email' in form.changed_data:
                if has_credentials:
                    text = 'Email was successfully changed.'
                else:
                    text = 'Credentials have been successfully added.'
                    user.set_password(first_password)
                messages.success(request, text)
                user.save()
                auth.login(request, user)
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            messages.error(request, '<br>'.join([' '.join(error) for error in form.errors.values()]), extra_tags='profile')
    form = UserProfileForm(instance=request.user) if has_credentials else EmptyUserProfileForm()
    context = {'form': form, 'page_mode': 'profile', 'has_credentials': has_credentials}
    return render(request, 'users/profile.html', context)

@login_required
def delete_user(request):
    if request.method == 'POST':
        form = DeleteUserForm(data=request.POST)
        if form.is_valid():
            current_password = form.cleaned_data.get('current_password')
            if request.user.check_password(current_password):
                request.user.delete()
                messages.success(request, 'Account was successfully deleted.', extra_tags='profile')
                return redirect('users:registration')
            else:
                messages.error(request, 'The current password is incorrect.', extra_tags='profile')

    form = DeleteUserForm()
    context = {'form': form, 'page_mode': 'delete_account'}
    return render(request, 'users/profile.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('decks_list'))


def telegram_auth(request):
    if request.method == 'GET':
        form = TelegramUserForm(data=request.GET)
        if form.is_valid():
            telegram_id = form.cleaned_data['id']
            user, created = User.objects.get_or_create(telegram_id=telegram_id)
            auth.login(request, user)
            return HttpResponseRedirect(reverse('decks_list'))

    form = UserLoginForm()
    context = {'form': form, 'page_mode': 'login'}
    return render(request, 'users/user_auth_base.html', context)

@login_required
def telegram_connect(request):

    form = UserProfileForm(instance=request.user)
    context = {'form': form, 'page_mode': 'profile', 'has_credentials': True}

    if request.method == 'GET':
        form = TelegramUserForm(data=request.GET)
        if form.is_valid():
            tg_user = form.cleaned_data['id']
            current_user = request.user
            user = User.objects.filter(telegram_id=tg_user).first()
            if user:
                Categories.objects.filter(user=user).update(user=current_user)
                user.delete()
            else:
                current_user.telegram_id = tg_user
                current_user.save()
            messages.success(request, '🎉 Congratulations! Your Telegram account has been successfully linked to your current account. You can now study flashcards both on this web version and through the Telegram bot. To start the bot, click the AnkiChatBot button.',  extra_tags='profile')
            return redirect('users:profile')
        else:
            messages.error(request, 'We’re experiencing an issue with Telegram’s server. Please try again later.', extra_tags='profile')


    return render(request, 'users/profile.html', context)