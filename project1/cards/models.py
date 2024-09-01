import re
from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from transliterate import detect_language, translit

from cards.services.compute_study_metrics import compute_study_easiness, scale_easiness, NextReviewDate


def custom_slugify(value):
    """
    Custom slugification function to generate slugs with specific rules.
    - Replaces underscores with hyphens, converts to lowercase, and trims spaces.
    - Adds a prefix if the first character is not alphabetical.
    - Transliterates the value if it's in a non-Latin script.
    - Removes any non-alphanumeric characters, except for hyphens.
    """
    value = value.replace('_', '-').lower().strip()
    if not value[0].isalpha():
        value = f'deck-{value}'
    if detect_language(value):
        value = translit(value, reversed=True)
    value = re.sub(r'[^a-z0-9-]+', '', value)
    return value


class Users(models.Model):
    """
    Model representing a user with basic authentication details.
    """
    name = models.CharField(max_length=100)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)


class Categories(models.Model):
    """
    Model representing a category for organizing cards.
    - `name`: The name of the category.
    - `user`: The user who owns this category.
    - `slug`: A URL-friendly slug generated from the category name.
    """
    name = models.CharField(max_length=25)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    slug = AutoSlugField(populate_from='name', unique=True, always_update=True, slugify=custom_slugify, max_length=50)

    def clean(self):
        """
        Custom validation to ensure the category name contains at least one alphanumeric character.
        """
        if not any(c.isalnum() for c in self.name):
            raise ValidationError('The category name must contain at least one letter and one number.')

    def __str__(self):
        return self.name


class Cards(models.Model):
    """
    Model representing a flashcard with two sides.
    - `side1`: The front of the card.
    - `side2`: The back of the card.
    - `transcription`: Optional transcription for pronunciation.
    - `audio`: Optional URL to an audio file.
    """
    side1 = models.CharField(max_length=255)
    side2 = models.CharField(max_length=255)
    transcription = models.CharField(max_length=255)
    audio = models.URLField(blank=True, null=True, max_length=255)

    def __str__(self):
        return self.side1

    def save(self, *args, **kwargs):
        """
        Override the save method to replace angle brackets in card content
        with their typographic alternatives.
        """
        self.side1 = self.side1.replace("<", "‹").replace(">", "›")
        self.side2 = self.side2.replace("<", "‹").replace(">", "›")
        super().save(*args, **kwargs)


class Mappings(models.Model):
    """
    Model representing the relationship between cards and categories, including study metrics.
    - `category`: The category this mapping belongs to.
    - `card`: The card being mapped.
    - `has_two_sides`: Boolean indicating if the card has two sides.
    - `repetition`: Number of times this card has been reviewed.
    - `mem_rating`: A rating of how well the card is remembered.
    - `easiness`: A calculated value indicating how easy the card is to remember.
    - `study_mode`: The current study status of the card ('new', 'review', 'known').
    - `review_params`: JSON field storing additional review parameters.
    - `review_date`: The next scheduled review date.
    - `upd_date`: The date this record was last updated.
    """
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    card = models.ForeignKey(Cards, on_delete=models.CASCADE)
    has_two_sides = models.BooleanField(default=False)
    repetition = models.IntegerField(default=0)
    mem_rating = models.IntegerField(default=0)
    easiness = models.FloatField(default=0.0)
    study_mode = models.CharField(max_length=10, default='new')
    review_params = models.JSONField(blank=True, null=True)
    review_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(auto_now=True)

    def my_debug(self):
        """
        Print debug information about the current mapping.
        """
        data = (
            f'ID: {self.id}',
            f'Repetition: {self.repetition}',
            f'Easiness: {self.easiness}',
            f'Mem_rating: {self.mem_rating}',
            f'Study mode: {self.study_mode}'
        )
        print('\033[33;40;1m %-15s %-20s %-20s %-35s %-20s\033[0m' % data, '\n')

    def move(self, rating):
        """
        Update the card's status based on the given rating and recalculate study metrics.
        """
        self.my_debug()

        if rating == 4 or self.easiness == 5:
            if self.study_mode == 'new':
                self.study_mode = 'review'
            rev_params, rev_date = NextReviewDate(self.review_params or {}).review(scale_easiness(self.easiness))
            self.review_params = rev_params
            self.review_date = rev_date
            self.repetition = 0
            self.mem_rating = 0
            print(rev_params, '    ', rev_date)
        elif rating == 5:
            self.study_mode = 'known'
        else:
            self.easiness = compute_study_easiness(self.easiness, rating, self.repetition)
            if self.mem_rating == rating == 3:
                self.easiness = min(scale_easiness(self.easiness), 5)
            self.repetition += 1
            self.mem_rating = rating

        self.save()
        self.my_debug()
        return self
