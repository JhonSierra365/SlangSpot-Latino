from django.contrib import admin
from .models import Lesson, Expression, Comment, ForumPost, SiteSettings, UserProfile, BlogPost, UserLessonProgress, BlogComment

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'level', 'category', 'created_at')
    list_filter = ('level', 'category', 'created_at')
    search_fields = ('title', 'content')



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'preferred_language', 'created_at')
    list_filter = ('preferred_language', 'created_at')
    search_fields = ('user__username', 'bio', 'learning_goals')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'views', 'created_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'content', 'excerpt', 'author__username')
    list_editable = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'likes', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Contenido', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Publicación', {
            'fields': ('is_published', 'is_active')
        }),
        ('Estadísticas', {
            'fields': ('views', 'likes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class ExpressionAdmin(admin.ModelAdmin):
    list_display = ('text', 'lesson', 'meaning', 'created_at')
    search_fields = ('text', 'meaning', 'lesson__title')
    list_filter = ('lesson',)

class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'video_explicativo_titulo', 'updated_at')
    fieldsets = (
        ('Información General', {
            'fields': ('site_name',)
        }),
        ('Video Explicativo', {
            'fields': ('video_explicativo_url', 'video_explicativo_id', 'video_explicativo_titulo', 'video_explicativo_descripcion'),
            'description': 'Configura el video que explica qué es SlangSpot Latino. El ID del video permite reproducirlo directamente en la página.'
        }),
    )
    
    def has_add_permission(self, request):
        # Solo permitir una configuración
        return not SiteSettings.objects.exists()

admin.site.register(Expression, ExpressionAdmin)
admin.site.register(Comment)
admin.site.register(ForumPost)
admin.site.register(SiteSettings, SiteSettingsAdmin)

@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'completed_at')

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
