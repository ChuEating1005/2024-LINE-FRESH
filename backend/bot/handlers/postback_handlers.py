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
            respond_message(event, "發生錯誤，請再試一次")
        
        

