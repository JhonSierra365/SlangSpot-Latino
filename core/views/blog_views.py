from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from ..models import BlogPost

class BlogListView(ListView):
    model = BlogPost
    template_name = 'core/blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True, is_active=True)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogPost.CATEGORY_CHOICES
        return context

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'core/blog/blog_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Incrementar vistas
        self.object.views += 1
        self.object.save()
        
        # Posts relacionados
        related_posts = BlogPost.objects.filter(
            category=self.object.category,
            is_published=True,
            is_active=True
        ).exclude(id=self.object.id)[:3]
        
        context['related_posts'] = related_posts
        return context

class BlogCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    template_name = 'core/blog/blog_form.html'
    fields = ['title', 'content', 'excerpt', 'category', 'featured_image', 'is_published']
    success_url = reverse_lazy('core:blog_list')
    login_url = reverse_lazy('core:login')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Artículo creado exitosamente.')
        return super().form_valid(form)

class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = BlogPost
    template_name = 'core/blog/blog_form.html'
    fields = ['title', 'content', 'excerpt', 'category', 'featured_image', 'is_published']
    login_url = reverse_lazy('core:login')

    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Artículo actualizado exitosamente.')
        return super().form_valid(form)

class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = BlogPost
    template_name = 'core/blog/blog_confirm_delete.html'
    success_url = reverse_lazy('core:blog_list')
    login_url = reverse_lazy('core:login')

    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Artículo eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

@login_required
@require_POST
def blog_like(request, slug):
    """Vista para dar like a un post del blog"""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count()
    }) 