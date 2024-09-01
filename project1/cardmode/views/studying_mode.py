import random
import json
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import auth, messages

from cards.models import Cards, Mappings
from cards.services.query_builder import get_card_queryset
from speech.views import synthesize_speech
from cards.services.check_permission import check_permission_with_slug
from django.contrib.auth.decorators import login_required

from users.forms import TelegramWebAppForm
from users.models import User


@login_required
@check_permission_with_slug
def study_view_start(request, *args, **kwargs):
    """
    Renders the study mode start view for authenticated users with proper permissions.
    """
    return render(request, 'cardmode/studying_mode.html')


def telegram_web_app_start(request, *args, **kwargs):
    """
    Handles the start of the study view for Telegram Web App users.
    If a valid Telegram ID is provided, the user is logged in and redirected to the Telegram study mode.
    Otherwise, an error page is displayed.
    """
    if request.method == 'GET':
        telegram_id = kwargs.get('telegram_id')

        if telegram_id:
            # Attempt to retrieve the user by their Telegram ID
            user = User.objects.filter(telegram_id=telegram_id).first()
            if user:
                # Log in the user and set the session's authentication method
                auth.login(request, user)
                request.session['auth_method'] = 'telegram'
                return render(request, 'cardmode/studying_mode_tg.html')
        else:
            # Render an error page if no valid Telegram ID is provided
            return render(request, 'deckhub/error_page.html')
