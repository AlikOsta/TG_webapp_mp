from django.shortcuts import render, get_object_or_404
from .models import Bb, Rubric


def index(request):
    bbs = "Bb.objects.all()"
    rubrics = "Rubric.objects.all()"
    data = {
        'title': 'Главная страница',
        'bbs': bbs,
        'rubrics': rubrics,
    }
    return render(request, 'main/index.html', context=data)


def by_rubric(request):
    rubric = "get_object_or_404(Rubric, pk=pk)"
    bbs = "Bb.objects.filter(rubric=pk)"
    data = {
        'title': 'Рубрики',
        'bbs': bbs,
        'rubrics': rubric,
    }
    return render(request, 'main/by_rubric.html', context=data)


def user(request):
    data = {'title' : 'Пользователь'}
    return render(request, 'main/user.html', context=data)


def detail(request):
    data = {'title' : 'Детали товара'}
    return render(request, 'main/detail.html', context=data)


def create(request):
    data = {'title' : 'Новое объявление'}
    return render(request, 'main/create.html', context=data)
