from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from transliterate import translit, detect_language
from cards.services.compute_study_metrics import compute_study_easiness, scale_easiness, NextReviewDate

NUM_BOXES = 5
BOXES = range(1, NUM_BOXES + 2)

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
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    # slug = AutoSlugField(populate_from='title', unique=True) установить!!!

    def clean(self):
        if not any(c.isalnum() for c in self.name):
            raise ValidationError(('Имя категории должно содержать хотя бы одну букву и одну цифру.'))
    def save(self, *args, **kwargs):
        if not self.slug:
            name = self.name
            if detect_language(name):
                name = translit(name, reversed=True)
            self.slug = slugify(name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Cards(models.Model):
    side1 = models.CharField(max_length=255)
    side2 = models.CharField(max_length=255)
    transcription = models.CharField(max_length=255)
    audio = models.URLField(blank=True, null=True, max_length=255)
    def __str__(self):
        return self.side1



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


class TestSides(models.Model):
    side = models.CharField(max_length=255)
    relation = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

class ActiveStudy(models.Model):
    mappings = models.OneToOneField(Mappings, on_delete=models.CASCADE)
    study_mode = models.CharField(max_length=3, default='new')
    class Meta:
        db_table = 'cards_active_study'
