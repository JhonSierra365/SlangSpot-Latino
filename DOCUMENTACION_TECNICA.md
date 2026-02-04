# Documentación Técnica: SlangSpot Latino

Este documento proporciona una visión general técnica del proyecto **SlangSpot Latino**, incluyendo la arquitectura de datos, stack tecnológico y guía de ejecución.

## 1. Estructura de la Base de Datos
El proyecto utiliza una base de datos relacional (SQLite en desarrollo / PostgreSQL en producción) gestionada a través del ORM de Django. Los modelos principales son:

### Core (Aplicación Principal)
*   **Expression**: Almacena expresiones de jerga.
    *   Campos: `text`, `meaning`, `example`, `audio`, `lesson` (FK).
*   **Lesson**: Lecciones estructuradas.
    *   Campos: `title`, `level` (Principiante/Intermedio...etc), `country`, `video_url`, `content`, `cover_image`.
*   **ForumPost**: Publicaciones del foro de la comunidad.
    *   Campos: `title`, `content`, `author` (User FK), `category`, `is_pinned`, `slug`.
*   **Comment**: Comentarios en los posts del foro (soporta anidamiento).
    *   Campos: `post`, `author`, `content`, `parent` (Self FK).
*   **UserProfile**: Extensión del modelo User de Django.
    *   Campos: `bio`, `preferred_language`, `avatar`, `reputation`, `learning_goals`.
*   **Conversation & Message**: Sistema de Chat con IA.
    *   `Conversation`: Metadatos del chat (`user`, `last_message_at`).
    *   `Message`: Contenido del chat (`content`, `is_user`).
*   **BlogPost**: Artículos del blog.
    *   Campos: `title`, `content`, `category`, `is_published`.
*   **SiteSettings**: Configuración dinámica del sitio (ej. video explicativo en home).

## 2. Tecnologías Utilizadas
### Backend
*   **Django 5.2.3**: Framework web principal.
*   **Django Allauth**: Autenticación y registro (incluye Social Login con Google).
*   **Bleach**: Sanitización de HTML para seguridad en contenido de usuarios.
*   **Django Compressor**: Optimización de archivos estáticos (CSS/JS).
*   **Django Redis**: Cache y backend de sesiones (opcional/producción).

### Base de Datos & Almacenamiento
*   **SQLite**: Base de datos por defecto para desarrollo.
*   **Redis**: Utilizado para caché y sesiones si se configura `REDIS_URL`.

### Dependencias Clave (requirements.txt)
*   `whitenoise`: Servidor de archivos estáticos.
*   `sentry-sdk`: Monitoreo de errores (Prod).
*   `Pillow`: Procesamiento de imágenes.

## 3. Cómo Ejecutar el Proyecto Localmente

### Prerrequisitos
*   Python 3.10+
*   Pip (Gestor de paquetes)

### Pasos
1.  **Clonar/Navegar al directorio del proyecto**:
    ```bash
    cd "SlangSpot Latino Google"
    ```

2.  **Crear y activar un entorno virtual** (Recomendado):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Mac/Linux
    # o
    .\venv\Scripts\activate   # En Windows
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variables de entorno**:
    Cree un archivo `.env` en la raíz (basado en `env_template.txt` si existe) o asegúrese de que `python-decouple` pueda leer las variables necesarias (`SECRET_KEY`, `DEBUG=True`).

5.  **Aplicar migraciones de base de datos**:
    ```bash
    python manage.py migrate
    ```

6.  **Ejecutar el servidor de desarrollo**:
    ```bash
    python manage.py runserver
    ```
    El sitio estará disponible en `http://127.0.0.1:8000`.

## 4. Credenciales de Acceso Admin
Por seguridad, las contraseñas **no se almacenan en el código**. Para acceder al panel de administración (`/admin`), debe crear un "superusuario" localmente:

1.  Asegúrese de que el entorno virtual esté activo.
2.  Ejecute el siguiente comando:
    ```bash
    python manage.py createsuperuser
    ```
3.  Siga las instrucciones interactivas:
    *   **Username**: admin (o el que prefiera)
    *   **Email**: admin@example.com
    *   **Password**: (Ingrese una contraseña segura)

Una vez creado, puede iniciar sesión en `http://127.0.0.1:8000/admin` con esas credenciales.
