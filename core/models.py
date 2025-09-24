from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .validators import validate_file_size, validate_image_extension, validate_audio_extension
import uuid
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

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
        Valida que se proporcione al menos un significado o ejemplo.

        Lanza:
            ValidationError: Si no se proporciona ni significado ni ejemplo.
        """
        if not self.meaning and not self.example:
            raise ValidationError("Debe proporcionar al menos un significado o un ejemplo de uso.")

    class Meta:
        ordering = ['created_at']

def lesson_cover_path(instance, filename):
    # Generar un nombre único para la imagen
    ext = filename.split('.')[-1]
    filename = f"{instance.id}_{instance.title}_{uuid.uuid4().hex[:8]}.{ext}"
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
    video_url = models.URLField(blank=True, null=True)
    cultural_notes = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(
        upload_to=lesson_cover_path,
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_extension]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

        Soporta diferentes formatos de URLs de YouTube y retorna la URL
        de embed correspondiente.

        Retorna:
            str or None: URL de embed de YouTube o None si no hay video_url.
        """
        if not self.video_url:
            return None

        # Si ya es una URL de embed, la devuelve tal como está
        if 'youtube.com/embed' in self.video_url or 'youtu.be/embed' in self.video_url:
            return self.video_url

        # Extrae el ID del video de diferentes formatos de URL de YouTube
        import re

        # Patrones más completos para diferentes formatos de URL de YouTube
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)',
            r'youtube\.com/watch\?[^&]*v=([^&\n?#]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.video_url, re.IGNORECASE)
            if match:
                video_id = match.group(1)
                # Limpiar el ID del video (remover parámetros adicionales)
                video_id = video_id.split('?')[0].split('&')[0].split('#')[0]
                # Validar que el ID tenga 11 caracteres (IDs de YouTube estándar)
                if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                    return f'https://www.youtube.com/embed/{video_id}'

        # Si no coincide con ningún patrón, intentar extraer ID directamente
        # para casos como URLs malformadas
        url_lower = self.video_url.lower()
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            # Buscar cualquier secuencia de 11 caracteres que podría ser un ID de YouTube
            potential_ids = re.findall(r'[a-zA-Z0-9_-]{11}', self.video_url)
            if potential_ids:
                video_id = potential_ids[0]
                if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                    return f'https://www.youtube.com/embed/{video_id}'

        # Si no se puede convertir, devolver None para no mostrar el iframe
        return None

    def get_video_thumbnail_url(self):
        """
        Obtiene la URL de la miniatura del video de YouTube.

        Retorna:
            str or None: URL de la miniatura o None si no hay video_url.
        """
        if not self.video_url:
            return None

        # Extraer el ID del video usando la misma lógica que get_video_embed_url
        import re

        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)',
            r'youtube\.com/watch\?[^&]*v=([^&\n?#]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.video_url, re.IGNORECASE)
            if match:
                video_id = match.group(1)
                # Limpiar el ID del video
                video_id = video_id.split('?')[0].split('&')[0].split('#')[0]
                # Validar que el ID tenga 11 caracteres
                if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                    # Retornar URL de miniatura de máxima calidad, con fallback a hqdefault si maxresdefault no existe
                    return f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'

        return None
    
    def __str__(self):
        return self.title

    def clean(self):
        if not self.content or self.content.strip() == '':
            raise ValidationError("El contenido de la lección no puede estar vacío.")
        if self.content == 'Contenido pendiente':
            raise ValidationError("Por favor, escribe el contenido de la lección.")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lección'
        verbose_name_plural = 'Lecciones'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['level']),
            models.Index(fields=['category']),
            models.Index(fields=['country']),
            models.Index(fields=['created_at']),
        ]

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

    def get_absolute_url(self):
        return reverse('core:post_detail', kwargs={'pk': self.pk})

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

class Comment(BaseModel):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        if not self.author or not self.post:
            return "Comentario sin autor o post"
        return f'Comentario de {self.author.username} en {self.post.title}'

    def get_replies(self):
        return self.replies.filter(is_active=True).order_by('created_at')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    preferred_language = models.CharField(max_length=50, default='es')
    learning_goals = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    reputation = models.IntegerField(default=0)
    website = models.URLField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

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
        import re

        # Primero intentar usar el video_id directo si está disponible
        if self.video_explicativo_id and len(self.video_explicativo_id.strip()) > 0:
            video_id = self.video_explicativo_id.strip()
            if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                return f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'

        # Si no hay video_id, intentar extraer de la URL
        video_url = self.video_explicativo_url
        if not video_url:
            return None

        # Extraer el ID del video usando la misma lógica que get_video_embed_url

        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)',
            r'youtube\.com/watch\?[^&]*v=([^&\n?#]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, video_url, re.IGNORECASE)
            if match:
                video_id = match.group(1)
                # Limpiar el ID del video
                video_id = video_id.split('?')[0].split('&')[0].split('#')[0]
                # Validar que el ID tenga 11 caracteres
                if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                    # Retornar URL de miniatura de máxima calidad, con fallback a hqdefault si maxresdefault no existe
                    return f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'

        return None

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

class Practice(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', _('Fácil')),
        ('medium', _('Medio')),
        ('hard', _('Difícil')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.user.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje en {self.conversation.title} - {self.created_at}"

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

    def __str__(self):
        return self.title
