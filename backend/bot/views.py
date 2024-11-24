from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, 
    PostbackEvent,
    TextMessage, 
    TextSendMessage,
    AudioMessage
)
from .handlers.message_handlers import handle_text_message
from .handlers.audio_handler import process_audio_message
from .handlers.postback_handlers import handle_postback_event
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

from .handlers.utils import list_all_article, get_article_by_id
from django.shortcuts import render
import markdown


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

@handler.add(PostbackEvent)
def handle_postback(event):
    handle_postback_event(event)

@csrf_exempt
def info(request):
    articles = list_all_article()
    return render(request, 'info.html', {'articles': articles})

@csrf_exempt
def article_detail(request, article_id):
    article = get_article_by_id(article_id)
    article_content = markdown.markdown(article["content"])
    return render(request, 'article.html', {'article': article, 'content': article_content})
