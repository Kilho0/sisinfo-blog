from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PostForm
from .models import Comment, Post


class PostListView(ListView):
    model = Post


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_list'] = self.object.comments.select_related('author')
        context['comment_form'] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post_obj
        return context

    def form_valid(self, form):
        form.instance.post = self.post_obj
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_detail', args=[self.post_obj.pk]) + '#comentarios'
