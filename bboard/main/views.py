from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Q

from .models import Bb, Rubric, Favorite, CustomUser, AdView
from .forms import BbForm, AiFormSet, ChaserUserInfoForm, SearchForm


def get_favorite_status_for_bbs(user, bbs):
    """Определяет, являются ли объявления избранными для текущего пользователя"""
    favorite_ids = set()
    if user.is_authenticated:
        favorite_ids = set(Favorite.objects.filter(user=user).values_list('bb_id', flat=True))
    for bb in bbs:
        bb.is_favorite = bb.id in favorite_ids


def user(request):
    current_user = request.user
    bbs = Bb.objects.filter(author=current_user).select_related('rubric', 'currency').prefetch_related('additional_images')
    paginator = Paginator(bbs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    rubrics = Rubric.objects.all()

    context = {
        'user': current_user,
        'page_obj': page_obj,
        'rubrics': rubrics,
        'len_bb': bbs.count(),
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/bb_list_ajax.html', context)

    return render(request, 'main/user.html', context)


def index(request):
    bbs = Bb.objects.filter(is_active=True).select_related('rubric', 'currency').prefetch_related('additional_images')
    rubrics = Rubric.objects.all()

    get_favorite_status_for_bbs(request.user, bbs)

    paginator = Paginator(bbs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'rubrics': rubrics,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/bb_list_ajax.html', context)

    return render(request, 'main/index.html', context)


def by_rubric(request, pk):
    rubric = get_object_or_404(Rubric, pk=pk)
    bbs = Bb.objects.filter(rubric=rubric, is_active=True).select_related('rubric', 'currency').prefetch_related('additional_images')

    get_favorite_status_for_bbs(request.user, bbs)
# фильтрация объявлений по выбранному слову
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(content__icontains=keyword) | Q(title__icontains=keyword)
        bbs = Bb.objects.filter(q)
    else:
        keyword = ''

    form = SearchForm(initial={'keyword': keyword})

    paginator = Paginator(bbs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'rubric': rubric,
        'form': form,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/bb_list_ajax.html', context)

    return render(request, 'main/by_rubric.html', context)


def detail(request, rubric_pk, pk):
    bb = get_object_or_404(Bb, pk=pk)
    bb.check_expiration()

    # Проверка уникального просмотра
    if request.user.is_authenticated :
        # Если пользователь авторизован, проверяем по пользователю и объявлению
        viewed, created = AdView.objects.get_or_create(user=request.user, ad=bb)
    else :
        # Если пользователь анонимный, используем session_key
        session_key = request.session.session_key
        if not session_key :
            # Создаем новую сессию, если она не существует
            request.session.create()
            session_key = request.session.session_key

        viewed, created = AdView.objects.get_or_create(session_key=session_key, ad=bb)

    # Если запись о просмотре была создана (то есть, просмотр уникальный), увеличиваем счетчик
    if created :
        bb.views += 1
        bb.save(update_fields=['views'])

    if not bb.is_active:
        return render(request, 'main/404.html', status=404)

    if request.user.is_authenticated:
        bb.is_favorite = Favorite.objects.filter(user=request.user, bb=bb).exists()
    else:
        bb.is_favorite = False

    context = {'bb': bb}
    return render(request, 'main/detail.html', context)


class BbCreateView(LoginRequiredMixin, CreateView):
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


class ChangeUserInfoView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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

    return render(request, 'main/profile_bb_delete.html', {'bb': bb})


def profile_bb_change(request, pk) :
    bb = get_object_or_404(Bb, pk=pk)

    if request.method == 'POST' :
        form = BbForm(request.POST, request.FILES, instance=bb)
        formset = AiFormSet(request.POST, request.FILES, instance=bb)

        if form.is_valid():

            bb = form.save()
            formset.save = AiFormSet(request.POST, request.FILES, instance=bb)

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
        return redirect('login')

    favorite, created = Favorite.objects.get_or_create(user=user, bb=bb)

    if not created:
        favorite.delete()

    return redirect(request.META.get('HTTP_REFERER', 'index'))


def favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('bb__rubric', 'bb__currency')

    # Формирование списка избранных объявлений с дополнительной информацией
    favorite_list = []

    for favorite in favorites:
        favorite_list.append({
            'bb': favorite.bb,
            'is_favorite': True  # Поскольку это избранное, is_favorite всегда будет True
        })

    context = {
        'favorite_list': favorite_list
    }
    return render(request, 'main/favorites.html', context)


def seller_list_bb(request, seller_id):
    seller = get_object_or_404(CustomUser, telegram_id=seller_id)
    listings = Bb.objects.filter(author=seller, is_active=True).select_related('rubric', 'currency').prefetch_related('additional_images')

    context = {
        'seller': seller,
        'listings': listings,
    }
    return render(request, 'main/user_listings.html', context)