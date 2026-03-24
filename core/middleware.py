import gzip
import json
from django.utils.deprecation import MiddlewareMixin
import time


class CompressionMiddleware(MiddlewareMixin):
    """
    Middleware para comprimir respuestas HTTP usando gzip
    """
    
    def process_response(self, request, response):
        # Solo comprimir tipos de contenido de texto
        content_types = [
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/json',
            'text/plain',
        ]

        content_type = response.get('Content-Type', '')
        if not any(ct in content_type for ct in content_types):
            return response

        # Evitar streaming y respuestas ya comprimidas
        if getattr(response, 'streaming', False):
            return response
        if response.has_header('Content-Encoding'):
            return response

        # Solo comprimir si el cliente lo soporta
        if 'gzip' not in request.META.get('HTTP_ACCEPT_ENCODING', ''):
            return response

        # Solo comprimir respuestas suficientemente grandes
        content = getattr(response, 'content', b'')
        if not isinstance(content, (bytes, bytearray)):
            return response
        if len(content) < 500:
            return response

        # Comprimir la respuesta
        gzip_content = gzip.compress(content)
        response.content = gzip_content
        response['Content-Encoding'] = 'gzip'
        # Asegurar encabezado Vary
        vary = response.get('Vary')
        if vary:
            if 'Accept-Encoding' not in vary:
                response['Vary'] = f"{vary}, Accept-Encoding"
        else:
            response['Vary'] = 'Accept-Encoding'
        response['Content-Length'] = str(len(gzip_content))

        return response


class CacheHeadersMiddleware(MiddlewareMixin):
    """
    Middleware para agregar headers de cache apropiados
    """
    
    def process_response(self, request, response):
        # No modificar si el método no es GET o el status no es 200
        if request.method != 'GET' or response.status_code != 200:
            return response

        path = request.path or ''

        # Archivos estáticos
        if path.startswith('/static/'):
            # Solo si no está ya configurado
            if not response.has_header('Cache-Control'):
                response['Cache-Control'] = 'public, max-age=86400'  # 24 horas
            # Asegurar Vary para codificación
            vary = response.get('Vary')
            if vary:
                if 'Accept-Encoding' not in vary:
                    response['Vary'] = f"{vary}, Accept-Encoding"
            else:
                response['Vary'] = 'Accept-Encoding'
            return response

        # Archivos de media
        if path.startswith('/media/'):
            if not response.has_header('Cache-Control'):
                response['Cache-Control'] = 'public, max-age=3600'  # 1 hora
            vary = response.get('Vary')
            if vary:
                if 'Accept-Encoding' not in vary:
                    response['Vary'] = f"{vary}, Accept-Encoding"
            else:
                response['Vary'] = 'Accept-Encoding'
            return response

        # Evitar cache para admin
        if path.startswith('/admin/'):
            return response

        # Páginas HTML: no cachear contenido autenticado
        if getattr(request, 'user', None) and request.user.is_authenticated:
            # Forzar no-store para respuestas autenticadas
            response['Cache-Control'] = 'private, no-store'
            # Asegurar Vary por Cookie para fragmentos
            vary = response.get('Vary')
            if vary:
                if 'Cookie' not in vary:
                    response['Vary'] = f"{vary}, Cookie"
            else:
                response['Vary'] = 'Cookie'
            return response

        # Contenido público anónimo
        if not response.has_header('Cache-Control'):
            response['Cache-Control'] = 'public, max-age=300'  # 5 minutos

        # Asegurar Vary por Cookie (para diferenciar anónimo/autenticado en caches intermedios)
        vary = response.get('Vary')
        components = []
        if vary:
            components = [v.strip() for v in vary.split(',') if v.strip()]
        if 'Cookie' not in components:
            components.append('Cookie')
        if 'Accept-Encoding' not in components:
            components.append('Accept-Encoding')
        response['Vary'] = ', '.join(components) if components else 'Cookie, Accept-Encoding'

        return response


class PerformanceMiddleware(MiddlewareMixin):
    """
    Middleware para monitorear el rendimiento de las vistas
    """
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            # Agregar header con tiempo de respuesta para debugging
            response['X-Response-Time'] = f'{duration:.3f}s'
            
            # Log de rendimiento para respuestas lentas
            if duration > 1.0:  # Más de 1 segundo
                import logging
                logger = logging.getLogger('django.performance')
                logger.warning(
                    f'Slow response: {request.path} took {duration:.3f}s'
                )
        
        return response 