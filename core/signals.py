from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
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