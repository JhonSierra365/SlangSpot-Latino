from django.db import models
from django.contrib.auth.models import User
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
        Valida que se proporcione al menos un significado o ejemplo.

        Lanza:
            ValidationError: Si no se proporciona ni significado ni ejemplo.
        """
        if not self.meaning and not self.example:
            raise ValidationError("Debe proporcionar al menos un significado o un ejemplo de uso.")

        # Validar longitud del texto de la expresión
        if self.text and len(self.text.strip()) < 2:
            raise ValidationError("La expresión debe tener al menos 2 caracteres.")

        # Validar que la expresión no sea solo caracteres especiales
        import re
        if self.text and not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', self.text):
            raise ValidationError("La expresión debe contener al menos una letra.")

        # Sanitizar contenido HTML en significado y ejemplo
        if self.meaning:
            allowed_tags = ['p', 'br', 'strong', 'em', 'u']
            allowed_attrs = {}
            self.meaning = bleach.clean(self.meaning, tags=allowed_tags, attributes=allowed_attrs, strip=True)

        if self.example:
            allowed_tags = ['p', 'br', 'strong', 'em', 'u']
            allowed_attrs = {}
            self.example = bleach.clean(self.example, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    class Meta:
        ordering = ['created_at']

def lesson_cover_path(instance, filename):
    # Generar un nombre único para la imagen
    ext = filename.split('.')[-1]
    # Usar ID si está disponible, sino usar un UUID temporal
    if instance.id:
        filename = f"{instance.id}_{instance.title}_{uuid.uuid4().hex[:8]}.{ext}"
    else:
        # Para nuevas instancias sin ID, usar timestamp + UUID
        import time
        timestamp = str(int(time.time()))
        filename = f"temp_{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"
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

# Modelos para sistema de subscripciones y pagos

class SubscriptionPlan(BaseModel):
    """
    Modelo que representa los diferentes planes de subscripción disponibles.
    """
    PLAN_TYPES = [
        ('monthly', 'Mensual'),
        ('yearly', 'Anual'),
    ]

    name = models.CharField(max_length=100, help_text="Nombre del plan (ej: Premium, Pro)")
    description = models.TextField(help_text="Descripción del plan y sus beneficios")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default='monthly')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio en USD")
    stripe_price_id = models.CharField(max_length=100, blank=True, help_text="ID del precio en Stripe")
    is_active = models.BooleanField(default=True)
    features = models.JSONField(default=list, help_text="Lista de características del plan")
    max_lessons = models.IntegerField(null=True, blank=True, help_text="Máximo de lecciones que puede crear")
    max_expressions = models.IntegerField(null=True, blank=True, help_text="Máximo de expresiones por lección")
    has_priority_support = models.BooleanField(default=False)
    has_audio_download = models.BooleanField(default=False)
    has_certificates = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.plan_type} (${self.price})"

    class Meta:
        ordering = ['price']
        verbose_name = 'Plan de Subscripción'
        verbose_name_plural = 'Planes de Subscripción'

class UserSubscription(BaseModel):
    """
    Modelo que representa la subscripción activa de un usuario.
    """
    SUBSCRIPTION_STATUS = [
        ('active', 'Activa'),
        ('canceled', 'Cancelada'),
        ('past_due', 'Vencida'),
        ('incomplete', 'Incompleta'),
        ('trialing', 'En período de prueba'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=100, unique=True, help_text="ID de subscripción en Stripe")
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='active')
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.subscription_plan.name}"

    def is_active(self):
        """Verifica si la subscripción está activa"""
        return self.status == 'active' and self.current_period_end > timezone.now()

    def days_until_expiry(self):
        """Retorna los días hasta que expire la subscripción"""
        if not self.is_active():
            return 0
        delta = self.current_period_end - timezone.now()
        return max(0, delta.days)

    class Meta:
        verbose_name = 'Subscripción de Usuario'
        verbose_name_plural = 'Subscripciones de Usuarios'

class Payment(BaseModel):
    """
    Modelo que registra los pagos realizados por los usuarios.
    """
    PAYMENT_STATUS = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey('UserSubscription', on_delete=models.CASCADE, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, help_text="ID del Payment Intent en Stripe")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto en USD")
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.status})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

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
        # Sanitizar HTML en contenido - permitir tags básicos pero no imágenes por seguridad
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote']
        allowed_attrs = {'a': ['href', 'title']}
        self.content = bleach.clean(self.content, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    def get_absolute_url(self):
        return reverse('core:post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    def is_premium_content(self):
        """
        Determina si una lección es contenido premium basado en criterios.
        Por defecto, lecciones avanzadas o con video son premium.
        """
        return self.level == 'advanced' or bool(self.video_url)

    def can_user_access(self, user):
        """
        Determina si un usuario puede acceder a esta lección.
        """
        if not user.is_authenticated:
            return False

        # Los administradores pueden acceder a todo
        if user.is_staff:
            return True

        # Si no es contenido premium, todos pueden acceder
        if not self.is_premium_content():
            return True

        # Para contenido premium, verificar subscripción
        try:
            profile = user.userprofile
            return profile.has_active_subscription()
        except:
            return False

    def clean(self):
        # Validar contenido básico
        if not self.content or not self.content.strip():
            raise ValidationError("El contenido de la lección no puede estar vacío.")

        # Limpiar contenido de espacios y caracteres especiales
        content_stripped = self.content.strip()

        # Validar longitud mínima razonable (al menos 10 caracteres después de limpiar)
        if len(content_stripped) < 10:
            raise ValidationError("El contenido de la lección es demasiado corto. Debe tener al menos 10 caracteres.")

        # Verificar contenido por defecto o placeholder
        placeholder_texts = ['Contenido pendiente', 'contenido pendiente', 'Contenido por defecto', 'Por favor escribe el contenido']
        if any(placeholder in content_stripped.lower() for placeholder in placeholder_texts):
            raise ValidationError("Por favor, escribe el contenido real de la lección.")

        # Sanitizar HTML para seguridad
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a']
        allowed_attrs = {'a': ['href', 'title']}
        self.content = bleach.clean(self.content, tags=allowed_tags, attributes=allowed_attrs, strip=True)

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

    def has_active_subscription(self):
        """
        Verifica si el usuario tiene una subscripción activa.
        """
        try:
            active_subscription = self.user.usersubscription.filter(
                status='active',
                current_period_end__gt=timezone.now()
            ).first()
            return active_subscription is not None
        except:
            return False

    def get_subscription_status(self):
        """
        Obtiene el estado de la subscripción del usuario.
        """
        try:
            subscription = self.user.usersubscription_set.filter(
                status__in=['active', 'trialing']
            ).first()
            if subscription:
                return subscription.status
        except:
            pass
        return 'none'

    def can_create_lessons(self):
        """
        Verifica si el usuario puede crear lecciones basado en su plan.
        """
        if self.user.is_staff:
            return True

        subscription = self.user.usersubscription_set.filter(
            status='active',
            current_period_end__gt=timezone.now()
        ).first()

        if not subscription:
            return True  # Los usuarios free pueden crear lecciones básicas

        # Verificar límites del plan
        if subscription.subscription_plan.max_lessons:
            current_count = Lesson.objects.filter(user=self.user, is_active=True).count()
            return current_count < subscription.subscription_plan.max_lessons

        return True

    def can_access_premium_content(self):
        """
        Verifica si el usuario puede acceder a contenido premium.
        """
        if self.user.is_staff:
            return True
        return self.has_active_subscription()

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

class Practice(BaseModel):
    DIFFICULTY_CHOICES = [
        ('easy', _('Fácil')),
        ('medium', _('Medio')),
        ('hard', _('Difícil')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')

    def __str__(self):
        return self.title

class Conversation(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.user.username}"

class Message(BaseModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)

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
