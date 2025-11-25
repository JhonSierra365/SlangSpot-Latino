from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .permissions import (
    can_edit_lesson, can_delete_lesson,
    can_edit_expression, can_delete_expression,
    can_edit_comment, can_delete_comment,
    can_edit_post, can_delete_post
)


def permission_required(permission_func, object_attr, error_message, redirect_url_func):
    """
    Decorador genérico para verificar permisos.

    Args:
        permission_func: Función que verifica el permiso (user, obj) -> bool
        object_attr: Nombre del atributo donde está el objeto en la función view
        error_message: Mensaje de error a mostrar
        redirect_url_func: Función que retorna la URL de redirect (obj) -> str
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            obj = getattr(view_func, object_attr, None)
            if obj is None:
                messages.error(request, 'Objeto no encontrado.')
                return redirect('home')

            if not permission_func(request.user, obj):
                messages.error(request, error_message)
                return redirect(redirect_url_func(obj))

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('core:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def lesson_edit_required(view_func):
    return permission_required(
        can_edit_lesson,
        'lesson',
        'No tienes permiso para editar esta lección.',
        lambda lesson: f'/lessons/{lesson.id}/'
    )(view_func)

def lesson_delete_required(view_func):
    return permission_required(
        can_delete_lesson,
        'lesson',
        'No tienes permiso para eliminar esta lección.',
        lambda lesson: f'/lessons/{lesson.id}/'
    )(view_func)

def expression_edit_required(view_func):
    return permission_required(
        can_edit_expression,
        'expression',
        'No tienes permiso para editar esta expresión.',
        lambda expression: f'/lessons/{expression.lesson.id}/'
    )(view_func)

def expression_delete_required(view_func):
    return permission_required(
        can_delete_expression,
        'expression',
        'No tienes permiso para eliminar esta expresión.',
        lambda expression: f'/lessons/{expression.lesson.id}/'
    )(view_func)

def comment_edit_required(view_func):
    return permission_required(
        can_edit_comment,
        'comment',
        'No tienes permiso para editar este comentario.',
        lambda comment: f'/lessons/{comment.expression.lesson.id}/'
    )(view_func)

def comment_delete_required(view_func):
    return permission_required(
        can_delete_comment,
        'comment',
        'No tienes permiso para eliminar este comentario.',
        lambda comment: f'/lessons/{comment.expression.lesson.id}/'
    )(view_func)

def post_edit_required(view_func):
    return permission_required(
        can_edit_post,
        'post',
        'No tienes permiso para editar esta publicación.',
        lambda post: f'/core/forum/post/{post.id}/'
    )(view_func)

def post_delete_required(view_func):
    return permission_required(
        can_delete_post,
        'post',
        'No tienes permiso para eliminar esta publicación.',
        lambda post: f'/core/forum/post/{post.id}/'
    )(view_func)