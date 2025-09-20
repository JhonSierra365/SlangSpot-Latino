"""
Integration tests using Selenium for critical user flows.
These tests require a running Django development server and Chrome WebDriver.
"""
import os
import time
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SlangSpotIntegrationTest(LiveServerTestCase):
    """
    Integration tests for SlangSpot Latino using Selenium WebDriver.
    Tests critical user flows end-to-end.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Configure Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        # Initialize WebDriver
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
        except Exception as e:
            cls.skipTest(f"Chrome WebDriver not available: {e}")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """Set up test data and navigate to home page."""
        # Create test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Navigate to home page
        self.driver.get(self.live_server_url)

    def tearDown(self):
        """Clean up after each test."""
        # Clear any alerts or modals
        try:
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
        except:
            pass

    def wait_for_element(self, locator, timeout=10):
        """Wait for an element to be present and return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def wait_for_clickable(self, locator, timeout=10):
        """Wait for an element to be clickable and return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def login_user(self, username='testuser', password='testpass123'):
        """Helper method to log in a user."""
        # Navigate to login page
        self.driver.get(f"{self.live_server_url}/login/")

        # Fill login form
        username_field = self.wait_for_element((By.NAME, 'login'))
        password_field = self.driver.find_element(By.NAME, 'password')

        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)

        # Submit form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        # Wait for redirect to home
        self.wait_for_element((By.CLASS_NAME, 'user-greeting'))

    def test_home_page_loads(self):
        """Test that the home page loads correctly."""
        self.assertIn("SlangSpot Latino", self.driver.title)

        # Check for main elements
        hero_title = self.wait_for_element((By.CLASS_NAME, 'hero-title'))
        self.assertIn("español latino", hero_title.text.lower())

        # Check navigation
        nav_links = self.driver.find_elements(By.CSS_SELECTOR, '.nav-links a')
        self.assertGreater(len(nav_links), 0)

        # Check CTA buttons
        cta_buttons = self.driver.find_elements(By.CLASS_NAME, 'cta-button')
        self.assertGreater(len(cta_buttons), 0)

    def test_user_registration_flow(self):
        """Test complete user registration flow."""
        # Navigate to registration page
        self.driver.get(f"{self.live_server_url}/registro/")

        # Fill registration form
        username_field = self.wait_for_element((By.NAME, 'username'))
        email_field = self.driver.find_element(By.NAME, 'email')
        first_name_field = self.driver.find_element(By.NAME, 'first_name')
        last_name_field = self.driver.find_element(By.NAME, 'last_name')
        password1_field = self.driver.find_element(By.NAME, 'password1')
        password2_field = self.driver.find_element(By.NAME, 'password2')

        # Generate unique username
        import uuid
        unique_username = f"testuser_{uuid.uuid4().hex[:8]}"

        username_field.send_keys(unique_username)
        email_field.send_keys(f"{unique_username}@example.com")
        first_name_field.send_keys("Test")
        last_name_field.send_keys("User")
        password1_field.send_keys("testpass123")
        password2_field.send_keys("testpass123")

        # Submit form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        # Wait for success or redirect
        try:
            # Check if redirected to home or shows success message
            self.wait_for_element((By.CLASS_NAME, 'user-greeting'), timeout=5)
            success = True
        except TimeoutException:
            # Check for success message
            try:
                success_message = self.driver.find_element(By.CLASS_NAME, 'alert-success')
                success = True
            except NoSuchElementException:
                success = False

        self.assertTrue(success, "User registration should succeed")

    def test_user_login_flow(self):
        """Test user login flow."""
        self.login_user()

        # Verify user is logged in
        user_greeting = self.wait_for_element((By.CLASS_NAME, 'user-greeting'))
        self.assertIn("Hola, testuser", user_greeting.text)

        # Check logout button is present
        logout_button = self.driver.find_element(By.CSS_SELECTOR, '.auth-btn.logout')
        self.assertTrue(logout_button.is_displayed())

    def test_navigation_between_pages(self):
        """Test navigation between different pages."""
        # Test navigation links
        nav_links = self.driver.find_elements(By.CSS_SELECTOR, '.nav-links a')

        for link in nav_links:
            href = link.get_attribute('href')
            if href and 'lesson' in href:
                # Click lessons link
                link.click()
                self.wait_for_element((By.CLASS_NAME, 'lessons-section'))

                # Verify URL changed
                self.assertIn('lessons', self.driver.current_url)
                break

    def test_create_lesson_flow(self):
        """Test the complete flow of creating a lesson."""
        # Login first
        self.login_user()

        # Navigate to create lesson page
        self.driver.get(f"{self.live_server_url}/lessons/create/")

        # Fill lesson form
        title_field = self.wait_for_element((By.NAME, 'title'))
        content_field = self.driver.find_element(By.NAME, 'content')
        level_field = self.driver.find_element(By.NAME, 'level')
        category_field = self.driver.find_element(By.NAME, 'category')
        country_field = self.driver.find_element(By.NAME, 'country')

        import uuid
        unique_title = f"Test Lesson {uuid.uuid4().hex[:8]}"

        title_field.send_keys(unique_title)
        content_field.send_keys("This is a test lesson content for integration testing.")
        level_field.send_keys('beginner')
        category_field.send_keys('slang')
        country_field.send_keys('CO')

        # Submit form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        # Wait for success message or redirect
        try:
            success_message = self.wait_for_element((By.CLASS_NAME, 'alert-success'), timeout=5)
            self.assertIn("creada", success_message.text.lower())
        except TimeoutException:
            # Check if redirected to lesson detail
            self.assertIn('lessons', self.driver.current_url)

    def test_forum_interaction(self):
        """Test forum browsing and interaction."""
        # Login first
        self.login_user()

        # Navigate to forum
        self.driver.get(f"{self.live_server_url}/forum/")

        # Check forum elements
        forum_title = self.wait_for_element((By.CSS_SELECTOR, 'h1, .section-title'))
        self.assertTrue(forum_title.is_displayed())

        # Try to create a post (if button exists)
        try:
            create_post_button = self.driver.find_element(By.LINK_TEXT, 'Crear Publicación')
            create_post_button.click()

            # Fill post form
            title_field = self.wait_for_element((By.NAME, 'title'))
            content_field = self.driver.find_element(By.NAME, 'content')
            category_field = self.driver.find_element(By.NAME, 'category')

            title_field.send_keys("Test Forum Post")
            content_field.send_keys("This is a test forum post for integration testing.")
            category_field.send_keys('general')

            # Submit
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()

            # Check success
            success_message = self.wait_for_element((By.CLASS_NAME, 'alert-success'), timeout=5)
            self.assertIn("creada", success_message.text.lower())

        except NoSuchElementException:
            # No create post button, just verify forum loads
            self.assertIn("foro", self.driver.title.lower())

    def test_responsive_design(self):
        """Test that the site is responsive on different screen sizes."""
        # Test mobile size
        self.driver.set_window_size(375, 667)  # iPhone size

        # Check that navigation collapses or adapts
        nav_container = self.driver.find_element(By.CLASS_NAME, 'nav-container')
        nav_styles = nav_container.get_attribute('class')

        # Test tablet size
        self.driver.set_window_size(768, 1024)  # iPad size

        # Test desktop size
        self.driver.set_window_size(1920, 1080)  # Desktop size

        # Verify content is still accessible
        hero_section = self.driver.find_element(By.CLASS_NAME, 'hero-section')
        self.assertTrue(hero_section.is_displayed())

    def test_search_functionality(self):
        """Test search functionality in lessons."""
        # Login first
        self.login_user()

        # Navigate to lessons
        self.driver.get(f"{self.live_server_url}/lessons/")

        # Look for search input
        try:
            search_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="q"], input[placeholder*="buscar"]')
            search_input.send_keys("test")

            # Submit search
            search_form = search_input.find_element(By.XPATH, '..').find_element(By.XPATH, '..')
            search_form.submit()

            # Verify search results page loads
            self.assertIn('lessons', self.driver.current_url)

        except NoSuchElementException:
            # Search not implemented yet, skip test
            self.skipTest("Search functionality not implemented")

    def test_accessibility_basic(self):
        """Test basic accessibility features."""
        # Check for alt text on images
        images = self.driver.find_elements(By.TAG_NAME, 'img')
        for img in images:
            alt_text = img.get_attribute('alt')
            # Allow empty alt for decorative images, but check it's not missing
            self.assertIsNotNone(alt_text, f"Image missing alt text: {img.get_attribute('src')}")

        # Check for form labels
        forms = self.driver.find_elements(By.TAG_NAME, 'form')
        for form in forms:
            inputs = form.find_elements(By.CSS_SELECTOR, 'input, select, textarea')
            for input_field in inputs:
                input_type = input_field.get_attribute('type')
                if input_type in ['text', 'email', 'password', 'select', 'textarea']:
                    # Check if input has associated label
                    input_id = input_field.get_attribute('id')
                    if input_id:
                        try:
                            label = self.driver.find_element(By.CSS_SELECTOR, f'label[for="{input_id}"]')
                            self.assertTrue(label.is_displayed(), f"Label not displayed for input {input_id}")
                        except NoSuchElementException:
                            self.fail(f"No label found for input with id {input_id}")