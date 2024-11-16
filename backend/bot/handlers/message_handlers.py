from linebot import LineBotApi
from linebot.models import TextSendMessage
from django.conf import settings
from .utils import *

line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)

def handle_text_message(event):
    user_message = event.message.text

    if get_user(event):
        respond_message(event, "歡迎回來！")
    else:
        add_user(event, user_message)
