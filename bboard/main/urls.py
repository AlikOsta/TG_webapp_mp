from bboard import settings
from django.urls import path
from django.conf.urls.static import static

from .views import index, by_rubric, BbCreateView, detail, favorites, user_view


urlpatterns = [
    path("add/", BbCreateView.as_view(), name="add"),
    path('<int:rubric_pk>/id-<int:pk>', detail, name="detail"),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('', index, name='index'),
    path('favorites/', favorites, name='favorites'),
    path('user/', user_view, name='user'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


