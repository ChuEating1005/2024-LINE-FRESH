from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, 
    TextMessage, 
    TextSendMessage,
    AudioMessage
)
from .handlers.message_handlers import handle_text_message
from .handlers.audio_handler import process_audio_message


handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        
        return HttpResponse('OK')
    else:
        return HttpResponseBadRequest()

# Register event handlers
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    handle_text_message(event)

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):
    process_audio_message(event)