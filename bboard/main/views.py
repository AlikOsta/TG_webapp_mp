from django.shortcuts import render


def index(request):
    data = {'title' : 'Главная страница'}
    return render(request, 'main/index.html', data)


def by_rubric(request):
    data = {'title' : 'Рубрики'}
    return render(request, 'main/by_rubric.html', data)


def user(request):
    data = {'title' : 'Пользователь'}
    return render(request, 'main/user.html', data)


def detail(request):
    data = {'title' : 'Детали товара'}
    return render(request, 'main/detail.html', data)


def create(request):
    data = {'title' : 'Новое объявление'}
    return render(request, 'main/create.html', data)
