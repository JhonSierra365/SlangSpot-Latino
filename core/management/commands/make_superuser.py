from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        email = 'jasierra8767@gmail.com'
        try:
            u = User.objects.get(email=email)
            u.is_staff = True
            u.is_superuser = True
            u.save()
            self.stdout.write(f'Superusuario actualizado: {u.username}')
        except User.DoesNotExist:
            self.stdout.write('Usuario no encontrado')
