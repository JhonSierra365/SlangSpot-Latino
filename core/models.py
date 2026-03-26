from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from .validators import validate_file_size, validate_image_extension, validate_audio_extension, validate_youtube_url
import uuid
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from urllib.parse import urlparse, parse_qs
import re
import bleach

# Create your models here.

class BaseModel(models.Model):
    """
    Modelo base abstracto que proporciona campos comunes para soft delete y timestamps.

    Atributos:
        id (AutoField): Identificador único del registro.
        created_at (DateTimeField): Fecha y hora de creación del registro.
        updated_at (DateTimeField): Fecha y hora de última actualización.
        is_active (BooleanField): Indica si el registro está activo.
        deleted_at (DateTimeField): Fecha y hora de eliminación suave (opcional).

    Meta:
        abstract (bool): Indica que esta clase es abstracta y no crea tabla.
    """
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """
        Realiza una eliminación suave del registro.

        Marca el registro como inactivo y establece la fecha de eliminación.
        """
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

class Expression(BaseModel):
    """
    Modelo que representa una expresión o frase en español latino.

    Atributos:
        lesson (ForeignKey): Lección a la que pertenece la expresión (opcional).
        text (CharField): Texto de la expresión.
        meaning (TextField): Significado de la expresión (opcional).
        example (TextField): Ejemplo de uso de la expresión (opcional).
        audio (FileField): Archivo de audio con la pronunciación (opcional).

    Relaciones:
        lesson: Relación con el modelo Lesson.
    """

    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='expressions', null=True, blank=True)
    text = models.CharField(max_length=200)
    meaning = models.TextField(null=True, blank=True)
    example = models.TextField(null=True, blank=True)
    audio = models.FileField(
        upload_to='expression_audio/',
        null=True,
        blank=True,
        validators=[validate_file_size, validate_audio_extension]
    )

    def __str__(self):
        """Retorna una representación legible de la expresión."""
        return f"{self.text} - {self.lesson.title if self.lesson else ''}"

    def clean(self):
        """
        Valida la expresión y sanitiza el contenido HTML.
        """
        self._validate_content_presence()
        self._validate_text_length()
        self._validate_text_has_letters()
        self._sanitize_html_content()

    def _validate_content_presence(self):
        """
        Valida que se proporcione al menos un significado o ejemplo.
        """
        if not self.meaning and not self.example:
            raise ValidationError("Debe proporcionar al menos un significado o un ejemplo de uso.")

    def _validate_text_length(self):
        """
        Valida la longitud mínima del texto de la expresión.
        """
        if self.text and len(self.text.strip()) < 2:
            raise ValidationError("La expresión debe tener al menos 2 caracteres. Ejemplo: '¡Hola!'")

    def _validate_text_has_letters(self):
        """
        Valida que la expresión contenga al menos una letra.
        """
        if self.text and not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', self.text):
            raise ValidationError("La expresión debe contener al menos una letra.")

    def _sanitize_html_content(self):
        """
        Sanitiza el contenido HTML en significado y ejemplo.
        """
        allowed_tags = ['p', 'br', 'strong', 'em', 'u']
        allowed_attrs = {}

        if self.meaning:
            self.meaning = bleach.clean(self.meaning, tags=allowed_tags, attributes=allowed_attrs, strip=True)

        if self.example:
            self.example = bleach.clean(self.example, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    class Meta:
        ordering = ['created_at']

def lesson_cover_path(instance, filename):
    """Genera un nombre único y corto para las imágenes de portada de lecciones."""
    ext = filename.split('.')[-1]
    # Usar ID + UUID corto para unicidad, sin incluir el título largo
    if instance.id:
        filename = f"{instance.id}_{uuid.uuid4().hex[:6]}.{ext}"
    else:
        # Para nuevas instancias sin ID, usar solo UUID
        filename = f"temp_{uuid.uuid4().hex[:8]}.{ext}"
    return f'lesson_covers/{filename}'

class Lesson(BaseModel):
    LEVEL_CHOICES = [
        ('beginner', _('Principiante')),
        ('intermediate', _('Intermedio')),
        ('advanced', _('Avanzado')),
    ]

    CATEGORY_CHOICES = [
        ('slang', _('Jerga y Slang')),
        ('sayings', _('Dichos Populares')),
        ('expressions', _('Expresiones Coloquiales')),
        ('idioms', _('Modismos')),
    ]

    COUNTRY_CHOICES = [
        ('AR', 'Argentina'),
        ('BO', 'Bolivia'),
        ('CL', 'Chile'),
        ('CO', 'Colombia'),
        ('CR', 'Costa Rica'),
        ('CU', 'Cuba'),
        ('DO', 'República Dominicana'),
        ('EC', 'Ecuador'),
        ('SV', 'El Salvador'),
        ('GT', 'Guatemala'),
        ('HN', 'Honduras'),
        ('MX', 'México'),
        ('NI', 'Nicaragua'),
        ('PA', 'Panamá'),
        ('PY', 'Paraguay'),
        ('PE', 'Perú'),
        ('PR', 'Puerto Rico'),
        ('ES', 'España'),
        ('UY', 'Uruguay'),
        ('VE', 'Venezuela'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='slang')
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    video_url = models.URLField(blank=True, null=True, validators=[validate_youtube_url])
    cultural_notes = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(
        upload_to=lesson_cover_path,
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_extension]
    )

    def get_difficulty_display(self):
        return dict(self.LEVEL_CHOICES).get(self.level, self.level)
    
    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
    
    def get_country_display(self):
        return dict(self.COUNTRY_CHOICES).get(self.country, self.country)
    
    def get_cover_image_url(self):
        """
        Obtiene la URL de la imagen de portada de la lección.

        Retorna:
            str: URL de la imagen de portada o URL de imagen por defecto.
        """
        if self.cover_image and hasattr(self.cover_image, 'url'):
            return self.cover_image.url
        return '/static/core/images/default-cover.jpg'

    def get_video_embed_url(self):
        """
        Convierte URLs de YouTube al formato de embed correcto.

        Retorna:
            str or None: URL de embed de YouTube o None si no hay video_url.
        """
        if not self.video_url:
            return None

        # Si ya es una URL de embed, la devuelve tal como está
        if 'youtube.com/embed' in self.video_url:
            return self.video_url

        # Parsear la URL
        parsed = urlparse(self.video_url)
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            if parsed.netloc == 'youtu.be':
                # youtu.be/short_id
                video_id = parsed.path.lstrip('/')
            else:
                # youtube.com/watch?v=...
                query = parse_qs(parsed.query)
                video_id = query.get('v', [None])[0]

            if video_id and len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                return f'https://www.youtube.com/embed/{video_id}'

        return None

    def get_video_thumbnail_url(self):
        """
        Obtiene la URL de la miniatura del video de YouTube.

        Retorna:
            str or None: URL de la miniatura o None si no hay video_url.
        """
        from .utils import get_youtube_thumbnail_url
        return get_youtube_thumbnail_url(self.video_url)
    
    def __str__(self):
        return self.title


class ForumPost(BaseModel):
    CATEGORY_CHOICES = [
        ('general', _('General')),
        ('grammar', _('Gramática')),
        ('vocabulary', _('Vocabulario')),
        ('pronunciation', _('Pronunciación')),
        ('culture', _('Cultura')),
        ('questions', _('Preguntas')),
        ('resources', _('Recursos')),
        ('off-topic', _('Off Topic')),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def clean(self):
        # Validación básica de contenido
        if not self.content or not self.content.strip():
            raise ValidationError("El contenido no puede estar vacío.")
        content_stripped = self.content.strip()
        if len(content_stripped) < 5:
            raise ValidationError("El contenido es demasiado corto. Debe tener al menos 5 caracteres.")

        # Sanitizar HTML en contenido - permitir tags básicos pero no imágenes por seguridad
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote']
        allowed_attrs = {'a': ['href', 'title', 'rel']}
        self.content = bleach.clean(self.content, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    def get_absolute_url(self):
        return reverse('core:post_detail', kwargs={'post_id': self.pk})

    def __str__(self):
        return self.title




    def can_edit(self, user):
        return user.is_superuser or self.author == user

    def can_delete(self, user):
        return user.is_superuser or self.author == user

    def can_moderate(self, user):
        return user.is_superuser or user.is_staff

    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Publicación del Foro'
        verbose_name_plural = 'Publicaciones del Foro'
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['is_pinned', '-created_at']),
        ]

class Comment(BaseModel):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        if not self.author or not self.post:
            return "Comentario sin autor o post"
        return f'Comentario de {self.author.username} en {self.post.title}'

    def get_replies(self):
        return self.replies.filter(is_active=True).order_by('created_at')

    def clean(self):
        # Sanitizar HTML en contenido
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a']
        allowed_attrs = {'a': ['href', 'title']}
        self.content = bleach.clean(self.content, tags=allowed_tags, attributes=allowed_attrs, strip=True)

class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    preferred_language = models.CharField(max_length=50, default='es')
    learning_goals = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    reputation = models.IntegerField(default=0)
    website = models.URLField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    # Sistema de monetización eliminado - todo es público por ahora
    # Los métodos de suscripción serán implementados más adelante
    # cuando se valide el producto

class Notification(BaseModel):
    TYPE_CHOICES = [
        ('info', _('Información')),
        ('success', _('Éxito')),
        ('warning', _('Advertencia')),
        ('error', _('Error')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.type.upper()}: {self.title} ({self.user.username})"

class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Category(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class SiteSettings(BaseModel):
    """Configuraciones del sitio que el administrador puede cambiar"""
    site_name = models.CharField(max_length=100, default="SlangSpot Latino")
    video_explicativo_url = models.URLField(
        max_length=500, 
        default="https://www.youtube.com/@aprendeconjhons",
        help_text="URL del video que explica qué es SlangSpot Latino"
    )
    video_explicativo_id = models.CharField(
        max_length=20,
        default="rsjRSa_B1P0",
        blank=True,
        help_text="ID del video de YouTube (ej: dQw4w9WgXcQ) para reproducir en la página"
    )
    video_explicativo_titulo = models.CharField(
        max_length=200, 
        default="¿Qué es SlangSpot Latino?",
        help_text="Título del video explicativo"
    )
    video_explicativo_descripcion = models.TextField(
        default="Descubre qué es SlangSpot Latino y cómo te ayudará a aprender español latino de forma auténtica",
        help_text="Descripción del video explicativo"
    )

    class Meta:
        verbose_name = 'Configuración del Sitio'
        verbose_name_plural = 'Configuraciones del Sitio'

    def __str__(self):
        return f"Configuración de {self.site_name}"

    def get_video_thumbnail_url(self):
        """
        Obtiene la URL de la miniatura del video de YouTube.

        Retorna:
            str or None: URL de la miniatura o None si no hay video_url o video_id.
        """
        from .utils import get_youtube_thumbnail_url, extract_youtube_video_id

        # Primero intentar usar el video_id directo si está disponible
        if self.video_explicativo_id and len(self.video_explicativo_id.strip()) > 0:
            video_id = self.video_explicativo_id.strip()
            import re
            if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                return f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'

        # Si no hay video_id, intentar extraer de la URL
        return get_youtube_thumbnail_url(self.video_explicativo_url)

    @classmethod
    def get_settings(cls):
        """Obtiene la configuración del sitio, creando una si no existe"""
        settings, created = cls.objects.get_or_create(
            is_active=True,
            defaults={
                'site_name': 'SlangSpot Latino',
                'video_explicativo_url': 'https://www.youtube.com/@aprendeconjhons',
                'video_explicativo_id': 'rsjRSa_B1P0',
                'video_explicativo_titulo': '¿Qué es SlangSpot Latino?',
                'video_explicativo_descripcion': 'Descubre qué es SlangSpot Latino y cómo te ayudará a aprender español latino de forma auténtica'
            }
        )
        return settings



class Conversation(BaseModel):
    """
    Modelo que representa una conversación de chat con IA.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, help_text="Título de la conversación")
    last_message_at = models.DateTimeField(null=True, blank=True, help_text="Fecha del último mensaje")
    message_count = models.PositiveIntegerField(default=0, help_text="Número total de mensajes")

    def __str__(self):
        title = self.title or f"Conversación {self.id}"
        return f"{title} - {self.user.username}"

    def update_last_message(self):
        """Actualiza la fecha del último mensaje y el contador"""
        from django.db.models import Count
        self.last_message_at = timezone.now()
        self.message_count = self.messages.filter(is_active=True).count()
        self.save(update_fields=['last_message_at', 'message_count'])

    class Meta:
        ordering = ['-last_message_at', '-updated_at']
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
        indexes = [
            models.Index(fields=['user', '-last_message_at']),
        ]

class Message(BaseModel):
    """
    Modelo que representa un mensaje en una conversación de chat.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Conversación a la que pertenece el mensaje"
    )
    content = models.TextField(help_text="Contenido del mensaje")
    is_user = models.BooleanField(default=True, help_text="True si es mensaje del usuario, False si es de la IA")
    read_at = models.DateTimeField(null=True, blank=True, help_text="Fecha en que el usuario leyó el mensaje")

    def __str__(self):
        sender = "Usuario" if self.is_user else "IA"
        return f"{sender}: {self.content[:50]}... ({self.created_at})"

    def mark_as_read(self):
        """Marca el mensaje como leído"""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['is_user']),
        ]

