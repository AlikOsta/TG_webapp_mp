from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .models import Bb, Rubric
from .forms import BbForm


def index(request) :
    bbs = Bb.objects.all()

    for bb in bbs :
        bb.check_expiration()
    bbs = Bb.objects.filter(is_active=True)

    paginator = Paginator(bbs, 40)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    rubrics = Rubric.objects.all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/bb_list_ajax.html', {'page_obj' : page_obj})

    data = {
        'page_obj': page_obj,
        'bbs': bbs,
        'rubrics' : rubrics,
    }

    return render(request, 'main/index.html', context=data)


def by_rubric(request, pk) :
    rubric = get_object_or_404(Rubric, pk=pk)
    bbs = Bb.objects.filter(rubric=pk)
    for bb in bbs :
        bb.check_expiration()
    bbs = bbs.filter(is_active=True)

    data = {
        'bbs' : bbs,
        'rubric' : rubric,
    }
    return render(request, 'main/by_rubric.html', context=data)


def user(request):
    data = {'title' : 'Пользователь'}
    return render(request, 'main/user.html', context=data)


def favorites(request):
    data = {'title' : 'favorites'}
    return render(request, 'main/favorites.html', context=data)


def detail(request, rubric_pk, pk):
    bb = get_object_or_404(Bb, pk=pk)
    bb.check_expiration()
    if not bb.is_active:
        return render(request, 'main/404.html', status=404)  # Или другой шаблон для неактивных объявлений
    context = {'bb': bb}
    return render(request, 'main/detail.html', context)

class BbCreateView(CreateView):
    template_name = "main/create.html"
    form_class = BbForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context


def create_bb(request):
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = BbForm()
    return render(request, 'create.html', {'form': form})


