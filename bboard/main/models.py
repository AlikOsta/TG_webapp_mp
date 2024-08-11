from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser


class Bb(models.Model):
    rubric = models.ForeignKey('Rubric', null=True, on_delete=models.PROTECT, verbose_name='Рубрика')
    currency = models.ForeignKey('Currency', null=True, on_delete=models.PROTECT, verbose_name='Валюта')
    title = models.CharField(max_length=30, verbose_name='Товар')
    content = models.TextField(max_length=150, blank=True, verbose_name='Описание')
    price = models.IntegerField(default=0, null=True, blank=True, verbose_name='Цена')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    country = models.ForeignKey('Country', null=True, on_delete=models.PROTECT, verbose_name='Страна')
    city = models.ForeignKey('City', null=True, on_delete=models.PROTECT, verbose_name='Город')

    def check_expiration(self):
        if self.published < timezone.now() - timedelta(days=28):
            self.is_active = False
            self.save()

    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Объявления"
        verbose_name = "Объявление"
        ordering = ['-published']


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name="Название")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Рубрики"
        verbose_name = "Рубрика"
        ordering = ['order']


class Currency(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name="Название")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Валюты"
        verbose_name = "Валюта"
        ordering = ['order']


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Название")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Страны"
        verbose_name = "Страна"
        ordering = ['order']


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name="Город")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities', verbose_name="Страна")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')

    def __str__(self):
        return f"{self.name}, {self.country.name}"

    class Meta:
        verbose_name_plural = "Города"
        verbose_name = "Город"
        ordering = ['order']
        unique_together = ['country', 'name']  # Обеспечивает уникальность города в рамках одной страны


class AdditionalImage(models.Model):
    bb = models.ForeignKey('Bb', on_delete=models.CASCADE, related_name='additional_images', verbose_name='Объявление')
    image = models.ImageField(upload_to='images/', verbose_name='Изображение')

    def __str__(self):
        return f"Изображение для {self.bb.title}"

    class Meta:
        verbose_name_plural = "Дополнительные изображения"
        verbose_name = "Дополнительное изображение"



# class AdvUser(AbstractUser):
#     pass
#
#     class Meta(AbstractUser.Meta):
#         pass
