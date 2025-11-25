from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core.models import (
    Expression, Lesson, Comment, ForumPost, UserProfile, lesson_cover_path
)


class ExpressionModelTest(TestCase):
    """Tests para el modelo Expression"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.lesson = Lesson.objects.create(
            user=self.user,
            title='Test Lesson',
            content='Test content',
            country='CO'
        )
    
    def test_expression_creation(self):
        """Test: Crear una expresión válida"""
        expression = Expression.objects.create(
            lesson=self.lesson,
            text='¡Qué chimba!',
            meaning='¡Qué genial!',
            example='¡Qué chimba este lugar!'
        )
        self.assertEqual(expression.text, '¡Qué chimba!')
        self.assertEqual(expression.meaning, '¡Qué genial!')
        self.assertEqual(expression.lesson, self.lesson)
    
    def test_expression_text_required(self):
        """Test: El campo text es obligatorio"""
        expression = Expression(
            lesson=self.lesson,
            meaning='Significado sin texto',
            example='Ejemplo sin texto'
        )
        with self.assertRaises(ValidationError):
            expression.full_clean()
    
    def test_expression_validation_without_meaning_and_example(self):
        """Test: Validación cuando no hay significado ni ejemplo"""
        expression = Expression(
            lesson=self.lesson,
            text='Test expression'
        )
        with self.assertRaises(ValidationError):
            expression.full_clean()
    
    def test_expression_validation_with_meaning_only(self):
        """Test: Validación cuando solo hay significado"""
        expression = Expression(
            lesson=self.lesson,
            text='Test expression',
            meaning='Test meaning'
        )
        try:
            expression.full_clean()
        except ValidationError:
            self.fail("Expression should be valid with meaning only")
    
    def test_expression_validation_with_example_only(self):
        """Test: Validación cuando solo hay ejemplo"""
        expression = Expression(
            lesson=self.lesson,
            text='Test expression',
            example='Test example'
        )
        try:
            expression.full_clean()
        except ValidationError:
            self.fail("Expression should be valid with example only")
    
    def test_expression_str_representation(self):
        """Test: Representación en string de la expresión"""
        expression = Expression.objects.create(
            lesson=self.lesson,
            text='Test expression',
            meaning='Test meaning'
        )
        expected = f"Test expression - {self.lesson.title}"
        self.assertEqual(str(expression), expected)
    
    def test_expression_without_lesson(self):
        """Test: Expresión sin lección asociada"""
        expression = Expression.objects.create(
            text='Test expression',
            meaning='Test meaning'
        )
        self.assertIsNone(expression.lesson)
        self.assertEqual(str(expression), "Test expression - ")


class LessonModelTest(TestCase):
    """Tests para el modelo Lesson"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_lesson_creation(self):
        """Test: Crear una lección válida"""
        lesson = Lesson.objects.create(
            user=self.user,
            title='Test Lesson',
            content='Test content for the lesson',
            country='CO',
            level='beginner',
            category='slang'
        )
        self.assertEqual(lesson.title, 'Test Lesson')
        self.assertEqual(lesson.user, self.user)
        self.assertEqual(lesson.country, 'CO')
    
    def test_lesson_validation_empty_content(self):
        """Test: Validación cuando el contenido está vacío"""
        lesson = Lesson(
            user=self.user,
            title='Test Lesson',
            content='',
            country='CO'
        )
        with self.assertRaises(ValidationError):
            lesson.full_clean()
    
    def test_lesson_validation_default_content(self):
        """Test: Validación cuando el contenido es el valor por defecto"""
        lesson = Lesson(
            user=self.user,
            title='Test Lesson',
            content='Contenido pendiente',
            country='CO'
        )
        with self.assertRaises(ValidationError):
            lesson.full_clean()
    
    def test_lesson_str_representation(self):
        """Test: Representación en string de la lección"""
        lesson = Lesson.objects.create(
            user=self.user,
            title='Test Lesson',
            content='Test content',
            country='CO'
        )
        self.assertEqual(str(lesson), 'Test Lesson')
    
    def test_lesson_get_difficulty_display(self):
        """Test: Obtener el display del nivel de dificultad"""
        lesson = Lesson.objects.create(
            user=self.user,
            title='Test Lesson',
            content='Test content',
            country='CO',
            level='intermediate'
        )
        self.assertEqual(lesson.get_difficulty_display(), 'Intermedio')
    
    def test_lesson_get_category_display(self):
        """Test: Obtener el display de la categoría"""
        lesson = Lesson.objects.create(
            user=self.user,
            title='Test Lesson',
            content='Test content',
            country='CO',
            category='slang'
        )
        self.assertEqual(lesson.get_category_display(), 'Jerga y Slang')
    
    def test_lesson_get_country_display(self):
        """Test: Obtener el display del país"""
        lesson = Lesson.objects.create(
            user=self.user,
            title='Test Lesson',
            content='Test content',
            country='MX'
        )
        self.assertEqual(lesson.get_country_display(), 'México')


