from linebot import LineBotApi
from linebot.models import TextSendMessage
from django.conf import settings
from .utils import *

line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)

def handle_text_message(event):
    user_message = event.message.text
    try:
        user = get_user(event)
        group = user.age_group
        status = user.status
        # 一般模式
        try: 
            if user_message == "使用說明":
                respond_message(event, "還沒做，自己看，不要問我。")
            elif user_message == "我要提問！":
                ask_question(user)
                update_user_status(user, 'questioning')
                respond_message(event, "請選擇感興趣的主題並輸入問題！")
            # 回答問題
            elif user_message == "我要回答問題！":
                update_user_status(user, 'answering')
                answer_question_button(event)
            elif user_message == "查看全部":
                view_all_questions(event)
            elif user_message == "特定主題":
                toggle_answertopic_richmenu(event)
                respond_message(event, "請選擇感興趣的主題！")
            elif user_message.startswith("查看主題"):
                view_question_by_topic(event)

            # 發表文章
            elif user_message == "我要發表文章！":
                response_article(event)
            elif user_message.startswith("發表文章："):
                generate_article(event, user_message)

            # 查看文章
            elif user_message == "我要查看文章！":
                select_article(user)
                respond_message(event, "請選擇要看推薦文章，還是所有文章")

            # 問問題模式
            elif status == 'questioning':
                if create_question(event, user, group):
                    respond_message(event, "問題已成功送出！請耐心等待回答")
                else:
                    respond_message(event, "發生錯誤，請再試一次")
            elif status == 'answering':
                answer_question(event, user)
            else:
                respond_message(event, "請輸入正確的指令")
            
        except Exception as e:
            print(e)
            
    except Exception as e:
        print(e)
        respond_message(event, "尚未註冊！請先選擇你的世代")

    