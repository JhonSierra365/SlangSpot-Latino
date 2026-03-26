from django.urls import path
from .views import (
    # Auth views
    home,
    notifications_view, mark_notification_read,
    mark_all_notifications_read,
    sobre_nosotros, politica_privacidad, terminos_uso,
    
    # Forum views
    ForumPostListView,
    ForumPostCreateView, ForumPostUpdateView,
    ForumPostDeleteView, post_detail_view,
    like_post, moderate_delete_post,
    
    # Lesson views
    LessonListView, LessonDetailView,
    LessonCreateView, LessonUpdateView,
    LessonDeleteView, ExpressionCreateView,
    ExpressionUpdateView, ExpressionDeleteView,
    complete_lesson,
    
    # Chat views
    chat, get_chat_history, send_message, get_ai_response,
    
    # Profile views
    ProfileView, ProfileUpdateView,
    

    # Blog views
    BlogListView, BlogDetailView, BlogCreateView,
    BlogUpdateView, BlogDeleteView, blog_like,
    add_blog_comment, like_blog_comment, moderate_blog_comment
)

app_name = 'core'

urlpatterns = [
    # Auth URLs
    path('', home, name='home'),
    
    # Static Pages
    path('sobre-nosotros/', sobre_nosotros, name='sobre_nosotros'),
    path('politica-privacidad/', politica_privacidad, name='politica_privacidad'),
    path('terminos-uso/', terminos_uso, name='terminos_uso'),
    
    # Notifications routes
    path('notifications/', notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),
    # Forum URLs
    path('forum/', ForumPostListView.as_view(), name='forum_index'),
    path('forum/post/<int:post_id>/', post_detail_view, name='post_detail'),
    path('forum/post/<int:pk>/moderate-delete/', moderate_delete_post, name='moderate_delete_post'),
    path('forum/post/create/', ForumPostCreateView.as_view(), name='create_post'),
    path('forum/post/<int:post_id>/edit/', ForumPostUpdateView.as_view(), name='edit_post'),
    path('forum/post/<int:post_id>/delete/', ForumPostDeleteView.as_view(), name='delete_post'),
    path('forum/post/<int:post_id>/like/', like_post, name='like_post'),
    
    # Lesson URLs
    path('lessons/', LessonListView.as_view(), name='lesson_list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/<int:pk>/complete/', complete_lesson, name='complete_lesson'),
    path('lessons/create/', LessonCreateView.as_view(), name='create_lesson'),
    path('lessons/<int:pk>/edit/', LessonUpdateView.as_view(), name='edit_lesson'),
    path('lessons/<int:pk>/delete/', LessonDeleteView.as_view(), name='delete_lesson'),
    path('lessons/<int:lesson_id>/expressions/create/', ExpressionCreateView.as_view(), name='create_expression'),
    path('expressions/<int:pk>/edit/', ExpressionUpdateView.as_view(), name='edit_expression'),
    path('expressions/<int:pk>/delete/', ExpressionDeleteView.as_view(), name='delete_expression'),
    
    # Chat URLs
    path('chat/', chat, name='chat'),
    path('api/chat/history/', get_chat_history, name='chat_history'),
    path('api/chat/send/', send_message, name='send_message'),
    path('api/chat/response/', get_ai_response, name='get_ai_response'),
    
    # Profile URLs
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    

    # Blog URLs
    path('blog/', BlogListView.as_view(), name='blog_list'),
    path('blog/create/', BlogCreateView.as_view(), name='blog_create'),
    path('blog/<int:pk>/edit/', BlogUpdateView.as_view(), name='blog_edit'),
    path('blog/<int:pk>/delete/', BlogDeleteView.as_view(), name='blog_delete'),
    path('blog/<slug:slug>/like/', blog_like, name='blog_like'),
    path('blog/<int:pk>/comment/', add_blog_comment, name='add_blog_comment'),
    path('blog/comment/<int:pk>/like/', like_blog_comment, name='like_blog_comment'),
    path('blog/comment/<int:pk>/moderate/', moderate_blog_comment, name='moderate_blog_comment'),
    path('blog/<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
] 