class CommentModelTest(TestCase):
    """Tests para el modelo Comment"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = ForumPost.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
    
    def test_comment_creation(self):
        """Test: Crear un comentario válido"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment content'
        )
        self.assertEqual(comment.content, 'Test comment content')
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
    
    def test_comment_author_required(self):
        """Test: El campo author es obligatorio"""
        with self.assertRaises(Exception):
            Comment.objects.create(
                post=self.post,
                content='Test comment without author'
            )
    
    def test_comment_post_required(self):
        """Test: El campo post es obligatorio"""
        with self.assertRaises(Exception):
            Comment.objects.create(
                author=self.user,
                content='Test comment without post'
            )
    
    def test_comment_str_representation(self):
        """Test: Representación en string del comentario"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        expected = f'Comentario de {self.user.username} en {self.post.title}'
        self.assertEqual(str(comment), expected)
    
    def test_comment_replies(self):
        """Test: Sistema de respuestas a comentarios"""
        parent_comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Parent comment'
        )
        reply = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Reply to parent',
            parent=parent_comment
        )
        replies = parent_comment.get_replies()
        self.assertIn(reply, replies)
        self.assertEqual(replies.count(), 1)


class UserProfileModelTest(TestCase):
    """Tests para el modelo UserProfile"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_userprofile_creation(self):
        """Test: Crear un perfil de usuario válido"""
        # Como ya existe un perfil por la señal automática, lo obtenemos
        profile = self.user.userprofile
        # Actualizamos los valores
        profile.bio = 'Test bio'
        profile.preferred_language = 'es'
        profile.learning_goals = 'Learn Spanish'
        profile.save()

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, 'Test bio')
        self.assertEqual(profile.preferred_language, 'es')
    
    def test_userprofile_str_representation(self):
        """Test: Representación en string del perfil"""
        # Usar el perfil existente creado por la señal automática
        profile = self.user.userprofile
        profile.bio = 'Test bio'
        profile.save()
        expected = f"{self.user.username}'s profile"
        self.assertEqual(str(profile), expected)
    
    def test_userprofile_default_values(self):
        """Test: Valores por defecto del perfil"""
        # Usar el perfil existente creado por la señal automática
        profile = self.user.userprofile
        self.assertEqual(profile.preferred_language, 'es')
        self.assertEqual(profile.reputation, 0)
        self.assertEqual(profile.bio, '')
        self.assertEqual(profile.learning_goals, '')

    def test_user_profile_auto_creation(self):
        """Test: Verificar que el perfil se crea automáticamente con la señal"""
        # Crear usuario directamente en la base de datos
        user = User.objects.create_user(
            username='signal_test_user',
            email='signal@example.com',
            password='testpass123'
        )

        # Verificar que el perfil se creó automáticamente
        self.assertTrue(hasattr(user, 'userprofile'))
        profile = user.userprofile
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.preferred_language, 'es')

    def test_lesson_video_url_validation(self):
        """Test: Validar URLs de YouTube en lecciones"""
        user = User.objects.create_user(
            username='lesson_test_user',
            email='lesson@example.com',
            password='testpass123'
        )

        # URL válida de YouTube
        valid_lesson = Lesson(
            user=user,
            title='Test Lesson with Video',
            content='Test content with video',
            country='CO',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        )

        # No debería lanzar error
        try:
            valid_lesson.full_clean()
        except ValidationError:
            self.fail("Valid YouTube URL should not raise ValidationError")

        # URL inválida
        invalid_lesson = Lesson(
            user=user,
            title='Test Lesson with Invalid Video',
            content='Test content with invalid video',
            country='CO',
            video_url='https://example.com/video'
        )

        # Debería lanzar error
        with self.assertRaises(ValidationError):
            invalid_lesson.full_clean()

    def test_lesson_file_upload_path_without_id(self):
        """Test: Función de upload de archivos cuando la lección no tiene ID"""
        user = User.objects.create_user(
            username='upload_test_user',
            email='upload@example.com',
            password='testpass123'
        )

        # Crear lección sin guardar (sin ID)
        lesson = Lesson(
            user=user,
            title='Test Upload Lesson',
            content='Test content for upload testing',
            country='CO'
        )

        # Probar función de path sin ID
        test_filename = 'test_image.jpg'
        path = lesson_cover_path(lesson, test_filename)

        # Debería generar un path válido con timestamp
        self.assertIn('lesson_covers/', path)
        self.assertIn('.jpg', path)
        self.assertTrue(path.startswith('lesson_covers/temp_'))

    def test_lesson_content_validation_edge_cases(self):
        """Test: Validaciones edge case del contenido de lecciones"""
        user = User.objects.create_user(
            username='validation_test_user',
            email='validation@example.com',
            password='testpass123'
        )

        # Contenido muy corto
        short_lesson = Lesson(
            user=user,
            title='Short Lesson',
            content='Hi',
            country='CO'
        )

        with self.assertRaises(ValidationError):
            short_lesson.full_clean()

        # Contenido con solo espacios
        spaces_lesson = Lesson(
            user=user,
            title='Spaces Lesson',
            content='   ',
            country='CO'
        )

        with self.assertRaises(ValidationError):
            spaces_lesson.full_clean()

        # Contenido válido mínimo
        valid_lesson = Lesson(
            user=user,
            title='Valid Lesson',
            content='Este es un contenido válido con más de 10 caracteres para la lección.',
            country='CO'
        )

        # No debería lanzar error
        try:
            valid_lesson.full_clean()
        except ValidationError:
            self.fail("Valid lesson content should not raise ValidationError")

    def test_expression_creation_with_audio(self):
        """Test: Crear expresión con archivo de audio"""
        user = User.objects.create_user(
            username='audio_test_user',
            email='audio@example.com',
            password='testpass123'
        )

        lesson = Lesson.objects.create(
            user=user,
            title='Test Lesson for Audio',
            content='Test content for audio testing',
            country='CO'
        )

        # Crear expresión con audio (simulado)
        expression = Expression.objects.create(
            lesson=lesson,
            text='¡Qué chimba!',
            meaning='¡Qué genial!',
            example='¡Qué chimba este lugar!'
        )

        self.assertEqual(expression.text, '¡Qué chimba!')
        self.assertEqual(expression.meaning, '¡Qué genial!')
        self.assertEqual(expression.lesson, lesson)
        self.assertIsNone(expression.audio)  # Sin archivo real en test

    def test_expression_validation_text_requirements(self):
        """Test: Validar requisitos del texto de expresión"""
        user = User.objects.create_user(
            username='validation_test_user',
            email='validation@example.com',
            password='testpass123'
        )

        lesson = Lesson.objects.create(
            user=user,
            title='Test Lesson for Validation',
            content='Test content for validation testing',
            country='CO'
        )

        # Texto muy corto
        short_expression = Expression(
            lesson=lesson,
            text='¡',
            meaning='Significado',
            example='Ejemplo'
        )

        with self.assertRaises(ValidationError):
            short_expression.full_clean()

        # Texto sin letras
        symbols_expression = Expression(
            lesson=lesson,
            text='!!!@@@###',
            meaning='Significado',
            example='Ejemplo'
        )

        with self.assertRaises(ValidationError):
            symbols_expression.full_clean()

        # Expresión válida
        valid_expression = Expression(
            lesson=lesson,
            text='¡Qué chimba!',
            meaning='¡Qué genial!',
            example='¡Qué chimba este lugar!'
        )

        # No debería lanzar error
        try:
            valid_expression.full_clean()
        except ValidationError:
            self.fail("Valid expression should not raise ValidationError")



    def test_forum_post_creation(self):
        """Test: Crear publicación de foro válida"""
        user = User.objects.create_user(
            username='forum_test_user',
            email='forum@example.com',
            password='testpass123'
        )

        post = ForumPost.objects.create(
            title='Test Forum Post',
            content='This is a test forum post content for testing purposes.',
            author=user,
            category='general'
        )

        self.assertEqual(post.title, 'Test Forum Post')
        self.assertEqual(post.author, user)
        self.assertEqual(post.category, 'general')
        self.assertEqual(post.views, 0)
        self.assertFalse(post.is_pinned)
        self.assertFalse(post.is_closed)

    def test_forum_post_like_functionality(self):
        """Test: Funcionalidad de likes en publicaciones del foro"""
        user1 = User.objects.create_user(
            username='forum_user1',
            email='forum1@example.com',
            password='testpass123'
        )

        user2 = User.objects.create_user(
            username='forum_user2',
            email='forum2@example.com',
            password='testpass123'
        )

        post = ForumPost.objects.create(
            title='Test Post for Likes',
            content='Test content for likes functionality',
            author=user1,
            category='general'
        )

        # Inicialmente sin likes
        self.assertEqual(post.likes.count(), 0)

        # Agregar like
        post.likes.add(user2)
        self.assertEqual(post.likes.count(), 1)
        self.assertIn(user2, post.likes.all())

        # Remover like
        post.likes.remove(user2)
        self.assertEqual(post.likes.count(), 0)
        self.assertNotIn(user2, post.likes.all())

    def test_comment_creation_and_replies(self):
        """Test: Crear comentarios y sistema de respuestas"""
        user1 = User.objects.create_user(
            username='comment_user1',
            email='comment1@example.com',
            password='testpass123'
        )

        user2 = User.objects.create_user(
            username='comment_user2',
            email='comment2@example.com',
            password='testpass123'
        )

        post = ForumPost.objects.create(
            title='Test Post for Comments',
            content='Test content for comments',
            author=user1,
            category='general'
        )

        # Crear comentario principal
        comment = Comment.objects.create(
            post=post,
            author=user2,
            content='This is a test comment'
        )

        self.assertEqual(comment.post, post)
        self.assertEqual(comment.author, user2)
        self.assertIsNone(comment.parent)

        # Crear respuesta
        reply = Comment.objects.create(
            post=post,
            author=user1,
            content='This is a reply to the comment',
            parent=comment
        )

        self.assertEqual(reply.post, post)
        self.assertEqual(reply.author, user1)
        self.assertEqual(reply.parent, comment)

        # Verificar que el comentario principal tiene la respuesta
        replies = comment.get_replies()
        self.assertIn(reply, replies)
        self.assertEqual(replies.count(), 1)