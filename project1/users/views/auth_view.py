from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse

from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm, TelegramUserForm


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('decks_list'))
        else:
            messages.error(request, 'There was an error with your registration.')
    else:
        form = UserLoginForm()

    context = {'title': 'Login', 'form': form}
    return render(request, 'users/user_auth_base.html', context)


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Welcome to our community.')
            return HttpResponseRedirect(reverse('users:login'))
        else:
            messages.error(request, 'There was an error with your registration.')
    form = UserRegistrationForm()
    context = {'title': 'Registration', 'form': form}
    return render(request, 'users/user_auth_base.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data was successfully changed.')
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            print(form.errors)
    form = UserProfileForm(instance=request.user)
    context = {'title': 'Profile', 'form': form}
    return render(request, 'users/user_auth_base.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('decks_list'))


def telegram_auth(request):
    if request.method == 'GET':
        form = TelegramUserForm(data=request.GET)
        if form.is_valid():
            id = form.cleaned_data['id']
            username = form.cleaned_data['username']

    return HttpResponseRedirect(request.path)

