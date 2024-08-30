from django.conf import settings

def current_bot_name(request):
    bot_name = settings.BOT_NAME
    return {'BOT_NAME': bot_name}