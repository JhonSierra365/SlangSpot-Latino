import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slangspot.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.filter(email='jasierra8767@gmail.com').first()
if user:
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print('PERMISOS OTORGADOS CORRECTAMENTE')
else:
    User.objects.create_superuser('jhon_admin', 'jasierra8767@gmail.com', 'password_temporal_123')
    print('SUPERUSUARIO CREADO DESDE CERO')
