from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .models import Bb, Rubric
from .forms import BbForm


def index(request):
    bbs = Bb.objects.all()
    rubrics = Rubric.objects.all()
    data = {
        'title': 'Главная страница',
        'bbs': bbs,
        'rubrics': rubrics,
    }
    return render(request, 'main/index.html', context=data)


def by_rubric(request, pk):
    rubric = get_object_or_404(Rubric, pk=pk)
    bbs = Bb.objects.filter(rubric=pk)

    data = {
        'title': 'Рубрики',
        'bbs': bbs,
        'rubrics': rubric,

    }
    return render(request, 'main/by_rubric.html', context=data)


def user(request):
    data = {'title' : 'Пользователь'}
    return render(request, 'main/user.html', context=data)


def favorites(request):
    data = {'title' : 'favorites'}
    return render(request, 'main/favorites.html', context=data)


def detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)

    context = {'bb': bb,}
    return render(request, 'main/detail.html', context)


class BbCreateView(CreateView):
    template_name = "main/create.html"
    form_class = BbForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context
