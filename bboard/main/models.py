from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser


class Bb(models.Model):
    rubric = models.ForeignKey('Rubric', null=True, on_delete=models.PROTECT, verbose_name='Рубрика')
    title = models.CharField(max_length=30, verbose_name='Товар')
    content = models.TextField(null=True, max_length=150, blank=True, verbose_name='Описание')
    price = models.IntegerField(default=0, null=True, blank=True, verbose_name='Цена')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    def check_expiration(self) :
        if self.published < timezone.now() - timedelta(days=1):
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


# class AdvUser(AbstractUser):
#     pass
#
#     class Meta(AbstractUser.Meta):
#         pass
