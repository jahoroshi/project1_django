import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_1.settings')
django.setup()

import csv
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import IntegerField, Min
from django.db.models import Q, Case, When, F, CharField, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cards.models import Categories, Cards
from cards.models import Mappings
from cards.services.handle_card_import import import_handler
from deckhub.serializers import DeckSetSerializer, DeckContentSerializer
from users.models import User

import django
from rest_framework import status

from users.models import User


from cards.models import Categories
from django.db.models import IntegerField

from django.db.models import Q, Case, When, Count
from django.utils import timezone
from django.utils.timezone import now



user = User.objects.get(id=155)
queryset = Categories.objects.filter(user=user).annotate(
            cards_count=Count(
                Case(
                    When(~Q(mappings__isnull=True) & ~Q(mappings__study_mode='known'), then=1),
                    output_field=IntegerField()
                )
            ),
            reviews_count=Count(
                Case(
                    When(
                        mappings__review_date__lte=now().date(),
                        then=1
                    ),
                    output_field=IntegerField(),
                )
            )
        )

for i in queryset:
    print(i.cards_count)