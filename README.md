# SlangSpot Latino

Una plataforma educativa para aprender español latino de forma auténtica y divertida. Aprende expresiones, slang y cultura de países latinoamericanos a través de lecciones interactivas, foro comunitario y contenido multimedia.

## 🚀 Características

- **Lecciones Interactivas**: Aprende expresiones reales con ejemplos contextuales
- **Foro Comunitario**: Conecta con otros estudiantes y hablantes nativos
- **Sistema de Blog**: Artículos sobre cultura y tips de aprendizaje
- **Práctica Personalizada**: Ejercicios adaptados a tu nivel
- **Chat con IA**: Conversaciones para practicar el idioma
- **Sistema de Reputación**: Gana puntos por participación activa
- **Autenticación Social**: Inicia sesión con Google
- **Responsive Design**: Funciona perfectamente en móvil y desktop
- **Seguridad Avanzada**: Sanitización HTML, rate limiting, validación estricta

## 🔒 Seguridad

SlangSpot Latino implementa múltiples capas de seguridad:

- **Sanitización HTML**: Todos los contenidos generados por usuarios pasan por sanitización con Bleach para prevenir XSS
- **Rate Limiting**: Control de tasa en formularios (5 lecciones/min, 10 expresiones/min por usuario)
- **Validación Estricta**: URLs de YouTube validadas, archivos con límites de tamaño y tipos permitidos
- **Headers de Seguridad**: Configuración avanzada de headers HTTP para protección adicional
- **Soft Delete**: Eliminación suave de datos para recuperación y auditoría

## 🛠️ Tecnologías

- **Backend**: Django 5.2.3
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Autenticación**: Django Allauth con OAuth 2.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Compresión**: Django Compressor
- **Cache**: Redis avanzado / LocMem
- **Seguridad**: Bleach (sanitización HTML), Django Ratelimit (control de tasa)
- **Monitoreo**: Django Debug Toolbar (desarrollo), Sentry (producción)
- **Analytics**: Google Analytics 4
- **CDN**: CloudFlare Pages (opcional)
- **CI/CD**: GitHub Actions con deployment automático
- **Despliegue**: Railway/Render/Docker-ready

## 📋 Requisitos

- Python 3.8+
- pip
- virtualenv (recomendado)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/slangspot-latino.git
cd slangspot-latino
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 5. Configurar base de datos

**Opción automática (recomendada):**
```bash
python manage.py setup_database --create-superuser
```

**Opción manual:**

Ejecutar migraciones:
```bash
python manage.py migrate
```

Crear superusuario:
```bash
python manage.py createsuperuser
```

**Resetear base de datos (desarrollo):**
```bash
python manage.py setup_database --reset --create-superuser
```

### 7. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

Visita `http://127.0.0.1:8000` en tu navegador.

## 🔧 Configuración de Producción

### Variables de Entorno

```env
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DATABASE_URL=postgresql://usuario:password@localhost:5432/slangspot
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Monitoreo y Analytics
SENTRY_DSN=https://tu-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXXX

# Cache Avanzado (Redis)
REDIS_URL=redis://localhost:6379/0

# CDN (opcional)
CDN_ENABLED=true
CDN_DOMAIN=cdn.tu-dominio.com
```

### Base de Datos PostgreSQL

**Instalar PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# macOS con Homebrew
brew install postgresql
brew services start postgresql

# Windows - descargar de https://www.postgresql.org/download/
```

**Configurar base de datos:**
```bash
# Crear usuario y base de datos
sudo -u postgres psql
CREATE DATABASE slangspot;
CREATE USER slangspot_user WITH PASSWORD 'tu_password_seguro';
GRANT ALL PRIVILEGES ON DATABASE slangspot TO slangspot_user;
ALTER USER slangspot_user CREATEDB;
\q

