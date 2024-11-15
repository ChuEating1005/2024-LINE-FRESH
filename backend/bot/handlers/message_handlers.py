from linebot import LineBotApi
from linebot.models import TextSendMessage
from django.conf import settings

line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)

def handle_text_message(event):
    user_message = event.message.text

    # 根據文字訊息執行不同邏輯
    if user_message == "Hello":
        reply = "Hi! How can I assist you?"
    elif user_message == "Help":
        reply = "Here are some commands you can try:\n1. Hello\n2. Help"
    else:
        reply = f"You said: {user_message}"

    # 回覆訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )
