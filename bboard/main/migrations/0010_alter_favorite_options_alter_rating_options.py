# Generated by Django 5.1 on 2024-08-25 11:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_alter_favorite_bb_alter_favorite_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранные'},
        ),
        migrations.AlterModelOptions(
            name='rating',
            options={'verbose_name': 'Рейтинг', 'verbose_name_plural': 'Рейтинги'},
        ),
    ]
