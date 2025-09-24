from django.conf import settings

def google_analytics(request):
    """
    Context processor para Google Analytics
    """
    return {
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'debug': settings.DEBUG,
    }