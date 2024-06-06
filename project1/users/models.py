from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image = models.ImageField(upload_to='users/', blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, max_length=254, verbose_name='email address')
    username = models.CharField(blank=True, null=True, max_length=120)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email