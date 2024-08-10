
from django.urls import path
from django.conf.urls.static import static

from .views import index, by_rubric, BbCreateView, detail, user, favorites


urlpatterns = [
    path("add/", BbCreateView.as_view(), name="add"),
    path('<int:rubric_pk>/id-<int:pk>', detail, name="detail"),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('', index, name='index'),
    path('user/', user, name='user'),
    path('favorites/', favorites, name='favorites'),

]


