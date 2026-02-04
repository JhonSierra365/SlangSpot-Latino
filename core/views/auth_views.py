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

def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # El perfil se crea automáticamente con la señal post_save
                # UserProfile creation handled by signal

                # Specify the authentication backend explicitly
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, '¡Registro exitoso! Bienvenido a SlangSpot.')
                return redirect('home')

            except Exception as e:
                # Log del error para debugging
                logger.error(f"Error durante el registro: {e}")
                messages.error(request, 'Ha ocurrido un error durante el registro. Por favor, inténtalo de nuevo.')
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

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