from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.cache import cache_page
import jwt
from django.conf import settings
from .models import Profile, Bb, Rubric
from .forms import BbForm


def user_view(request):

    token = request.GET.get("token")

    try:
        # Декодируем токен
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

        username = payload.get('username')
        user_id = payload.get('user_id')

        return render(request, 'main/user.html', {"user_id": user_id, "username": username})

    except jwt.ExpiredSignatureError:
        return render(request, 'main/invalid_signature.html')

    except jwt.InvalidTokenError:
        return render(request, 'main/invalid_signature.html')


@cache_page(60 * 60)
def index(request):
    bbs = Bb.objects.all()
    for bb in bbs:
        bb.check_expiration()
    bbs = Bb.objects.filter(is_active=True)
    paginator = Paginator(bbs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    rubrics = Rubric.objects.all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/bb_list_ajax.html', {'page_obj': page_obj})

    data = {
        'page_obj': page_obj,
        'rubrics': rubrics,
    }
    return render(request, 'main/index.html', context=data)


@cache_page(60 * 60)
def by_rubric(request, pk):
    rubric = get_object_or_404(Rubric, pk=pk)
    bbs = Bb.objects.filter(rubric=pk)

    for bb in bbs:
        bb.check_expiration()

    bbs = bbs.filter(is_active=True)

    paginator = Paginator(bbs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/bb_list_ajax.html', {'page_obj': page_obj})

    data = {
        'page_obj': page_obj,
        'rubric': rubric,
    }
    return render(request, 'main/by_rubric.html', context=data)


def favorites(request):
    data = {'title': 'favorites'}
    return render(request, 'main/favorites.html', context=data)


def detail(request, rubric_pk, pk):
    bb = get_object_or_404(Bb, pk=pk)
    bb.check_expiration()
    if not bb.is_active:
        return render(request, 'main/404.html', status=404)
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
            return redirect('index')
    else:
        form = BbForm()
    return render(request, 'create.html', {'form': form})
