import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_1.settings')
django.setup()
from cards.models import Categories
from humanize import naturaldelta
from django.db.models import Count, Case, When, Q, F, IntegerField


from django.db.models import Min, Q, ExpressionWrapper, fields
from django.utils import timezone

now = timezone.now()

print(now)