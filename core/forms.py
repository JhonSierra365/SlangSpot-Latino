from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ForumPost, Comment, Lesson, Expression, Practice, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

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
            # Verificar si es una URL de YouTube válida
            youtube_patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)',
                r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
                r'youtu\.be\/([^&\n?#]+)',
            ]

            is_youtube_url = False
            for pattern in youtube_patterns:
                if re.search(pattern, video_url, re.IGNORECASE):
                    is_youtube_url = True
                    break

            if not is_youtube_url and ('youtube.com' in video_url.lower() or 'youtu.be' in video_url.lower()):
                # Es una URL de YouTube pero no coincide con los patrones
                potential_ids = re.findall(r'[a-zA-Z0-9_-]{11}', video_url)
                if not potential_ids:
                    raise forms.ValidationError(
                        'Formato de URL de YouTube no reconocido. Usa uno de estos formatos: '
                        'https://www.youtube.com/watch?v=VIDEO_ID, '
                        'https://youtu.be/VIDEO_ID, '
                        'https://www.youtube.com/embed/VIDEO_ID'
                    )
            elif not is_youtube_url:
                raise forms.ValidationError('Solo se permiten URLs de YouTube.')

        return video_url

class ExpressionForm(forms.ModelForm):
    class Meta:
        model = Expression
        fields = ['text', 'meaning', 'example', 'audio']
        labels = {
            'text': 'Expresión',
            'meaning': 'Significado',
            'example': 'Ejemplo de uso',
            'audio': 'Audio (opcional)',
        }
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Escribe la expresión o frase...'}),
            'meaning': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Explica el significado...'}),
            'example': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ejemplo de uso en contexto...'}),
            'audio': forms.FileInput(attrs={'accept': 'audio/*'}),
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