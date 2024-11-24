from urllib.parse import parse_qsl
from linebot import LineBotApi
from django.conf import settings
from .utils import *

line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)

def handle_postback_event(event):
    user = get_user(event)
    data = dict(parse_qsl(event.postback.data))
    action = data.get('action', '')

    if action == 'choose_generation':
        generation = data.get('generation')
        print(f"User added with generation: {generation}")
        if add_user(event, generation):
            respond_message(event, f"註冊成功！")
        else:
            debug_richmenu(event)
            respond_message(event, "您已經註冊過了！跳轉到主頁")
    
    elif action == "choose_article":
        select = data.get('select')
        if select == '所有文章':
            respond_message(event, f"所有文章網頁:\n{settings.CURRENT_BASE_URL}")
        else:
            view_popular_articles(event)
        
        

