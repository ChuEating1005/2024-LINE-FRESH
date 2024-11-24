from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
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
from .models import Article
from .handlers.utils import list_all_article_by_topic, get_article_by_id
from django.shortcuts import render, get_object_or_404
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
    # 獲取所有文章並按主題分組
    articles_by_topic = {}
    topics = ['傳統技藝', '歷史文化', '佳餚食譜', '人生經驗', '科技新知', '其他']
    
    # 主題描述
    topic_descriptions = {
        '傳統技藝': '傳統技藝是文化傳承的象徵，這些技藝蘊含著世代智慧與藝術價值。將珍貴的手藝藉由文章傳遞，讓傳統在現代重焕生機。',
        '歷史文化': '歷史文化是民族的根基，記錄著重要的故事與價值觀。這些文化底蘊都能成為世代交流的橋梁，也是重要的文化資產',
        '佳餚食譜': '美食是情感的紐帶，記錄著重要的味道與地方特色。佳餚食譜不僅連結了味蕾，更也讓美味在每個廚房中得以延續。',
        '人生經驗': '人生經驗是寶貴的智慧庫。無論是生活哲學、應對挑戰以及成功與失敗的故事，都是專屬生命的重要篇章。',
        '科技新知': '科技是現代生活的驅動力，青世代熟悉數位技術，銀世代則對新科技抱有學習熱情。科技世界將為不同世代帶來改變。',
        '其他': '人們對生命的體驗不侷限在一定的區塊，在這個主題，一切意想不到都將可能為別的生命併發新的體驗。'
    }
    
    # 主題圖片
    topic_images = {
        '傳統技藝': 'https://firebasestorage.googleapis.com/v0/b/linefresh-2024.firebasestorage.app/o/images%2Fimg_list%2F1.png?alt=media&token=be508a88-072f-4322-b3f1-3159ac037db6',
        '歷史文化': 'https://firebasestorage.googleapis.com/v0/b/linefresh-2024.firebasestorage.app/o/images%2Fimg_list%2F2.png?alt=media&token=9d3bfda2-c421-4deb-b78b-e6417ccecefc',
        '佳餚食譜': 'https://firebasestorage.googleapis.com/v0/b/linefresh-2024.firebasestorage.app/o/images%2Fimg_list%2F3.png?alt=media&token=d2b4e8c7-1e12-47cf-a600-59a27f87f941',
        '人生經驗': 'https://firebasestorage.googleapis.com/v0/b/linefresh-2024.firebasestorage.app/o/images%2Fimg_list%2F4.png?alt=media&token=c1d7f025-1526-49e8-86fc-ae07a6702128',
        '科技新知': 'https://firebasestorage.googleapis.com/v0/b/linefresh-2024.firebasestorage.app/o/images%2Fimg_list%2F5.png?alt=media&token=0c7b298b-65f0-4003-bddd-05ce9cf43863',
        '其他': 'https://firebasestorage.googleapis.com/v0/b/linefresh-2024.firebasestorage.app/o/images%2Fimg_list%2F6.png?alt=media&token=3754ecb8-f59a-4d2b-a37b-40352bbbec7a'
    }
    
    for topic in topics:
        articles_by_topic[topic] = Article.objects.filter(category=topic)
    
    context = {
        'articles': articles_by_topic,
        'topics': topics,
        'topic_descriptions': topic_descriptions,
        'topic_images': topic_images,
        'liff_id': settings.LIFF_ID
    }
    
    return render(request, 'lobby.html', context)

@csrf_exempt
def article_detail(request, article_id):
    article = Article.objects.filter(id=article_id).first()
    user_id = request.session.get('line_user_id')
    # 獲取相關文章，排除當前文章
    related_articles = Article.objects.exclude(id=article_id).filter(
        # 其他篩選條件，例如相同標籤或分類
        category=article.category
    )[:5]  # 限制顯示數量
    context = {
        'article': get_article_by_id(article_id),
        'user_id': user_id,
        'related_articles':related_articles,
    }
    return render(request, 'article.html', context)


@csrf_exempt
def like_article(request, article_id):
    article = Article.objects.filter(id=article_id).first()
    user_id = request.session.get('line_user_id')  # 從 session 獲取 LINE 用戶 ID
    
    # 檢查用戶是否已經按過讚
    if not article.liked_by:  # 如果 liked_by 為 None
        article.liked_by = []
    
    is_liked = user_id in article.liked_by
    
    if is_liked:
        # 如果已經按過讚，取消讚
        article.liked_by.remove(user_id)
        article.likes = max(0, article.likes - 1)  # 確保讚數不會小於 0
    else:
        # 如果還沒按讚，添加讚
        article.liked_by.append(user_id)
        article.likes += 1
    
    article.save()
    
    return JsonResponse({
        'success': True,
        'likes': article.likes,
        'is_liked': not is_liked  # 返回新的狀態
    })