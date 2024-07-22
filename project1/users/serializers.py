from django.utils import timezone
from django.utils.timezone import now
from rest_framework import serializers
from cards.models import Categories, Cards
from users.models import TelegramUser, User


class UserSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('telegram_id', 'language', 'username')
