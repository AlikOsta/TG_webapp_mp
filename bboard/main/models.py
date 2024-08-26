from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.db.models import Avg
import os

# Модель для хранения рейтингов пользователей
class Rating(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings_received',
        verbose_name='Продавец'
    )
    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings_given',
        verbose_name='Оценивающий'
    )
    score = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seller', 'rater')  # Ограничение на единственную оценку от одного пользователя
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    def __str__(self):
        return f"Рейтинг {self.score} для {self.seller.username} от {self.rater.username}"


# Менеджер пользователя с дополнительными методами создания суперпользователей и пользователей
class CustomUserManager(BaseUserManager):
    def create_superuser(self, telegram_id, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(telegram_id, username, password, **extra_fields)

    def create_user(self, telegram_id, username, password=None, **extra_fields):
        if not telegram_id:
            raise ValueError('The Telegram ID must be set')

        user = self.model(
            telegram_id=telegram_id,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


# Модель пользовательского класса с дополнительными полями
class CustomUser(AbstractUser):
    telegram_id = models.CharField(max_length=12, unique=True, verbose_name='telegram id')
    username = models.CharField(default="Пользователь", max_length=30, verbose_name='имя пользователя')
    tg_name = models.CharField(default="@telegram", max_length=30, verbose_name='telegram имя')
    image = models.ImageField(
        upload_to='images/user',
        default='static/main/no_photo_user.png',
        verbose_name='Фото профиля'
    )

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def get_average_rating(self):
        # Оптимизация агрегатного запроса для вычисления среднего рейтинга
        return self.ratings_received.aggregate(average=Avg('score'))['average'] or 0

    def __str__(self):
        return self.username


# Модель объявления
class Bb(models.Model):
    rubric = models.ForeignKey('Rubric', null=True, on_delete=models.PROTECT, verbose_name='Рубрика')
    currency = models.ForeignKey('Currency', null=True, on_delete=models.PROTECT, verbose_name='Валюта')
    title = models.CharField(max_length=30, verbose_name='Товар')
    content = models.TextField(max_length=150, blank=True, verbose_name='Описание')
    price = models.IntegerField(default=0, null=True, blank=True, verbose_name='Цена')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    city = models.ForeignKey('SubLocation', null=True, on_delete=models.PROTECT, verbose_name='Город')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')

    def check_expiration(self):
        """Деактивация объявления, если оно просрочено"""
        if self.published < timezone.now() - timedelta(days=28):
            self.is_active = False
            self.save(update_fields=['is_active'])

    def delete(self, *args, **kwargs) :
        for ai in self.additional_images.all() :  # Используем related_name, если он есть
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Объявления"
        verbose_name = "Объявление"
        ordering = ['-published']


# Модель для рубрик
class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name="Название")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Рубрики"
        verbose_name = "Рубрика"
        ordering = ['order']


# Модель для валют
class Currency(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name="Название")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Валюты"
        verbose_name = "Валюта"
        ordering = ['order']


# Модель дополнительных изображений для объявления
class AdditionalImage(models.Model):
    bb = models.ForeignKey(Bb, related_name='additional_images', on_delete=models.CASCADE, verbose_name='Объявления')
    image = models.ImageField(upload_to='images/', verbose_name='Изображение')

    def __str__(self):
        return f"Изображение для {self.bb.title}"

    def delete(self, *args, **kwargs) :
        if self.image and os.path.isfile(self.image.path) :
            os.remove(self.image.path)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Дополнительные изображения"
        verbose_name = "Дополнительное изображение"


# Базовая модель локации
class Location(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name="Название")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name="Порядок")
    super_location = models.ForeignKey("SuperLocation", on_delete=models.PROTECT, null=True, blank=True, verbose_name="Страна")


# Менеджер для фильтрации супергородов (стран)
class SuperLocationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_location__isnull=True)


# Прокси-модель для супергородов (стран)
class SuperLocation(Location):
    objects = SuperLocationManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'


# Менеджер для фильтрации подгородов
class SubLocationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_location__isnull=False)


# Прокси-модель для подгородов
class SubLocation(Location):
    objects = SubLocationManager()

    def __str__(self):
        return '%s, %s' % (self.super_location.name, self.name)

    class Meta:
        proxy = True
        ordering = ('super_location__order', 'super_location__name', 'order', 'name')
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


# Модель избранного
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    bb = models.ForeignKey('Bb', on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'bb')
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self):
        return f"{self.user.username} добавил {self.bb.title} в избранное"
