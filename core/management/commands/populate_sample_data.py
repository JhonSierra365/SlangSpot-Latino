from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import (
    Lesson, Expression, ForumPost, Comment, BlogPost,
    UserProfile
)

class Command(BaseCommand):
    help = 'Poblar la base de datos con contenido de ejemplo atractivo'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando población de contenido de ejemplo...')
        )

        # Crear usuario de ejemplo
        sample_user, created = User.objects.get_or_create(
            username='estudiante_ejemplo',
            defaults={
                'email': 'estudiante@slangspot.com',
                'first_name': 'María',
                'last_name': 'González'
            }
        )
        if created:
            sample_user.set_password('demo123')
            sample_user.save()
            # Crear perfil automáticamente con la señal
            profile = sample_user.userprofile
            profile.bio = 'Estudiante apasionada de español latino, especialmente colombiano y mexicano.'
            profile.learning_goals = 'Aprender expresiones coloquiales para viajar por Latinoamérica.'
            profile.save()

        # Crear usuario experto
        expert_user, created = User.objects.get_or_create(
            username='experto_slang',
            defaults={
                'email': 'experto@slangspot.com',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez'
            }
        )
        if created:
            expert_user.set_password('demo123')
            expert_user.save()
            profile = expert_user.userprofile
            profile.bio = 'Profesor de español con 10 años de experiencia, especializado en slang y cultura latinoamericana.'
            profile.learning_goals = 'Compartir conocimiento auténtico de español latino.'
            profile.reputation = 150
            profile.save()

        self.create_sample_lessons(sample_user, expert_user)
        self.create_sample_expressions()
        self.create_sample_forum_posts(sample_user, expert_user)
        self.create_sample_blog_posts(expert_user)

        self.stdout.write(
            self.style.SUCCESS('✅ ¡Contenido de ejemplo creado exitosamente!')
        )
        self.stdout.write(
            self.style.SUCCESS('📊 Resumen del contenido creado:')
        )
        self.stdout.write(f'   • Lecciones: {Lesson.objects.count()}')
        self.stdout.write(f'   • Expresiones: {Expression.objects.count()}')
        self.stdout.write(f'   • Posts en foro: {ForumPost.objects.count()}')
        self.stdout.write(f'   • Comentarios: {Comment.objects.count()}')
        self.stdout.write(f'   • Artículos de blog: {BlogPost.objects.count()}')

    def create_sample_lessons(self, sample_user, expert_user):
        """Crear lecciones de ejemplo atractivas"""

        lessons_data = [
            {
                'user': expert_user,
                'title': '¡Qué chimba! - Expresiones colombianas básicas',
                'content': '''¡Bienvenidos a esta lección sobre expresiones colombianas auténticas!

En Colombia, especialmente en Bogotá y la costa, encontrarás expresiones únicas que dan color y personalidad al español. Vamos a aprender algunas de las más comunes y útiles.

**¿Qué significa "chimba"?**
La palabra "chimba" en Colombia es una de las expresiones más versátiles. Puede significar:
- Algo genial: "¡Esta fiesta está chimba!" (Esta fiesta está genial)
- Algo impresionante: "¡Qué chimba de carro!" (Qué carro tan genial)
- También puede usarse para expresar admiración o sorpresa positiva

**Contexto cultural:**
En Colombia, las expresiones como "chimba" forman parte del habla cotidiana y ayudan a crear un vínculo más cercano con las personas. No son consideradas groseras, sino parte del lenguaje coloquial natural.

**¿Cuándo usar "chimba"?**
- Para expresar entusiasmo: "¡Qué chimba!" = "¡Qué genial!"
- Para felicitar: "Te quedó chimba" = "Te quedó genial"
- Para expresar sorpresa positiva: "¡Chimba, no lo puedo creer!"

**Ejemplos en contexto:**
1. "Llegamos al mirador y la vista estaba chimba" (Llegamos al mirador y la vista estaba genial)
2. "Mi mamá hace una bandeja paisa chimba" (Mi mamá hace una bandeja paisa genial)
3. "¡Qué chimba que viniste!" (¡Qué genial que viniste!)

**Nota cultural:** En otros países latinoamericanos, esta expresión podría no existir o tener significados diferentes, por eso es importante aprender el contexto local.''',
                'level': 'beginner',
                'category': 'slang',
                'country': 'CO',
                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'cultural_notes': 'En Colombia, el slang es muy regional. En la costa caribeña encontrarás expresiones más influenciadas por el inglés y el criollo, mientras que en los Andes predominan expresiones más tradicionales.'
            },
            {
                'user': expert_user,
                'title': '¡No manches! - Expresiones mexicanas de sorpresa',
                'content': '''¡Hola amigos! ¿Listos para aprender expresiones mexicanas que te dejarán con la boca abierta?

México es un país rico en expresiones coloquiales que varían según la región. Hoy nos enfocaremos en expresiones de sorpresa que escucharás en todo el país.

**"¡No manches!" - La expresión más versátil**
Esta es una de las expresiones más comunes en México para expresar sorpresa, incredulidad o admiración.

**Usos comunes:**
- Sorpresa: "¡No manches! ¿En serio?" (No lo puedo creer, ¿en serio?)
- Admiración: "¡No manches, qué bonito!" (No lo puedo creer, qué bonito)
- Incredulidad: "¡No manches que ya se acabó!" (No lo puedo creer que ya se acabó)

**Otras expresiones de sorpresa mexicanas:**
1. **"¡Órale!"** - Expresa sorpresa o admiración
2. **"¡Híjole!"** - Similar a "¡No manches!" pero más suave
3. **"¡Nel!"** - Expresión de negación o sorpresa (de "no" + "nel" = "no nel")
4. **"¡A huevo!"** - Expresa aprobación o sorpresa positiva

**Contexto cultural:**
En México, estas expresiones forman parte del lenguaje cotidiano y ayudan a crear un ambiente de confianza y cercanía. Son especialmente comunes entre jóvenes y en contextos informales.

**Ejemplos en conversaciones:**
- "¡Órale! ¿Ya terminaste el proyecto?" (¡Qué sorpresa! ¿Ya terminaste?)
- "¡Híjole, qué caro está todo!" (¡Qué barbaridad, qué caro está todo!)
- "¡Nel, no me digas!" (¡No lo puedo creer, no me digas!)

**Variaciones regionales:**
- En el norte de México: más influencia del inglés
- En el centro: expresiones más tradicionales
- En el sur: influencia de lenguas indígenas''',
                'level': 'intermediate',
                'category': 'expressions',
                'country': 'MX',
                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'cultural_notes': 'México tiene una de las variedades más ricas de español en Latinoamérica, con influencias indígenas, africanas y estadounidenses.'
            },
            {
                'user': sample_user,
                'title': '¡Qué boludo! - Lunfardo argentino',
                'content': '''¡Hola che! ¿Querés aprender lunfardo argentino? El lunfardo es el slang típico de Buenos Aires y Río de la Plata.

**"Boludo" - La palabra más característica**
- **Uso amigable:** "Che boludo, ¿cómo estás?" (Hey amigo, ¿cómo estás?)
- **Expresión de sorpresa:** "¡Qué boludo que soy!" (¡Qué tonto que soy!)
- **Enfado:** "¡No seas boludo!" (¡No seas tonto!)

**Otras expresiones del lunfardo:**
1. **"Che"** - Hey, amigo (como "dude" en inglés)
2. **"Copado"** - Genial, excelente
3. **"Flaquita"** - Cerveza (literalmente "flaquita")
4. **"Guita"** - Plata, dinero
5. **"Laburo"** - Trabajo
6. **"Pibe"** - Niño, joven
7. **"Mina"** - Mujer, chica

**Ejemplos en contexto:**
- "Che boludo, pasame la guita" (Hey amigo, pásame la plata)
- "Este laburo está copado" (Este trabajo está genial)
- "La mina está re buena onda" (La chica está muy copada)

**Contexto cultural:**
El lunfardo nació en el tango y la inmigración europea en Buenos Aires. Hoy es parte fundamental de la identidad porteña y argentina.''',
                'level': 'advanced',
                'category': 'slang',
                'country': 'AR',
                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'cultural_notes': 'Argentina tiene uno de los acentos más característicos del español, con influencias italianas muy marcadas en el lunfardo.'
            }
        ]

        for lesson_data in lessons_data:
            lesson, created = Lesson.objects.get_or_create(
                title=lesson_data['title'],
                defaults=lesson_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Lección creada: {lesson.title}')
                )

    def create_sample_expressions(self):
        """Crear expresiones de ejemplo para las lecciones"""

        expressions_data = [
            {
                'lesson_title': '¡Qué chimba! - Expresiones colombianas básicas',
                'text': '¡Qué chimba!',
                'meaning': 'Expresión de admiración o sorpresa positiva. Similar a "¡Qué genial!" o "¡Qué increíble!"',
                'example': '¡Qué chimba este restaurante! La comida está deliciosa.'
            },
            {
                'lesson_title': '¡Qué chimba! - Expresiones colombianas básicas',
                'text': '¡Qué gonorrea!',
                'meaning': 'Expresión de admiración extrema. Similar a "¡Qué increíble!" pero más intensa.',
                'example': '¡Qué gonorrea de vista desde este cerro!'
            },
            {
                'lesson_title': '¡No manches! - Expresiones mexicanas de sorpresa',
                'text': '¡No manches!',
                'meaning': 'Expresión de sorpresa, incredulidad o admiración. Similar a "¡No me digas!" o "¡No lo puedo creer!"',
                'example': '¡No manches! ¿Ya te graduaste? ¡Felicidades!'
            },
            {
                'lesson_title': '¡No manches! - Expresiones mexicanas de sorpresa',
                'text': '¡Órale!',
                'meaning': 'Expresión de sorpresa, admiración o acuerdo. Muy versátil en el español mexicano.',
                'example': '¡Órale! No sabía que tocabas guitarra tan bien.'
            },
            {
                'lesson_title': '¡Qué boludo! - Lunfardo argentino',
                'text': '¡Qué boludo!',
                'meaning': 'Expresión de sorpresa por un error propio o ajeno. Similar a "¡Qué tonto!" pero en contexto amigable.',
                'example': '¡Qué boludo! Me olvidé las llaves adentro del auto.'
            }
        ]

        for expr_data in expressions_data:
            try:
                lesson = Lesson.objects.get(title=expr_data['lesson_title'])
                expression, created = Expression.objects.get_or_create(
                    lesson=lesson,
                    text=expr_data['text'],
                    defaults={
                        'meaning': expr_data['meaning'],
                        'example': expr_data['example']
                    }
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Expresión creada: {expression.text}')
                    )
            except Lesson.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Lección no encontrada: {expr_data["lesson_title"]}')
                )

    def create_sample_forum_posts(self, sample_user, expert_user):
        """Crear posts de ejemplo en el foro"""

        posts_data = [
            {
                'author': sample_user,
                'title': '¡Ayuda! ¿Cómo diferencio el acento colombiano del mexicano?',
                'content': '''¡Hola comunidad! Soy nueva estudiando español latino y me confunden mucho los diferentes acentos.

¿Me podrían dar tips para diferenciar el acento colombiano del mexicano? Especialmente en expresiones coloquiales.

¡Gracias de antemano! 😊''',
                'category': 'pronunciation'
            },
            {
                'author': expert_user,
                'title': 'Recomendaciones de series para practicar listening',
                'content': '''¡Hola a todos los estudiantes!

Para practicar listening y slang auténtico, les recomiendo estas series:

**Para slang colombiano:**
- "La Niña" (serie sobre la vida en Medellín)
- "El Bronx" (realismo urbano bogotano)

**Para slang mexicano:**
- "Club de Cuervos" (fútbol y humor mexicano)
- "La Casa de las Flores" (clase alta mexicana)

**Para slang argentino:**
- "El Marginal" (lunfardo porteño auténtico)
- "Monzón" (boxeo y cultura argentina)

¿Cuáles me recomiendan ustedes?''',
                'category': 'resources'
            },
            {
                'author': sample_user,
                'title': '¿Es grosero decir "chimba" en Colombia?',
                'content': '''¡Hola! Estoy planeando un viaje a Colombia y me encanta la expresión "¡Qué chimba!" pero no quiero ofender a nadie.

¿En qué contextos es apropiado usarla? ¿Hay regiones donde no se usa?

¡Gracias por su ayuda!''',
                'category': 'culture'
            }
        ]

        for post_data in posts_data:
            post, created = ForumPost.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'content': post_data['content'],
                    'author': post_data['author'],
                    'category': post_data['category']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Post creado: {post.title}')
                )

    def create_sample_blog_posts(self, expert_user):
        """Crear artículos de ejemplo en el blog"""

        blog_data = [
            {
                'title': 'Guía completa para aprender español latino auténtico',
                'content': '''Aprender español latino va más allá de las reglas gramaticales. Se trata de entender la cultura, las costumbres y las formas únicas de expresión de cada país.

En esta guía completa, exploraremos los aspectos más importantes para dominar el español latino de manera efectiva y natural.

## 1. Entiende las variaciones regionales

Cada país latinoamericano tiene su propio acento, vocabulario y expresiones únicas:
- **México:** Rico en expresiones indígenas y anglicismos
- **Colombia:** Variado por regiones, con influencia caribeña en la costa
- **Argentina:** Influencia italiana muy marcada en el lunfardo
- **Chile:** Uso único de modismos y expresiones locales

## 2. Aprende el slang por inmersión

La mejor forma de aprender slang auténtico es:
- Ver series y películas locales
- Escuchar música popular
- Interactuar con hablantes nativos
- Practicar en contextos reales

## 3. No temas cometer errores

El aprendizaje de un idioma es un proceso gradual. Los hispanohablantes aprecian el esfuerzo de los estudiantes y suelen ser pacientes y comprensivos.

**Tip:** Empieza con expresiones básicas y ve expandiendo tu vocabulario progresivamente.''',
                'excerpt': 'Guía completa para dominar el español latino auténtico, desde variaciones regionales hasta inmersión cultural.',
                'category': 'tips',
                'is_published': True
            },
            {
                'title': 'Las 10 expresiones colombianas que todo estudiante debe conocer',
                'content': '''Colombia es un país con una riqueza lingüística increíble. Aquí te presentamos las 10 expresiones más útiles y comunes que escucharás en las calles de Bogotá, Medellín y otras ciudades colombianas.

1. **¡Qué chimba!** - ¡Qué genial!
2. **¡Qué gonorrea!** - ¡Qué increíble! (más intenso)
3. **Parcero/a** - Amigo/a
4. **¡Qué hp!** - ¡Qué...! (eufemismo)
5. **¡Listo!** - ¡Perfecto! / ¡Entendido!
6. **¡Qué berraquera!** - ¡Qué valentía!
7. **¡Qué nota!** - ¡Qué genial!
8. **¡Qué boleta!** - ¡Qué vergüenza!
9. **¡Qué oso!** - ¡Qué vergüenza! (más común)
10. **¡Qué pereza!** - ¡Qué flojera!

**Consejo:** Estas expresiones varían por región. En la costa caribeña encontrarás influencias africanas y del inglés, mientras que en los Andes predominan expresiones más tradicionales.''',
                'excerpt': 'Descubre las 10 expresiones colombianas más comunes y útiles para comunicarte como un local.',
                'category': 'slang',
                'is_published': True
            }
        ]

        for blog_data_item in blog_data:
            blog_post, created = BlogPost.objects.get_or_create(
                title=blog_data_item['title'],
                defaults={
                    'content': blog_data_item['content'],
                    'excerpt': blog_data_item['excerpt'],
                    'author': expert_user,
                    'category': blog_data_item['category'],
                    'is_published': blog_data_item['is_published']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Artículo creado: {blog_post.title}')
                )