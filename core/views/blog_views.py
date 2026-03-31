from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from ..models import BlogPost, BlogComment
from ..forms import BlogPostForm

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
        
        # Comentarios
        context['comments'] = self.object.comments.filter(is_approved=True).select_related('author')
        if self.request.user.is_authenticated and self.request.user.is_staff:
            context['pending_comments'] = self.object.comments.filter(is_approved=False).select_related('author')
            
        return context

class BlogCreateView(UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.is_staff

    model = BlogPost
    template_name = 'core/blog/blog_form.html'
    form_class = BlogPostForm
    success_url = reverse_lazy('core:blog_list')
    login_url = reverse_lazy('account_login')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Artículo creado exitosamente.')
        return super().form_valid(form)

class BlogUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_staff

    model = BlogPost
    template_name = 'core/blog/blog_form.html'
    form_class = BlogPostForm
    login_url = reverse_lazy('account_login')

    def get_queryset(self):
        # Any staff member can edit any blog post
        return BlogPost.objects.all()

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'Artículo actualizado exitosamente.')
        return super().form_valid(form)

class BlogDeleteView(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_staff

    model = BlogPost
    template_name = 'core/blog/blog_confirm_delete.html'
    success_url = reverse_lazy('core:blog_list')
    login_url = reverse_lazy('account_login')

    def get_queryset(self):
        # Any staff member can delete any blog post
        return BlogPost.objects.all()

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

@login_required
@require_POST
def add_blog_comment(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, is_published=True)
    content = request.POST.get('content', '').strip()
    
    if content:
        is_approved = BlogComment.objects.filter(author=request.user, is_approved=True).exists()
        BlogComment.objects.create(
            post=post,
            author=request.user,
            content=content[:1000],
            is_approved=is_approved
        )
        if is_approved:
            messages.success(request, 'Tu comentario ha sido publicado.')
        else:
            messages.info(request, 'Tu comentario ha sido enviado y está pendiente de aprobación.')
            
    return redirect('core:blog_detail', slug=post.slug)

@login_required
@require_POST
def like_blog_comment(request, pk):
    comment = get_object_or_404(BlogComment, pk=pk)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
        
    return JsonResponse({
        'liked': liked,
        'total_likes': comment.total_likes()
    })

@login_required
@require_POST
def moderate_blog_comment(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied("No tienes permisos para moderar comentarios.")
        
    comment = get_object_or_404(BlogComment, pk=pk)
    action = request.POST.get('action')
    post_slug = comment.post.slug
    
    if action == 'approve':
        comment.is_approved = True
        comment.save()
        messages.success(request, 'Comentario aprobado exitosamente.')
    elif action == 'delete':
        comment.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
        
    return redirect('core:blog_detail', slug=post_slug) 