"""
Management command to set up the database for SlangSpot Latino.
Handles database creation, migrations, and initial data setup.
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Set up database for SlangSpot Latino'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset database (drop all tables)',
        )
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create default superuser',
        )
        parser.add_argument(
            '--load-fixtures',
            action='store_true',
            help='Load initial data fixtures',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando configuración de base de datos para SlangSpot Latino')
        )

        # Verificar tipo de base de datos
        db_engine = connection.vendor
        self.stdout.write(f'📊 Base de datos: {db_engine}')

        if options['reset']:
            self.reset_database(db_engine)

        # Ejecutar migraciones
        self.stdout.write('🔄 Ejecutando migraciones...')
        call_command('migrate', verbosity=1)

        # Crear superusuario si se solicita
        if options['create_superuser']:
            self.create_superuser()

        # Cargar fixtures si se solicita
        if options['load_fixtures']:
            self.load_fixtures()

        self.stdout.write(
            self.style.SUCCESS('✅ Configuración de base de datos completada!')
        )

    def reset_database(self, db_engine):
        """Reset database by dropping all tables."""
        self.stdout.write('🗑️  Reseteando base de datos...')

        if db_engine == 'sqlite3':
            # Para SQLite, eliminar el archivo de base de datos
            db_path = connection.settings_dict['NAME']
            if os.path.exists(db_path):
                os.remove(db_path)
                self.stdout.write(f'   Eliminado: {db_path}')
        elif db_engine == 'postgresql':
            # Para PostgreSQL, eliminar todas las tablas
            with connection.cursor() as cursor:
                # Obtener todas las tablas
                cursor.execute("""
                    SELECT tablename FROM pg_tables
                    WHERE schemaname = 'public';
                """)
                tables = cursor.fetchall()

                if tables:
                    # Desactivar restricciones de clave foránea
                    cursor.execute("SET CONSTRAINTS ALL DEFERRED;")

                    # Eliminar todas las tablas
                    for table in tables:
                        cursor.execute(f'DROP TABLE IF EXISTS "{table[0]}" CASCADE;')

                    self.stdout.write(f'   Eliminadas {len(tables)} tablas')
                else:
                    self.stdout.write('   No hay tablas para eliminar')
        else:
            raise CommandError(f'Motor de base de datos no soportado: {db_engine}')

    def create_superuser(self):
        """Create default superuser if it doesn't exist."""
        self.stdout.write('👤 Creando superusuario...')

        # Verificar si ya existe un superusuario
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('   Superusuario ya existe, omitiendo creación')
            return

        # Crear superusuario con variables de entorno o valores por defecto
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@slangspot.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'   Superusuario creado: {username}')
            )
            self.stdout.write(
                self.style.WARNING('   ⚠️  Cambia la contraseña por defecto en producción!')
            )
        except Exception as e:
            raise CommandError(f'Error creando superusuario: {e}')

    def load_fixtures(self):
        """Load initial data fixtures."""
        self.stdout.write('📦 Cargando datos iniciales...')

        # Lista de fixtures a cargar (en orden)
        fixtures = [
            # Agregar fixtures aquí cuando se creen
            # 'initial_categories.json',
            # 'initial_tags.json',
        ]

        for fixture in fixtures:
            try:
                call_command('loaddata', fixture, verbosity=1)
                self.stdout.write(f'   ✅ {fixture}')
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'   ⚠️  {fixture}: {e}')
                )

        if not fixtures:
            self.stdout.write('   No hay fixtures configurados')