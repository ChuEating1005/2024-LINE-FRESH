from linebot import LineBotApi
from linebot.models import TextSendMessage
from django.conf import settings
from .utils import *

line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)

def handle_postback_event(event):
    data = event.postback.data

    if 'action=choose_generation' in data:
        generation = data.split('&')[1].split('=')[1]
        print(f"User added with generation: {generation}")
        add_user(event, generation)
        
