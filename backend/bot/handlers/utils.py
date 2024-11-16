from linebot import LineBotApi
from linebot.models import TextSendMessage
from django.conf import settings
from ..models import User, AudioMessage, Conversation, Question, Answer, Article, Comment

line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)

def add_user(event, age_group):
    if age_group == "":
        respond_message(event, "請輸入年齡組別")
        return None
    elif age_group not in ['青世代', '銀世代']:
        respond_message(event, "請輸入正確的年齡組別")
        return None
    try:
        line_id = event.source.user_id
        profile=line_bot_api.get_profile(line_id)
        display_name = profile.display_name
        pic_url = profile.picture_url
        user = User.objects.create(line_id=line_id, display_name=display_name, pic_url=pic_url, age_group=age_group)
        respond_message(event, f"註冊成功！")
        return user
    except Exception as e:
        print(e)
        respond_message(event, "發生錯誤，請再試一次")
        return None

def get_user(event):
    try:
        user = User.objects.get(line_id=event.source.user_id)
        return user
    except User.DoesNotExist:
        return None

def respond_message(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )