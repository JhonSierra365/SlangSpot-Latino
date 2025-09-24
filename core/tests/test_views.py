from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Lesson, Expression, ForumPost, Comment, Practice, UserProfile


class HomeViewTest(TestCase):
    """Tests para la vista de inicio"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_home_view_accessible(self):
        """Test: La vista de inicio es accesible"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
    
    def test_home_view_with_authenticated_user(self):
        """Test: Vista de inicio con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.context)


class AuthViewsTest(TestCase):
    """Tests para las vistas de autenticación"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_registro_view_get(self):
        """Test: Vista de registro con GET"""
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/registro.html')
        self.assertIn('form', response.context)
    
    def test_registro_view_post_valid(self):
        """Test: Vista de registro con datos válidos"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(reverse('core:register'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_registro_view_post_invalid(self):
        """Test: Vista de registro con datos inválidos"""
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'newpass123',
            'password2': 'differentpass123'
        }
        response = self.client.post(reverse('core:register'), form_data)
        self.assertEqual(response.status_code, 200)  # Stay on form page
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_login_view_get(self):
        """Test: Vista de login con GET"""
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')
        self.assertIn('form', response.context)
    
    def test_login_view_post_valid(self):
        """Test: Vista de login con credenciales válidas"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('core:login'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_login_view_post_invalid(self):
        """Test: Vista de login con credenciales inválidas"""
        form_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('core:login'), form_data)
        self.assertEqual(response.status_code, 200)  # Stay on form page
    
    def test_logout_view(self):
        """Test: Vista de logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class LessonViewsTest(TestCase):
    """Tests para las vistas de lecciones"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.lesson = Lesson.objects.create(
            user=self.user,
            title='Test Lesson',
            content='Test content for the lesson',
            country='CO'
        )
    
    def test_lesson_list_view_requires_login(self):
        """Test: Vista de lista de lecciones requiere login"""
        response = self.client.get(reverse('core:lesson_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_lesson_list_view_with_login(self):
        """Test: Vista de lista de lecciones con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:lesson_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/lessons_index.html')
        self.assertIn('lessons', response.context)
    
    def test_lesson_detail_view(self):
        """Test: Vista de detalle de lección"""
        response = self.client.get(reverse('core:lesson_detail', kwargs={'pk': self.lesson.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/lesson_detail.html')
        self.assertEqual(response.context['lesson'], self.lesson)
    
    def test_lesson_create_view_requires_login(self):
        """Test: Vista de crear lección requiere login"""
        response = self.client.get(reverse('core:create_lesson'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_lesson_create_view_with_login(self):
        """Test: Vista de crear lección con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:create_lesson'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/create_lesson.html')
        self.assertIn('form', response.context)
    
    def test_lesson_create_view_post_valid(self):
        """Test: Crear lección con datos válidos"""
        self.client.login(username='testuser', password='testpass123')
        form_data = {
            'title': 'New Test Lesson',
            'content': 'New test content for the lesson',
            'country': 'MX',
            'level': 'intermediate',
            'category': 'slang'
        }
        response = self.client.post(reverse('core:create_lesson'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Lesson.objects.filter(title='New Test Lesson').exists())
    
    def test_lesson_edit_view_owner_only(self):
        """Test: Solo el propietario puede editar la lección"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.get(reverse('core:edit_lesson', kwargs={'pk': self.lesson.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_lesson_edit_view_owner_access(self):
        """Test: El propietario puede editar la lección"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:edit_lesson', kwargs={'pk': self.lesson.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/edit_lesson.html')


class ForumViewsTest(TestCase):
    """Tests para las vistas del foro"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = ForumPost.objects.create(
            title='Test Post',
            content='Test content for the post',
            author=self.user
        )
    
    def test_forum_index_view(self):
        """Test: Vista de índice del foro"""
        response = self.client.get(reverse('core:forum_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/forum_index.html')
        self.assertIn('object_list', response.context)
    
    def test_post_detail_view(self):
        """Test: Vista de detalle de post"""
        response = self.client.get(reverse('core:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/post_detail.html')
        self.assertEqual(response.context['post'], self.post)
    
    def test_create_post_view_requires_login(self):
        """Test: Vista de crear post requiere login"""
        response = self.client.get(reverse('core:create_post'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_create_post_view_with_login(self):
        """Test: Vista de crear post con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:create_post'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/create_post.html')
        self.assertIn('form', response.context)
    
    def test_create_post_view_post_valid(self):
        """Test: Crear post con datos válidos"""
        self.client.login(username='testuser', password='testpass123')
        form_data = {
            'title': 'New Test Post',
            'content': 'New test content for the post',
            'category': 'general'
        }
        response = self.client.post(reverse('core:create_post'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(ForumPost.objects.filter(title='New Test Post').exists())


class SecurityTest(TestCase):
    """Tests de seguridad básicos"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
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
    
    def test_csrf_protection(self):
        """Test: Protección CSRF en formularios"""
        # Intentar hacer POST sin CSRF token
        response = self.client.post(reverse('core:create_lesson'), {
            'title': 'Test Lesson',
            'content': 'Test content',
            'country': 'CO'
        })
        self.assertEqual(response.status_code, 403)  # CSRF verification failed
    
    def test_xss_protection(self):
        """Test: Protección contra XSS"""
        self.client.login(username='testuser', password='testpass123')
        malicious_content = '<script>alert("XSS")</script>'
        form_data = {
            'title': 'Test Lesson',
            'content': malicious_content,
            'country': 'CO'
        }
        response = self.client.post(reverse('core:create_lesson'), form_data)
        # El contenido malicioso debería ser escapado en la respuesta
        if response.status_code == 200:  # Si hay errores de validación
            self.assertNotIn('<script>', str(response.content))
    
    def test_sql_injection_protection(self):
        """Test: Protección contra SQL injection"""
        self.client.login(username='testuser', password='testpass123')
        malicious_title = "'; DROP TABLE core_lesson; --"
        form_data = {
            'title': malicious_title,
            'content': 'Test content',
            'country': 'CO'
        }
        response = self.client.post(reverse('core:create_lesson'), form_data)
        # La aplicación no debería fallar con contenido malicioso
        self.assertNotEqual(response.status_code, 500) 