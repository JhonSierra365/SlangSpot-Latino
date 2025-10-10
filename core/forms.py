from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ForumPost, Comment, Lesson, Expression, Practice, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Ingresa una dirección de correo electrónico válida. Te enviaremos un enlace de confirmación."
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text="Tu nombre real para personalizar tu experiencia."
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text="Tu apellido."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        help_texts = {
            'username': "Elige un nombre de usuario único. Solo letras, números y @/./+/-/_",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de ayuda para contraseñas
        self.fields['password1'].help_text = (
            "Tu contraseña debe tener al menos 8 caracteres y no ser demasiado común. "
            "No debe ser similar a tu información personal."
        )
        self.fields['password2'].help_text = "Repite tu contraseña para confirmar."

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()  # Normalizar email
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Ya existe una cuenta con este correo electrónico.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip()  # Eliminar espacios
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Este nombre de usuario ya está en uso.")
            # Validar caracteres permitidos
            import re
            if not re.match(r'^[a-zA-Z0-9_@.+-]+$', username):
                raise forms.ValidationError("El nombre de usuario solo puede contener letras, números y los caracteres @/./+/-/_")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['title', 'content', 'category']
        labels = {
            'title': 'Título',
            'content': 'Contenido',
            'category': 'Categoría',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la publicación'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Contenido de la publicación', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Título"
        self.fields['content'].label = "Contenido"
        self.fields['category'].label = "Categoría"

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': ''
        }
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Escribe tu comentario aquí...', 'rows': 3})
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'level', 'category', 'country', 'video_url', 'cultural_notes', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            }),
            'cultural_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Título de la Lección',
            'content': 'Contenido',
            'level': 'Nivel de Dificultad',
            'category': 'Categoría',
            'country': 'País',
            'video_url': 'URL del Video de YouTube',
            'cultural_notes': 'Notas Culturales',
            'cover_image': 'Imagen de Portada',
        }
        help_texts = {
            'video_url': '📹 Copia y pega la URL completa del video de YouTube. Formatos soportados: https://www.youtube.com/watch?v=VIDEO_ID, https://youtu.be/VIDEO_ID, https://www.youtube.com/embed/VIDEO_ID',
        }

    def clean_video_url(self):
        """Valida que la URL del video sea de YouTube y tenga un formato válido."""
        video_url = self.cleaned_data.get('video_url')
        if video_url:
            import re
            from urllib.parse import urlparse, parse_qs

            # Verificar si es una URL de YouTube válida
            youtube_patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)',
                r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
                r'youtu\.be\/([^&\n?#]+)',
            ]

            is_youtube_url = False
            video_id = None

            for pattern in youtube_patterns:
                match = re.search(pattern, video_url, re.IGNORECASE)
                if match:
                    is_youtube_url = True
                    video_id = match.group(1)
                    break

            if not is_youtube_url and ('youtube.com' in video_url.lower() or 'youtu.be' in video_url.lower()):
                # Intentar extraer el ID del video usando urllib
                try:
                    parsed = urlparse(video_url)
                    if 'youtu.be' in parsed.netloc:
                        video_id = parsed.path.lstrip('/')
                    elif 'youtube.com' in parsed.netloc:
                        query = parse_qs(parsed.query)
                        video_id = query.get('v', [None])[0]

                    if video_id and len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                        is_youtube_url = True
                except:
                    pass

            if not is_youtube_url:
                raise forms.ValidationError(
                    'Por favor ingresa una URL válida de YouTube. Formatos aceptados: '
                    'https://www.youtube.com/watch?v=VIDEO_ID, '
                    'https://youtu.be/VIDEO_ID, '
                    'https://www.youtube.com/embed/VIDEO_ID'
                )

            # Validar que el video ID tenga el formato correcto
            if video_id and not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                raise forms.ValidationError('El ID del video de YouTube no es válido.')

        return video_url

class ExpressionForm(forms.ModelForm):
    class Meta:
        model = Expression
        fields = ['text', 'meaning', 'example', 'audio']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'meaning': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'example': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'audio': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'text': 'Expresión',
            'meaning': 'Significado',
            'example': 'Ejemplo de uso',
            'audio': 'Audio (opcional)',
        }
        help_texts = {
            'meaning': 'Explica el significado de la expresión.',
            'example': 'Proporciona un ejemplo de uso en contexto.',
            'audio': 'Formatos aceptados: MP3, WAV, OGG (máximo 10MB)',
        }

class PracticeForm(forms.ModelForm):
    class Meta:
        model = Practice
        fields = ['title', 'content', 'difficulty']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'preferred_language', 'learning_goals']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preferred_language': forms.TextInput(attrs={'class': 'form-control'}),
            'learning_goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 