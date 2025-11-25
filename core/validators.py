from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os
from urllib.parse import urlparse, parse_qs
import re

def validate_file_size(value):
    filesize = value.size
    if filesize > 10 * 1024 * 1024:  # 10MB
        raise ValidationError(_("El archivo no puede ser mayor a 10MB"))

def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if ext.lower() not in valid_extensions:
        raise ValidationError(_('Formato de imagen no soportado. Use: jpg, jpeg, png o gif'))

def validate_audio_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.mp3', '.wav', '.ogg']
    if ext.lower() not in valid_extensions:
        raise ValidationError(_('Formato de audio no soportado. Use: mp3, wav u ogg'))

def validate_youtube_url(value):
    """Valida que la URL sea de YouTube y tenga un ID válido"""
    if not value:
        return

    parsed = urlparse(value)
    if parsed.netloc not in ['www.youtube.com', 'youtube.com', 'youtu.be']:
        raise ValidationError(_('Solo se permiten URLs de YouTube. Ejemplos: https://www.youtube.com/watch?v=VIDEO_ID o https://youtu.be/VIDEO_ID'))

    video_id = None
    if parsed.netloc == 'youtu.be':
        video_id = parsed.path.lstrip('/')
    else:
        query = parse_qs(parsed.query)
        video_id = query.get('v', [None])[0]

    if not video_id or len(video_id) != 11 or not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        raise ValidationError(_('URL de YouTube inválida. Asegúrate de que la URL sea correcta y contenga un ID de video válido.'))