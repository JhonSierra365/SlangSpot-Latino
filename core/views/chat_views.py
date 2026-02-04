from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
import json
import requests
import os
import logging
from ..models import Conversation, Message

logger = logging.getLogger(__name__)

@login_required
def chat(request):
    """Vista para la página de chat"""
    return render(request, 'core/chat.html')

@login_required
@require_http_methods(["GET"])
def get_chat_history(request):
    """Obtener el historial de chat del usuario"""
    # Obtener o crear conversación activa
    conversation, created = Conversation.objects.get_or_create(
        user=request.user,
        defaults={'title': f'Chat con {request.user.username}'}
    )
    
    messages = conversation.messages.all().order_by('created_at')
    messages_data = [{
        'content': msg.content,
        'is_user': msg.is_user,
        'created_at': msg.created_at.strftime('%H:%M')
    } for msg in messages]
    
    return JsonResponse({'messages': messages_data})

@login_required
@require_http_methods(["POST"])
def send_message(request):
    """Enviar un mensaje al chat"""
    try:
        data = json.loads(request.body)
        content = data.get('message', '').strip()
        
        if not content:
            return JsonResponse({'status': 'error', 'message': 'El mensaje no puede estar vacío'})
            
        conversation, created = Conversation.objects.get_or_create(
            user=request.user,
            defaults={'title': f'Chat con {request.user.username}'}
        )
        
        # Guardar mensaje del usuario
        Message.objects.create(
            conversation=conversation,
            content=content,
            is_user=True,
            read_at=timezone.now()
        )
        
        conversation.update_last_message()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_http_methods(["POST"])
def get_ai_response(request):
    """Obtener respuesta de la IA"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        conversation = Conversation.objects.filter(user=request.user).order_by('-last_message_at').first()
        if not conversation:
            return JsonResponse({'status': 'error', 'message': 'No hay conversación activa'})

        # Integration with OpenAI
        api_key = os.environ.get('OPENAI_API_KEY')
        ai_response_text = ""

        if api_key:
            try:
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'gpt-3.5-turbo',
                        'messages': [
                            {"role": "system", "content": "Eres un experto en slang y jerga latinoamericana. Ayudas a los usuarios a entender el español de la calle de diferentes países."},
                            {"role": "user", "content": user_message}
                        ]
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    ai_response_text = response.json()['choices'][0]['message']['content']
                else:
                    logger.error(f"OpenAI API Error: {response.status_code} - {response.text}")
                    ai_response_text = "Lo siento, tuve un problema técnico conectando con mi cerebro. Intenta de nuevo más tarde."
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}")
                ai_response_text = "Ocurrió un error al procesar tu mensaje. Por favor intenta más tarde."
        else:
            # Fallback if no API key is configured
            ai_response_text = "¡Hola! Para que pueda responderte inteligentemente, el administrador debe configurar la variable de entorno OPENAI_API_KEY."
            logger.warning("OPENAI_API_KEY not found in environment variables.")
        
        # Guardar respuesta de la IA
        Message.objects.create(
            conversation=conversation,
            content=ai_response_text,
            is_user=False
        )
        
        conversation.update_last_message()
        
        return JsonResponse({'response': ai_response_text})
    except Exception as e:
        logger.error(f"Error in get_ai_response: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})
 