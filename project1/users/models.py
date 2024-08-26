import time

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image = models.ImageField(upload_to='users/', blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, max_length=254, verbose_name='email address')
    username = models.CharField(unique=True, blank=True, null=True, max_length=120)
    password = models.CharField(max_length=128, default='knowledge')
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    session_config = models.JSONField(blank=True, null=True)
    language = models.CharField(max_length=5, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    def save(self, *args, **kwargs):
        if not self.email:
            self.email = f'{self.telegram_id}_{int(time.time())}@ankichat.com'
        return super().save(*args, **kwargs)


class TelegramUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    telegram_id = models.BigIntegerField(blank=True, null=True)
    session_config = models.JSONField(blank=True, null=True)
    language = models.CharField(max_length=5, blank=True, null=True)
