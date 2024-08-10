

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rubric/', views.by_rubric, name='by_rubric'),
    path('user/', views.user, name='user'),
    path('detail/', views.detail, name='detail'),
    path('create/', views.create, name='create'),
]
