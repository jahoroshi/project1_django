import os

import django
from django.db.models.functions import RowNumber

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_1.settings')
django.setup()
from cards.models import Categories
from humanize import naturaldelta
from django.db.models import Count, Case, When, Q, F, IntegerField, Window

import logging
from random import randint

from django.db.models import Q, Subquery, Case, When, F, CharField, Count
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from cards.exceptions import DeckEmptyException
from cards.models import Mappings, Cards
from django.db.models.functions import Length
Cards.objects.update(audio=None)