# Verificar conexión
psql -h localhost -U slangspot_user -d slangspot
```

**Variables de entorno para PostgreSQL:**
```env
DATABASE_URL=postgresql://slangspot_user:tu_password_seguro@localhost:5432/slangspot
```

### Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### Compresión de Assets

```bash
python manage.py compress
```

## 📁 Estructura del Proyecto

```
slangspot-latino/
├── core/                          # App principal
│   ├── models.py                  # Modelos de datos
│   ├── views.py                   # Vistas y lógica
│   ├── forms.py                   # Formularios
│   ├── templates/                 # Plantillas HTML
│   ├── static/                    # Archivos estáticos
│   ├── migrations/                # Migraciones DB
│   └── tests/                     # Tests
├── slangspot/                     # Configuración Django
│   ├── settings.py                # Configuración principal
│   ├── urls.py                    # URLs del proyecto
│   └── wsgi.py                    # WSGI
├── static/                        # Archivos estáticos globales
├── templates/                     # Plantillas globales
├── requirements.txt               # Dependencias Python
├── manage.py                      # Script de gestión Django
└── README.md                      # Este archivo
```

## 🎯 Uso

### Crear una Lección

1. Inicia sesión en la plataforma
2. Ve a "Lecciones" > "Crear Lección"
3. Completa el formulario con:
   - Título y contenido
   - Nivel de dificultad
   - Categoría y país
   - URL de video de YouTube (opcional)
   - Imagen de portada (opcional)

### Participar en el Foro

1. Ve a la sección "Foro"
2. Crea una nueva publicación o responde a existentes
3. Usa menciones con @usuario
4. Da like a publicaciones útiles

### Sistema de Práctica

1. Accede a "Práctica"
2. Crea ejercicios personalizados
3. Practica con expresiones del día a día

## 🧪 Tests

### Ejecutar Tests

**Script simplificado (recomendado):**
```bash
# Ejecutar todos los tests
python run_tests.py

# Solo tests unitarios
python run_tests.py unit

# Solo tests de integración
python run_tests.py integration

# Análisis de calidad
python run_tests.py quality
```

**Comandos manuales:**

**Todos los tests:**
```bash
python manage.py test
```

**Tests específicos:**
```bash
# Tests unitarios
python manage.py test core.tests.test_models --verbosity=2
python manage.py test core.tests.test_views --verbosity=2
python manage.py test core.tests.test_forms --verbosity=2

# Tests de integración (requieren Chrome WebDriver)
python manage.py test core.tests.test_integration --verbosity=2
```

### Tests de Integración con Selenium

Los tests de integración requieren:
- Chrome WebDriver instalado
- Servidor de desarrollo corriendo

**Instalar Chrome WebDriver:**
```bash
# macOS con Homebrew
brew install chromedriver

# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# Windows - descargar de https://chromedriver.chromium.org/
```

**Ejecutar tests de integración:**
```bash
# Asegurarse de que el servidor no esté corriendo
python manage.py test core.tests.test_integration
```

### Monitoreo y Debugging

**Django Debug Toolbar** (solo en desarrollo):
- Paneles de SQL, templates, cache, señales
- Análisis de rendimiento de queries
- Información detallada de requests

Accede a `http://127.0.0.1:8000/__debug__/` durante desarrollo.

**Sentry** (producción):
- Monitoreo de errores en tiempo real
- Performance monitoring
- Release tracking
- Alertas automáticas

**Google Analytics 4**:
- Métricas de usuario y comportamiento
- Seguimiento de conversiones
- Análisis de rendimiento

### Calidad de Código

**Verificar estilo de código:**
```bash
flake8 core/ slangspot/
```

**Análisis de seguridad:**
```bash
bandit -r core/ slangspot/
```

### CI/CD

El proyecto incluye GitHub Actions para CI/CD automático:

- **Tests automáticos** en cada push/PR
- **Análisis de calidad** de código
- **Tests de seguridad** con Bandit
- **Despliegue automático** a staging/production

Ver `.github/workflows/ci-cd.yml` para detalles.

## 🚀 Despliegue

### Con Docker

```bash
docker build -t slangspot-latino .
docker run -p 8000:8000 slangspot-latino
```

### Con Gunicorn + Nginx

```bash
gunicorn slangspot.wsgi:application --bind 0.0.0.0:8000
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Contacto

- **Autor**: Tu Nombre
- **Email**: tu-email@ejemplo.com
- **YouTube**: [@aprendeconjhons](https://youtube.com/@aprendeconjhons)
- **Podcast**: [SlangSpot Latino](https://podcasts.apple.com/co/podcast/slangspot-latino/id1787990919)

## 🙏 Apoyo

Si te gusta SlangSpot Latino, considera apoyarme:

- ⭐ Dale star al repositorio
- 📱 Comparte en redes sociales
- 💰 [Apoya con PayPal](https://paypal.me/jhonsierramusica)

---

¡Gracias por usar SlangSpot Latino! 🇨🇴🇲🇽🇦🇷🇪🇸