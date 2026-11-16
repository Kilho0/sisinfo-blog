from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import AccessForm, ProfileForm, SignupForm
from .models import ROLE_CHOICES, Profile, role_of, set_role

User = get_user_model()


class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'registration/signup.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile_detail', username=request.user.username)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Conta criada. Bem-vindo, {user.first_name or user.username}!')
        return redirect('profile_edit')


class MyProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return redirect('profile_detail', username=request.user.username)


class ProfileDetailView(DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile_user'
    template_name = 'contas/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context['profile'] = Profile.for_user(user)
        context['role'] = dict(ROLE_CHOICES)[role_of(user)]
        context['is_owner'] = self.request.user == user
        context['user_posts'] = user.posts.prefetch_related('categories')
        context['user_comments'] = user.comments.select_related('post')
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'contas/profile_form.html'

    def get_object(self, queryset=None):
        return Profile.for_user(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile_detail', args=[self.request.user.username])


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class AccessListView(SuperuserRequiredMixin, ListView):
    template_name = 'contas/access_list.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        users = User.objects.order_by('-is_superuser', '-is_staff', 'username')
        query = self.request.GET.get('q', '').strip()
        if query:
            users = users.filter(
                Q(username__icontains=query) | Q(first_name__icontains=query)
                | Q(last_name__icontains=query) | Q(email__icontains=query)
            )
        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        context['role_choices'] = ROLE_CHOICES
        for user in context['user_list']:
            user.role = role_of(user)
        return context


class AccessUpdateView(SuperuserRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        back = reverse_lazy('access_list')
        if user == request.user:
            messages.error(request, 'Você não pode mudar o próprio acesso. Peça para outro superadmin.')
            return redirect(back)

        form = AccessForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Nível de acesso inválido.')
            return redirect(back)

        set_role(user, form.cleaned_data['role'])
        user.is_active = form.cleaned_data['is_active']
        user.save(update_fields=['is_active'])
        role = dict(ROLE_CHOICES)[form.cleaned_data['role']]
        status = '' if user.is_active else ' (conta desativada)'
        messages.success(request, f'{user.username} agora é {role}{status}.')
        return redirect(back)
