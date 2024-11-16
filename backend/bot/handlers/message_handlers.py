from linebot import LineBotApi
from linebot.models import TextSendMessage
from django.conf import settings
from .utils import *

line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)

def handle_text_message(event):
    user_message = event.message.text

    if user := get_user(event):
        group = user.age_group
        status = user.status
        # 一般模式
        if status == 'idle':
            if user_message == "我要問問題！":
                update_user_status(user, 'questioning')
                respond_message(event, "請輸入您的問題！")
            elif user_message == "我要發表文章！":
                update_user_status(user, 'writing')
                respond_message(event, "請開始撰寫您的文章！文字或是語音輸入都可以")
            elif user_message == "我要回答問題！":
                update_user_status(user, 'answering')
                respond_message(event, "請開始回答問題！文字或是語音輸入都可以")
            else:
                respond_message(event, "請輸入正確的指令")
        # 問問題模式
        elif status == 'questioning':
            if create_question(event, user, group):
                respond_message(event, "問題已成功送出！請耐心等待回答")
                update_user_status(user, 'idle')
            else:
                respond_message(event, "發生錯誤，請再試一次")
    else:
        if add_user(event, user_message):
            respond_message(event, f"註冊成功！")
        else:
            respond_message(event, "發生錯誤，請再試一次")
