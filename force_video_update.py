import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slangspot.settings')
django.setup()
from core.models import SiteSettings
settings = SiteSettings.get_settings()
settings.video_explicativo_id = 'BnC2zl5Y-ds'
settings.save()
print('Video actualizado forzosamente a BnC2zl5Y-ds')
