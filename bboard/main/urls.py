from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    index, by_rubric, BbCreateView, detail,
    favorites, user, ChangeUserInfoView,
    profile_bb_delete, profile_bb_change, toggle_favorite
)
from .utils import user_view

urlpatterns = [
    # Главная страница и просмотр рубрик
    path('', index, name='index'),  # главная страница
    path('<int:pk>/', by_rubric, name='by_rubric'),  # просмотр объявлений по рубрике

    # Объявления
    path("add/", BbCreateView.as_view(), name="add"),  # добавление нового объявления
    path('<int:rubric_pk>/id-<int:pk>', detail, name="detail"),  # карточка товара

    # Избранное
    path('favorites/', favorites, name='favorites'),  # избранное для пользователя
    path('favorites/toggle/<int:bb_pk>/', toggle_favorite, name='toggle_favorite'),  # добавление/удаление из избранного

    # Пользовательские маршруты
    path('user/', user, name='user'),  # профиль пользователя
    path('user/change/', ChangeUserInfoView.as_view(), name='user_change'),  # изменение данных пользователя
    path('profile/edit/<int:pk>/', profile_bb_change, name='profile_bb_change'),  # редактирование объявления
    path('profile/delete/<int:pk>/', profile_bb_delete, name='profile_bb_delete'),  # удаление объявления

    # Взаимодействие с Telegram
    path('web-app/', user_view, name='web-app'),  # получение данных от Telegram
]

# Обслуживание медиа-файлов в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
