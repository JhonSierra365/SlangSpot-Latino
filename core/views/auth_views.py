from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import CustomUserCreationForm
from ..models import SiteSettings, UserProfile

import logging
logger = logging.getLogger(__name__)

def home(request):
    # Obtener las configuraciones del sitio
    site_settings = SiteSettings.get_settings()
    return render(request, 'core/home.html', {
        'site_settings': site_settings,
        'video_thumbnail_url': site_settings.get_video_thumbnail_url()
    })


@login_required
def notifications_view(request):
    notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')
    return render(request, 'core/notifications.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(request.user.notifications, id=notification_id)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@login_required
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, 'Todas las notificaciones han sido marcadas como leídas.')
    return redirect('notifications') 