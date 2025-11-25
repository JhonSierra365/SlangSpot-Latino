document.addEventListener('DOMContentLoaded', function() {
    // Manejar me gusta de posts
    document.querySelectorAll('.like-post-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            likePost(postId, this);
        });
    });

    // Manejar me gusta de comentarios
    document.querySelectorAll('.like-comment-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.dataset.commentId;
            likeComment(commentId, this);
        });
    });
});

function likePost(postId, button) {
    fetch(`/core/forum/post/${postId}/like/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        updateLikeButton(button, data);
    })
    .catch(error => console.error('Error:', error));
}

function likeComment(commentId, button) {
    // Nota: Endpoint aún no implementado en backend.
    fetch(`/core/forum/comment/${commentId}/like/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        updateLikeButton(button, data);
    })
    .catch(error => console.error('Error:', error));
}

function updateLikeButton(button, data) {
    const icon = button.querySelector('i');
    const countSpan = button.querySelector('.likes-count');
    
    if (data.liked) {
        icon.classList.remove('far');
        icon.classList.add('fas');
        button.classList.add('liked');
    } else {
        icon.classList.remove('fas');
        icon.classList.add('far');
        button.classList.remove('liked');
    }
    
    countSpan.textContent = data.likes_count;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 