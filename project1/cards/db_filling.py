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



import openai
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings


