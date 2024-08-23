from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ChaserUserInfoForm

from django.http import HttpResponseRedirect
from django.views.decorators.cache import cache_page

from django.conf import settings

from .models import Bb, Rubric, CustomUser
from .forms import BbForm
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

    print(len_bb)

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
    paginator = Paginator(bbs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    rubrics = Rubric.objects.all()

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
