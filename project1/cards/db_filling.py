# Предполагается, что у вас уже настроен проект Django и модели определены, как было указано ранее.
# Вот скрипт, который вы можете выполнить, чтобы заполнить таблицы базы данных.

# Сначала убедитесь, что переменная окружения DJANGO_SETTINGS_MODULE настроена
# Вы можете сделать это, выполнив следующую команду в вашей оболочке перед запуском скрипта:
# export DJANGO_SETTINGS_MODULE='имя_вашего_проекта.settings'

# Импортируем настройки Django, чтобы настроить окружение
import os
from supermemo2 import SMTwo
import django
from random import randint
from django.forms import inlineformset_factory
from django.db.models import Case, When, Value, F, CharField

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_1.settings')
django.setup()
from cards.models import Users, Categories, Cards, Mappings, TestSides

# Создаем пользователей


# Создаем карточки
# card2 = Cards.objects.create(side1=a, side2=b, transcription='Транскрипция (2)', audio='http://example.com/audio2.mp3')

# Создаем записи в логе
# log2 = Log.objects.create(category=cat, card=i, timestamp=django.utils.timezone.now(),
#                           localdate=django.utils.timezone.now().date(), repetition=0, status='0')

# print('Таблицы базы данных заполнены тестовыми данными.')



# Mappings.objects.all().delete()
# Users.objects.all().delete()
# Categories.objects.all().delete()
# Cards.objects.all().delete()
# c = 0
# for a, b in word_pairs:
#     c += 1
#     Cards.objects.create(side1=a, side2=b, transcription=c, audio=f'audio{c}.mp3')
# c_id = Cards.objects.get(pk=Cards.objects.all().order_by('id').first().id).id
# coun = Cards.objects.count()
#
# print(c_id, coun)
# for i in range(c_id, c_id + coun):
#     cat = Categories.objects.get(pk=(i-c_id + 1) % 2 + 1)
#     card = Cards.objects.get(pk=i)
#     Mappings.objects.create(category=cat, card=card)


# print(Cards.objects.get(pk=Cards.objects.all().order_by('id').first().id).id)
count = 0
# users_data = (
#     ("Андрей", "andrew82", "P@ssw0rd123", "andrew82@example.com"),
#     ("Елена", "elenasmith", "S3cur3P@ss", "elena.smith@email.com"),
#     ("Иван", "ivan_golfer", "G0lf1ngRulz!", "ivan.golfer@mail.ru"),
#     ("Наталья", "naty_green", "Gr33nTea2024", "naty.green@emailprovider.com"),
#     ("Петр", "pete1975", "P@ssw0rdPete", "pete1975@example.com")
# )
#
# for a, b, c, d in users_data:
#     Users.objects.create(name=a, login=b, password=c, email=d)
#     print(f"{a} - {b} - {c} - {d}")

# categories_data = ('Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5')
# for i, el in enumerate(categories_data):
#     # user = Users.objects.get(id=i % 2 + 1)
#     Categories.objects.create(name=el, user_id=(11 + (i % 2)))
#     print(f"{i} - {el}")
#
# word_pairs = [
#     ('Орел 1', 'REVERSE 1'),
#     ('Орел 2', 'REVERSE 2'),
#     ('Орел 3', 'REVERSE 3'),
#     ('Орел 4', 'REVERSE 4'),
#     ('Орел 5', 'REVERSE 5'),
#     ('Орел 6', 'REVERSE 6'),
#     ('Орел 7', 'REVERSE 7'),
#     ('Орел 8', 'REVERSE 8'),
#     ('Орел 9', 'REVERSE 9'),
#     ('Орел 10', 'REVERSE 10')
# ]
#
# for a, b in word_pairs:
#     Cards.objects.create(side1=a, side2=b, transcription='[ta%$#%$^]', audio=f'audio{a[:4]}.mp3')
#     print(f"{a} - {b}")

# aa = Cards.objects.get(pk=Cards.objects.all().order_by('id').first().id).id
# coun = Cards.objects.count()
#
# print(aa, coun)
# for i in range(aa, aa + coun):
#     cat = Categories.objects.get(pk=i%2 + 17)
#     card = Cards.objects.get(pk=i)
#     Mappings.objects.create(category=cat, card=card)
#     print(f"{i} - {card}  {cat}")


# category = Categories.objects.get(id=1)
# related_cards = category.mappings_set.all()
# related_cards = Cards.objects.filter(mappings__category=1)
# related_mappings = Mappings.objects.filter(category=1)

# related_mappings = Mappings.objects.filter(
#     category_id=1
# ).prefetch_related('card')
# a = related_mappings.values('repetition', 'card__side1', 'card__side2', 'id')
# print(a)

# a = Mappings.objects.filter(category_id=2)
# b = Cards.objects.get(id=2)
# print(b.mappings_set.all())
#
# print(a[0].card)


# filtered_data = Mappings.objects.filter(category_id=2).select_related('card')
# print(repr(filtered_data[0].status))
# # filtered_data[0].update({'status': 1, 'card__side1': 'Птаха 1'})
# filtered_data[0].status = 4
# filtered_data[0].save()
# for i in filtered_data:
#     print(i.status)

# MappingsFormSet = inlineformset_factory(Cards, Mappings, fields=["status", "category", "card__side1"])
# card = Cards.objects.get(id=3)
# formset = MappingsFormSet(instance=card)
# print(formset)


# a = Mappings.objects.filter(category_id=12).select_related('card')
# print(a[0])

# categories = Categories.objects.values('id', 'name')
# boxes = []
# for cat in categories:
#     cat_count = Cards.objects.filter(mappings__category__exact=cat['id']).count()
#     boxes.append({
#         "name": cat['name'],
#         "cat_count": cat_count
#     })
from django.shortcuts import get_object_or_404, redirect

# card = get_object_or_404(Mappings, card_id=112)
# a = Mappings.objects.filter(card_id=112)
# print(card)
# print(a)


# queryset = Mappings.objects.select_related('card')
#
# queryset2 = Mappings.objects.select_related('card').values('id')
#
# queryset3 = Mappings.objects.select_related('card').values(
#         'repetition', 'card__side1', 'card__side2', 'id', 'card__id'
#     ).order_by('repetition')
# # print(queryset2[0].card.side1)

# queryset4 = Categories.objects.select_related('car')

# r = SMTwo.first_review(1)
# for i in range(10):
#     m = randint(2, 5)
#     b = SMTwo(r.easiness, r.interval, r.repetitions).review(m)
#     print(b, f'   Mark {m}')
#     r = b

slug = 'category-2'
# a = Cards.objects.filter(mappings__category__slug=slug).annotate(
#     front_side=Case(
#         When(mappings__front_side=1, then=F('side1')),
#         default=F('side2'),
#         output_field=CharField(),
#     ),
#      back_side=Case(
#         When(mappings__front_side=1, then=F('side2')),
#         default=F('side1'),
#         output_field=CharField(),
#     ),
#
# ).values(
#     'mappings__repetition', 'front_side', 'back_side', 'id', 'mappings', 'mappings__category__name'
# )

# print(a)
deck = get_object_or_404(Categories, slug=slug)
cards = Cards.objects.filter(mappings__isnull=True).delete()
print(len(cards))
print(cards)

        # deck.delete()