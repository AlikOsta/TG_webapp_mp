from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.conf import settings
from django.db.models import Avg


class Rating(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_received', verbose_name='Продавец')
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_given', verbose_name='Оценивающий')
    score = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seller', 'rater') # проверяем что бы только 1 раз можно было оценить

    def __str__(self):
        return f"Рейтинг {self.score} для {self.seller.username} от {self.rater.username}"


class CustomUserManager(BaseUserManager):
    def create_superuser(self, telegram_id, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(telegram_id, username, password, **extra_fields)

    def create_user(self, telegram_id, username, password=None, **extra_fields):
        if not telegram_id:
            raise ValueError('The Telegram ID must be set')
        user = self.model(telegram_id=telegram_id, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    telegram_id = models.CharField(max_length=12, unique=True, verbose_name='telegram id')
    username = models.CharField(default="Пользователь", max_length=30, verbose_name='имя пользователя')
    tg_name = models.CharField(default="@telegram", max_length=30, verbose_name='telegram имя')
    image = models.ImageField(upload_to='images/user', default='static/main/no_photo_user.png',  verbose_name='Фото профиля')

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def get_average_rating(self):
        ratings = self.ratings_received.all()
        avg_rating = ratings.aggregate(Avg('score'))['score__avg']
        return avg_rating if avg_rating else 0

    def __str__(self):
        return self.username

class Bb(models.Model):
    rubric = models.ForeignKey('Rubric', null=True, on_delete=models.PROTECT, verbose_name='Рубрика')
    currency = models.ForeignKey('Currency', null=True, on_delete=models.PROTECT, verbose_name='Валюта')
    title = models.CharField(max_length=30, verbose_name='Товар')
    content = models.TextField(max_length=150, blank=True, verbose_name='Описание')
    price = models.IntegerField(default=0, null=True, blank=True, verbose_name='Цена')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    city = models.ForeignKey('SubLocation', null=True, on_delete=models.PROTECT, verbose_name='Город')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,  verbose_name='Автор')

    def check_expiration(self):
        if self.published < timezone.now() - timedelta(days=28):
            self.is_active = False
            self.save()

    def delete(self, *args, **kwargs) :
        for ai in self.additional_images.all() :
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


class AdditionalImage(models.Model):
    bb = models.ForeignKey(Bb, related_name='additional_images', on_delete=models.CASCADE, verbose_name='Объявления')
    image = models.ImageField(upload_to='images/', verbose_name='Изображение')

    def __str__(self):
        return f"Изображение для {self.bb.title}"

    class Meta:
        verbose_name_plural = "Дополнительные изображения"
        verbose_name = "Дополнительное изображение"


class Location(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name="Название")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name="Порядок")
    super_location = models.ForeignKey("SuperLocation", on_delete=models.PROTECT, null=True, blank=True, verbose_name="Страна")


class SuperLocationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_location__isnull=True)


class SuperLocation(Location):
    objects = SuperLocationManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'


class SubLocationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_location__isnull=False)


class SubLocation(Location):
    objects = SubLocationManager()

    def __str__(self):
        return '%s, %s' % (self.super_location.name, self.name)

    class Meta:
        proxy = True
        ordering = ('super_location__order', 'super_location__name', 'order', 'name')
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
