from django.contrib.auth.models import Permission
from django.db.models import Q

def get_user_permissions(user):
    if user.is_superuser:
        return Permission.objects.all()
    return user.user_permissions.all() | Permission.objects.filter(group__user=user)

def can_edit_lesson(user, lesson):
    return user.is_superuser or lesson.user == user

def can_delete_lesson(user, lesson):
    return user.is_superuser or lesson.user == user

def can_edit_expression(user, expression):
    return user.is_superuser or expression.lesson.user == user

def can_delete_expression(user, expression):
    return user.is_superuser or expression.lesson.user == user

def can_edit_comment(user, comment):
    return user.is_superuser or comment.author == user

def can_delete_comment(user, comment):
    return user.is_superuser or comment.author == user

def can_edit_post(user, post):
    return user.is_superuser or post.author == user

def can_delete_post(user, post):
    return user.is_superuser or post.author == user 