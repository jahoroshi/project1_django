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
            messages.error(request, 'There was an error with your authentication. Please try again.')
    else:
        form = UserLoginForm()

    context = {'title': 'Login', 'form': form}
    return render(request, 'users/user_auth_base.html', context)


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('decks_list'))
        else:
            messages.error(request, 'There was an error with your registration. Please try again.')
    form = UserRegistrationForm()
    context = {'title': 'Registration', 'form': form}
    return render(request, 'users/user_auth_base.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(instance=request.user, data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get('new_password')
            current_password = form.cleaned_data.get('password')
            password_is_valid = None
            if current_password:
                password_is_valid = user.check_password(current_password)
                if password_is_valid:
                    if new_password:
                        user.set_password(new_password)
                        user.save()
                        user = auth.authenticate(username=user.email, password=new_password)
                        messages.success(request, 'Data was successfully changed.')

                else:
                    messages.error(request, 'The current password is incorrect.')
            else:
                if 'email' in form.changed_data:
                    user.save()
                    messages.success(request, 'Data was successfully changed.')
            if password_is_valid:
                auth.login(request, user)
            else:
                auth.login(request, request.user)
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            print(form.errors)
    form = UserProfileForm(instance=request.user)
    context = {'title': 'Profile', 'form': form}
    return render(request, 'users/profile.html', context)


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

