from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

class OwnerRequiredMixin:
    """Mixin para verificar que el usuario es el propietario del objeto."""
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Verificar diferentes campos de autor según el modelo y herencias
        if hasattr(obj, 'author'):
            owner = obj.author
        elif hasattr(obj, 'user'):
            owner = obj.user
        elif hasattr(obj, 'lesson') and hasattr(obj.lesson, 'author'):
            owner = obj.lesson.author
        else:
            owner = None
            
        if owner and owner != request.user and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para realizar esta acción.')
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class SuccessMessageMixin:
    """Mixin para manejar mensajes de éxito."""
    
    success_message = None
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response

class SoftDeleteMixin:
    """Mixin para manejar eliminación suave de objetos."""
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save()
        messages.success(request, 'Elemento eliminado exitosamente.')
        return redirect(self.get_success_url())

class SearchMixin:
    """Mixin para manejar búsquedas en listas."""
    
    search_fields = []
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '')
        if search_query:
            from django.db.models import Q
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(query)
        return queryset 