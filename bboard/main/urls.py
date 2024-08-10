
from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('user/', views.user, name='user'),
    path('create/', views.create, name='create'),
    path('detail/', views.detail, name='detail'),
    path('rubric/', views.by_rubric, name='by_rubric'),

]