class BlogPost(BaseModel):
    CATEGORY_CHOICES = [
        ('slang', _('Slang y Expresiones')),
        ('culture', _('Cultura')),
        ('tips', _('Tips de Aprendizaje')),
        ('stories', _('Historias y Anécdotas')),
        ('interviews', _('Entrevistas')),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True, help_text="Resumen corto del artículo")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='slang')
    featured_image = models.ImageField(
        upload_to='blog_images/',
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_extension]
    )
    is_published = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_blog_posts', blank=True)

    def clean(self):
        # Validación y sanitización de contenido del blog
        if not self.content or not self.content.strip():
            raise ValidationError("El contenido del artículo no puede estar vacío.")
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote']
        allowed_attrs = {'a': ['href', 'title', 'rel']}
        self.content = bleach.clean(self.content, tags=allowed_tags, attributes=allowed_attrs, strip=True)
        if self.excerpt:
            self.excerpt = bleach.clean(self.excerpt, tags=['p', 'br', 'strong', 'em', 'u'], attributes={}, strip=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:blog_detail', kwargs={'slug': self.slug})

    def get_featured_image_url(self):
        if self.featured_image and hasattr(self.featured_image, 'url'):
            return self.featured_image.url
        return '/static/core/images/default-cover.jpg'

    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Artículo del Blog'
        verbose_name_plural = 'Artículos del Blog'
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return self.title

class UserLessonProgress(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'lesson')
        verbose_name = 'Progreso de lección'
        verbose_name_plural = 'Progresos de lecciones'

    def __str__(self):
        return f"{self.user} - {self.lesson} - {'Completada' if self.completed else 'En progreso'}"

class BlogComment(BaseModel):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField(max_length=1000)
    likes = models.ManyToManyField(User, related_name='liked_blog_comments', blank=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comentario de blog'
        verbose_name_plural = 'Comentarios de blog'

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Comentario de {self.author.username} en {self.post.title}"
