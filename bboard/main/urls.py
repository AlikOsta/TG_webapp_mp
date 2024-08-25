from bboard import settings
from django.urls import path
from django.conf.urls.static import static

from .views import index, by_rubric, BbCreateView, detail, favorites, user, ChangeUserInfoView, profile_bb_delete, profile_bb_change, toggle_favorite
from .utils import user_view


urlpatterns = [
    path("add/", BbCreateView.as_view(), name="add"), # добавляем новое объявление
    path('<int:rubric_pk>/id-<int:pk>', detail, name="detail"), # карточка товара
    path('<int:pk>/', by_rubric, name='by_rubric'), # рубрики
    path('', index, name='index'), # главная страница
    path('favorites/', favorites, name='favorites'), # избранное для пользователя
    path('favorites/toggle/<int:bb_pk>/', toggle_favorite, name='toggle_favorite'),
    path('web-app/', user_view, name='web-app'), # для получения данных от тг
    path('user/change/', ChangeUserInfoView.as_view(), name='user_change'),
    path('user/', user, name='user'), # пользователь
    path('profile/edit/<int:pk>/', profile_bb_change, name='profile_bb_change'),
    path('profile/delete/<int:pk>/', profile_bb_delete, name='profile_bb_delete'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


