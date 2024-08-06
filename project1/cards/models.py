import re

from autoslug import AutoSlugField
from django.core.exceptions import ValidationError
from django.db import models
from transliterate import detect_language, translit

from cards.services.compute_study_metrics import compute_study_easiness, scale_easiness, NextReviewDate
from users.models import User

NUM_BOXES = 5
BOXES = range(1, NUM_BOXES + 2)


def custom_slugify(value):
    value = value.replace('_', '-').lower().strip()
    if not value[0].isalpha():
        value = f'deck-{value}'
    if detect_language(value):
        value = translit(value, reversed=True)
    value = re.sub(r'[^a-z0-9-]+', '', value)
    return value


class Card(models.Model):
    question = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    box = models.IntegerField(
        choices=zip(BOXES, BOXES),
        default=BOXES[0],
    )
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

    def move(self, solved):
        new_box = self.box + 1 if solved else BOXES[0]

        if new_box in BOXES:
            self.box = new_box
            self.save()

        return self


class Users(models.Model):
    name = models.CharField(max_length=100)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)


class Categories(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    # slug = models.SlugField(unique=True, blank=True)
    slug = AutoSlugField(populate_from='name', unique=True, always_update=True, slugify=custom_slugify, max_length=50)

    def clean(self):
        if not any(c.isalnum() for c in self.name):
            raise ValidationError(('Имя категории должно содержать хотя бы одну букву и одну цифру.'))

    # def save(self, *args, **kwargs):
    #     # if not self.slug:
    #     name = self.name.replace('_', '-')
    #     if not name[0].isalpha():
    #         name = f'deck-{name}'
    #     if detect_language(name):
    #         name = translit(name, reversed=True)
    #     slug = slugify(name)
    #     for num in range(100):
    #         if Categories.objects.filter(slug=slug).exists():
    #             slug = f'{slug}-{self.user.id}' if not num else f'{slug}-{str(time()).split(".")[0]}'
    #         else:
    #             break
    #     self.slug = slug
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Cards(models.Model):
    side1 = models.CharField(max_length=255)
    side2 = models.CharField(max_length=255)
    transcription = models.CharField(max_length=255)
    audio_side1 = models.URLField(blank=True, null=True, max_length=255)
    audio_side2 = models.URLField(blank=True, null=True, max_length=255)

    def __str__(self):
        return self.side1

    def save(self, *args, **kwargs):
        self.side1 = self.side1.replace("<", "‹").replace(">", "›")
        self.side2 = self.side2.replace("<", "‹").replace(">", "›")
        super().save(*args, **kwargs)


class Mappings(models.Model):
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    card = models.ForeignKey(Cards, on_delete=models.CASCADE)
    is_back_side = models.BooleanField(default=False)
    repetition = models.IntegerField(default='0')
    mem_rating = models.IntegerField(default='0')
    easiness = models.FloatField(default='0.0')
    study_mode = models.CharField(max_length=10, default='new')
    review_params = models.JSONField(blank=True, null=True)
    review_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField(auto_now=True)

    def my_debug(self):
        data = (f'ID: {self.id}',
                f'Repetition: {self.repetition}',
                f'Easiness: {self.easiness}',
                f'Mem_rating: {self.mem_rating}',
                f'Study mode: {self.study_mode}')
        print('\033[33;40;1m %-15s %-20s %-20s %-35s %-20s\033[0m' % data, '\n')

    def move(self, rating):
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


class TestSides(models.Model):  # for delete
    side = models.CharField(max_length=255)
    relation = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)


class ActiveStudy(models.Model):  # for delete
    mappings = models.OneToOneField(Mappings, on_delete=models.CASCADE)
    study_mode = models.CharField(max_length=3, default='new')

    class Meta:
        db_table = 'cards_active_study'
