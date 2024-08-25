from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ChaserUserInfoForm
from django.contrib import messages

from django.http import HttpResponseRedirect
from django.views.decorators.cache import cache_page

from django.conf import settings

from .models import Bb, Rubric, CustomUser, Favorite
from .forms import BbForm, AiFormSet
from .utils import user_view



def user(request) :
    current_user = request.user
    # all_users = CustomUser.objects.all()

    bbs = Bb.objects.filter(author=request.user)
    paginator = Paginator(bbs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    rubrics = Rubric.objects.all()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/bb_list_ajax.html', {'page_obj': page_obj})

    len_bb = len(bbs)

    context={
        'user' : current_user,
        'page_obj': page_obj,
        'rubrics': rubrics,
        'len_bb': len_bb,
    }

    return render(request, 'main/user.html', context)


def index(request):
    bbs = Bb.objects.all()
    for bb in bbs:
        bb.check_expiration()

    bbs = Bb.objects.filter(is_active=True)
    rubrics = Rubric.objects.all()

    # Определяем избранные объявления для текущего пользователя
    if request.user.is_authenticated:
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('bb_id', flat=True)
        for bb in bbs:
            bb.is_favorite = bb.id in favorite_ids
    else:
        for bb in bbs:
            bb.is_favorite = False

    paginator = Paginator(bbs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/bb_list_ajax.html', {'page_obj': page_obj})

    context = {
        'page_obj': page_obj,
        'rubrics': rubrics,
    }

    return render(request, 'main/index.html', context)


def by_rubric(request, pk):
    rubric = get_object_or_404(Rubric, pk=pk)
    bbs = Bb.objects.filter(rubric=pk)

    for bb in bbs:
        bb.check_expiration()

    bbs = bbs.filter(is_active=True)

    # Определяем избранные объявления для текущего пользователя
    if request.user.is_authenticated:
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('bb_id', flat=True)
        for bb in bbs:
            bb.is_favorite = bb.id in favorite_ids
    else:
        for bb in bbs:
            bb.is_favorite = False

    paginator = Paginator(bbs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/bb_list_ajax.html', {'page_obj': page_obj})

    context = {
        'page_obj': page_obj,
        'rubric': rubric,
    }
    return render(request, 'main/by_rubric.html', context)

def detail(request, rubric_pk, pk):
    bb = get_object_or_404(Bb, pk=pk)
    bb.check_expiration()

    if not bb.is_active:
        return render(request, 'main/404.html', status=404)

    # Проверка, является ли объявление избранным для текущего пользователя
    if request.user.is_authenticated:
        bb.is_favorite = Favorite.objects.filter(user=request.user, bb=bb).exists()
    else:
        bb.is_favorite = False

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

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


def create_bb(request):
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = BbForm()
    return render(request, 'create.html', {'form': form})


class ChangeUserInfoView(SuccessMessageMixin, UpdateView):
    model = CustomUser
    template_name = 'main/change_user_info.html'
    form_class = ChaserUserInfoForm
    success_url = reverse_lazy('user')
    success_message = 'Данные изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


def profile_bb_delete(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if bb.author != request.user:
        return redirect('user')
    if request.method == 'POST':
        bb.delete()
        return redirect('user')
    return render(request, {'bb': bb})


def profile_bb_change(request, pk) :
    bb = get_object_or_404(Bb, pk=pk)

    if request.method == 'POST' :
        form = BbForm(request.POST, request.FILES, instance=bb)
        formset = AiFormSet(request.POST, request.FILES, instance=bb)

        if form.is_valid():

            bb = form.save()
            formset.save = AiFormSet(request.POST, request.FILES, instance=bb)

            messages.add_message(request, messages.SUCCESS, "Объявление исправлено")
            return redirect('user')
    else:
        form = BbForm(instance=bb)
        formset = AiFormSet(instance=bb)
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'main/profile_bb_change.html', context)


def toggle_favorite(request, bb_pk):
    bb = get_object_or_404(Bb, pk=bb_pk)
    user = request.user

    if not user.is_authenticated:
        return redirect('login')  # Перенаправляем на страницу входа, если пользователь не авторизован

    favorite, created = Favorite.objects.get_or_create(user=user, bb=bb)

    if not created:
        favorite.delete()  # Удаляем из избранного, если оно уже существует

    return redirect(request.META.get('HTTP_REFERER', 'index'))

def favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'main/favorites.html', {'favorites': favorites})