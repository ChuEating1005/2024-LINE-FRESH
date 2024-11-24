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

from .handlers.utils import list_all_article_by_topic, get_article_by_id
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
def article_list(request):
    articles = {}
    for topic in ['傳統技藝', '歷史方面', '佳餚食譜', '人生經驗', '科技新知', '其他']:
        articles[topic] = list_all_article_by_topic(topic)
    liff_id = settings.LIFF_ID 
    base_url = settings.STATIC_URL 
    return render(request, 'lobby.html', {
        'articles': articles, 
        'liff_id': liff_id,
        'base_url': base_url
    })

@csrf_exempt
def article_detail(request, article_id):
    article = get_article_by_id(article_id)
    return render(request, 'article.html', {'article': article})
