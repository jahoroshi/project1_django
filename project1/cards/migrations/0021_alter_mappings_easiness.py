# Generated by Django 5.0.4 on 2024-05-11 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0020_rename_params_mappings_review_params_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mappings',
            name='easiness',
            field=models.FloatField(default='0.0'),
        ),
    ]
