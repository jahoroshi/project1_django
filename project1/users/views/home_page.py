from django.shortcuts import render, redirect
from django.contrib import auth, messages

from users.forms import UserFirstStepLoginForm, UserSecondStepLoginForm
from users.models import User


def home(request):
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
        return redirect('home')

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
                return redirect('decks_list')
            else:
                messages.error(request, 'There was an error with your authentication. Please try again.',
                               extra_tags='auth')
                return redirect('users:login')

    form = UserSecondStepLoginForm()
    return render(request, 'users/home.html', {'form': form, 'email': email})