import os
from django.conf import settings
import tempfile
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth.models import User
from .models import ForumPost, Comment, UserProfile

# Importaciones condicionales para ElevenLabs - Comentado ya que no se usa
# try:
#     from elevenlabs import generate, save, set_api_key
#     ELEVENLABS_AVAILABLE = True
# except ImportError:
#     ELEVENLABS_AVAILABLE = False
#     print("Warning: ElevenLabs no está disponible. La generación de audio no funcionará.")

def generate_audio(text, filename):
    """
    Genera un archivo de audio usando ElevenLabs API - Comentado ya que no se usa
    """
    # if not ELEVENLABS_AVAILABLE:
    #     print("Error: ElevenLabs no está disponible")
    #     return False
    
    # if not settings.ELEVENLABS_API_KEY:
    #     print("Error: ELEVENLABS_API_KEY no está configurada")
    #     return False
    
    # try:
    #     # Configurar la API key
    #     set_api_key(settings.ELEVENLABS_API_KEY)
        
    #     # Generar el audio
    #     audio = generate(
    #         text=text,
    #         voice="Josh",  # Voz en inglés
    #         model="eleven_monolingual_v1"
    #     )
        
    #     # Crear el directorio si no existe
    #     os.makedirs(os.path.dirname(filename), exist_ok=True)
        
    #     # Guardar el audio
    #     save(audio, filename)
        
    #     return True
    # except Exception as e:
    #     print(f"Error generando audio: {str(e)}")
    #     return False
    
    # Por ahora retorna False ya que ElevenLabs no está implementado
    return False

def create_notification(user, message):
    """
    Crea una notificación y la envía en tiempo real al usuario
    TODO: Implementar cuando se cree el modelo Notification
    """
    # TODO: Implementar cuando se cree el modelo Notification
    print(f"Notificación para {user.username}: {message}")
    
    # Enviar notificación en tiempo real (comentado hasta implementar Notification y WebSockets)
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     f"user_{user.id}_notifications",
    #     {
    #         "type": "send_notification",
    #         "message": message,
    #         "notification_id": notification.id,
    #         "notification_type": notification_type,
    #         "data": {
    #             "post_id": related_post.id if related_post else None,
    #             "comment_id": related_comment.id if related_comment else None,
    #             "user_id": related_user.id if related_user else None,
    #         }
    #     }
    # )
    
    # return notification
    return None

def notify_post_like(post, user):
    """
    Notifica al autor de un post cuando recibe un like
    """
    if post.author != user:  # No notificar si el usuario se da like a sí mismo
        message = f"{user.username} dio me gusta a tu publicación '{post.title}'"
        create_notification(
            user=post.author,
            message=message
        )

def notify_comment_like(comment, user):
    """
    Notifica al autor de un comentario cuando recibe un like
    """
    if comment.author != user:  # No notificar si el usuario se da like a sí mismo
        message = f"{user.username} dio me gusta a tu comentario"
        create_notification(
            user=comment.author,
            message=message
        )

def notify_new_comment(post, comment, user):
    """
    Notifica al autor de un post cuando recibe un nuevo comentario
    """
    if post.author != user:  # No notificar si el autor comenta su propio post
        message = f"{user.username} comentó en tu publicación '{post.title}'"
        create_notification(
            user=post.author,
            message=message
        )

def notify_mention(user, mentioned_user, post=None, comment=None):
    """
    Notifica a un usuario cuando es mencionado
    """
    if user != mentioned_user:  # No notificar si el usuario se menciona a sí mismo
        context = "en un comentario" if comment else "en una publicación"
        message = f"{user.username} te mencionó {context}"
        create_notification(
            user=mentioned_user,
            message=message
        )

def notify_moderation(user, action, post=None, comment=None):
    """
    Notifica a un usuario sobre acciones de moderación
    """
    message = f"Tu {action} ha sido moderado"
    create_notification(
        user=user,
        message=message
    )

def get_recent_activity(user, days=7):
    """Obtiene la actividad reciente de un usuario"""
    start_date = timezone.now() - timezone.timedelta(days=days)
    
    posts = ForumPost.objects.filter(
        author=user,
        created_at__gte=start_date
    ).order_by('-created_at')
    
    comments = Comment.objects.filter(
        author=user,
        created_at__gte=start_date
    ).order_by('-created_at')
    
    return {
        'posts': posts,
        'comments': comments
    }

def get_user_stats(user):
    """Obtiene estadísticas del usuario"""
    return {
        'posts_count': ForumPost.objects.filter(author=user).count(),
        'comments_count': Comment.objects.filter(author=user).count(),
        'likes_received': ForumPost.objects.filter(author=user).aggregate(
            total_likes=Count('likes')
        )['total_likes'] or 0
    }

def search_posts(query):
    """Busca posts por título o contenido"""
    return ForumPost.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    ).order_by('-created_at')

def get_popular_posts(days=30):
    """Obtiene los posts más populares"""
    start_date = timezone.now() - timezone.timedelta(days=days)
    return ForumPost.objects.filter(
        created_at__gte=start_date
    ).annotate(
        popularity=Count('likes') + Count('comments')
    ).order_by('-popularity')[:10]

def get_user_reputation(user):
    """Calcula la reputación del usuario"""
    profile = UserProfile.objects.get_or_create(user=user)[0]
    return profile.reputation


def extract_youtube_video_id(url):
    """
    Extrae el ID del video de YouTube de una URL.

    Retorna:
        str or None: ID del video o None si no se encuentra.
    """
    import re

    if not url:
        return None

    regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(regex, url)
    
    if match:
        return match.group(1)

    return None


def get_youtube_thumbnail_url(video_url):
    """
    Obtiene la URL de la miniatura del video de YouTube con cache.

    Retorna:
        str or None: URL de la miniatura o None si no hay video_url válido.
    """
    from django.core.cache import cache

    if not video_url:
        return None

    # Usar cache para evitar recalcular la URL frecuentemente
    cache_key = f'youtube_thumbnail:{video_url}'
    cached_url = cache.get(cache_key)

    if cached_url is not None:
        return cached_url

    # Si no está en cache, calcular y cachear
    video_id = extract_youtube_video_id(video_url)
    if video_id:
        thumbnail_url = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
        # Cachear por 24 horas
        cache.set(cache_key, thumbnail_url, 86400)
        return thumbnail_url

    # Cachear None por 1 hora para URLs inválidas
    cache.set(cache_key, None, 3600)
    return None