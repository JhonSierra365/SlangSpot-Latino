from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from allauth.socialaccount.signals import social_account_added
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil de usuario cuando se crea un nuevo usuario.
    """
    if created:
        try:
            UserProfile.objects.create(user=instance)
        except Exception as e:
            # Log del error pero no interrumpir el proceso de registro
            logger.error(f"Error creando perfil para usuario {instance.username}: {e}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda el perfil de usuario cuando se guarda el usuario.
    """
    try:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # Si no existe perfil, crear uno
        try:
            UserProfile.objects.create(user=instance)
        except Exception as e:
            logger.error(f"Error creando perfil para usuario existente {instance.username}: {e}")
    except Exception as e:
        logger.error(f"Error guardando perfil para usuario {instance.username}: {e}")

@receiver(social_account_added)
def set_exclusive_admin_by_email(sender, request, sociallogin, **kwargs):
    """
    Operación 'Único Gran Jefe':
    Concede permisos de Staff y Superusuario única y exclusivamente
    al correo del administrador tras vincular su cuenta social.
    Revoca inmediatamente cualquier permiso similar a cualquier otro usuario.
    """
    user = sociallogin.user
    
    if user.email == 'jasierra8767@gmail.com':
        user.is_staff = True
        user.is_superuser = True
        logger.info(f"Permisos de Superusuario OTORGADOS automáticamente a: {user.email}")
    else:
        # Asegurarse de que cualquier otra persona no sea admin
        if user.is_staff or user.is_superuser:
            logger.warning(f"Permisos de Superusuario DENEGADOS/REVOCADOS a: {user.email}")
        user.is_staff = False
        user.is_superuser = False
        
    user.save()