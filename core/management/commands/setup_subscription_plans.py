from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Crea los planes de subscripción por defecto'

    def handle(self, *args, **options):
        # Plan Free (implícito)
        free_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Free',
            defaults={
                'description': 'Plan gratuito con acceso básico',
                'plan_type': 'monthly',
                'price': 0.00,
                'is_active': True,
                'features': [
                    'Acceso a lecciones básicas',
                    'Foro comunitario',
                    'Contenido limitado'
                ],
                'max_lessons': 5,
                'max_expressions': 10,
                'has_priority_support': False,
                'has_audio_download': False,
                'has_certificates': False
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Plan Free creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Plan Free ya existía')
            )

        # Plan Premium Mensual
        premium_monthly, created = SubscriptionPlan.objects.get_or_create(
            name='Premium',
            defaults={
                'description': 'Plan premium con acceso completo',
                'plan_type': 'monthly',
                'price': 9.99,
                'is_active': True,
                'features': [
                    'Acceso completo a todas las lecciones',
                    'Contenido premium exclusivo',
                    'Descarga de audio',
                    'Certificados de completion',
                    'Soporte prioritario',
                    'Lecciones sin límites'
                ],
                'max_lessons': None,  # Sin límite
                'max_expressions': None,  # Sin límite
                'has_priority_support': True,
                'has_audio_download': True,
                'has_certificates': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Plan Premium mensual creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Plan Premium mensual ya existía')
            )

        # Plan Premium Anual
        premium_yearly, created = SubscriptionPlan.objects.get_or_create(
            name='Premium Anual',
            defaults={
                'description': 'Plan premium anual con descuento',
                'plan_type': 'yearly',
                'price': 99.00,
                'is_active': True,
                'features': [
                    'Todos los beneficios del plan Premium',
                    '2 meses gratis (12x10=120, pagas 99)',
                    'Acceso anticipado a nuevo contenido',
                    'Características exclusivas'
                ],
                'max_lessons': None,
                'max_expressions': None,
                'has_priority_support': True,
                'has_audio_download': True,
                'has_certificates': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Plan Premium anual creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Plan Premium anual ya existía')
            )

        self.stdout.write(
            self.style.SUCCESS('Configuración de planes de subscripción completada')
        )