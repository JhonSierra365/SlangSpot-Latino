// Main JavaScript for SlangSpot Latino

document.addEventListener('DOMContentLoaded', function() {
    // Modal functionality
    const modal = document.getElementById('confirmModal');
    const modalMessage = document.getElementById('modalMessage');
    const confirmYes = document.getElementById('confirmYes');
    const confirmNo = document.getElementById('confirmNo');

    let currentCallback = null;

    // Function to show confirmation modal
    window.showConfirmModal = function(message, callback) {
        modalMessage.textContent = message;
        currentCallback = callback;
        modal.style.display = 'block';
    };

    // Modal button handlers
    confirmYes.addEventListener('click', function() {
        if (currentCallback) {
            currentCallback();
        }
        modal.style.display = 'none';
    });

    confirmNo.addEventListener('click', function() {
        modal.style.display = 'none';
        currentCallback = null;
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
            currentCallback = null;
        }
    });

    // Like functionality (AJAX)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('like-btn')) {
            e.preventDefault();
            const btn = e.target;
            const url = btn.dataset.url;
            const type = btn.dataset.type;
            const id = btn.dataset.id;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ type: type, id: id })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const countElement = btn.querySelector('.like-count') || btn.nextElementSibling;
                    if (countElement) {
                        countElement.textContent = data.likes_count;
                    }
                    btn.classList.toggle('liked', data.is_liked);
                }
            })
            .catch(error => console.error('Error:', error));
        }
    });

    // CSRF token helper
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('error');
                    isValid = false;
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Por favor, completa todos los campos requeridos.');
            }
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.alert, .message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});