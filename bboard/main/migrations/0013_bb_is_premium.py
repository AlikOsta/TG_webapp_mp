# Generated by Django 5.1 on 2024-08-28 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_adview'),
    ]

    operations = [
        migrations.AddField(
            model_name='bb',
            name='is_premium',
            field=models.BooleanField(default=False),
        ),
    ]
