from linebot import LineBotApi
from linebot.v3.messaging import MessagingApi, ApiClient, Configuration
from linebot.models import (
    TextSendMessage,
    FlexSendMessage
)
from django.conf import settings
from ..models import User, AudioMessage, Conversation, Question, Answer, Article, Comment

configuration = Configuration(access_token=settings.LINE_ACCESS_TOKEN)
line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)
line_bot_api2 = MessagingApi(ApiClient(configuration))
color_map = {
    '佳餚食譜': '#CA7373',
    '健康養生': '#859F3D',
    '人生經驗': '#E07B39',
    '傳統技藝': '#605678',
    '歷史方面': '#AB886D',
    '其他': '#B7B7B7'
}


def get_rich_menu_id_by_name(line_bot_api, rich_menu_name):
    try:        
        # Fetch all rich menus
        response = line_bot_api.get_rich_menu_list()
        rich_menus = response.richmenus
        
        # Search for the rich menu by name
        for rich_menu in rich_menus:
            if rich_menu.name == rich_menu_name:
                return rich_menu.rich_menu_id
        return None
    except Exception as e:
        print(f"Failed to retrieve rich menu list. Error: {e}")
        return None

def add_user(event, age_group):
    if age_group == "":
        respond_message(event, "請輸入年齡組別")
        return None
    elif age_group not in ['青世代', '銀世代']:
        respond_message(event, "請輸入正確的年齡組別")
        return None
    try:
        line_id = event.source.user_id
        profile = line_bot_api.get_profile(line_id)
        display_name = profile.display_name
        pic_url = profile.picture_url
        user = User.objects.create(line_id=line_id, display_name=display_name, pic_url=pic_url, age_group=age_group)
        
        # Get the rich menu ID by name
        rich_menu_main_id = get_rich_menu_id_by_name(line_bot_api2, "richmenu-main")
        if rich_menu_main_id:
            # Link the main rich menu to the user after signup
            line_bot_api2.link_rich_menu_id_to_user(line_id, rich_menu_main_id)
        else:
            print("Rich menu with the specified name not found.")
        
        return user
    except Exception as e:
        print(e)
        return None

def get_user(event):
    try:
        user = User.objects.get(line_id=event.source.user_id)
        return user
    except User.DoesNotExist:
        return None

def update_user_status(user, status):
    user.status = status
    user.save()

def ask_question(user):
    line_id = user.line_id
    # Get the rich menu ID by name
    rich_menu_questiontopic_id = get_rich_menu_id_by_name(line_bot_api2, "richmenu-questiontopic")
    if rich_menu_questiontopic_id:
        # Link the main rich menu to the user after signup
        line_bot_api2.link_rich_menu_id_to_user(line_id, rich_menu_questiontopic_id)
    else:
        print("Rich menu with the specified name not found.")

def create_question(event, user, group):
    try:
        message = event.message.text
        (topic, content) = message.split("\n")
        topic = topic.replace("主題：", "").strip()
        content = content.replace("你的問題：", "")
        print(f"topic: {topic}, content: {content}")
        question = Question.objects.create(asker=user, content=content, category=topic)
        return question
    except Exception as e:
        print(e)
        return None

def answer_question_button(event):
    flex_message = FlexSendMessage(
        alt_text='請選擇要查看的問題',
        contents={
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "請選擇要查看的問題：",
                                "size": "md",
                                "weight": "regular",
                                "wrap": True
                            }
                        ],
                        "backgroundColor": "#F5F5F5",
                        "paddingAll": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": [
                            {
                                "type": "button",
                                "style": "link",
                                "height": "sm",
                                "action": {
                                    "type": "message",
                                    "label": "查看全部",
                                    "text": "查看全部"
                                },
                                "color": "#3A6D8C"
                            },
                            {
                                "type": "button",
                                "style": "link",
                                "height": "sm",
                                "action": {
                                    "type": "message",
                                    "label": "特定主題",
                                    "text": "特定主題"
                                },
                                "color": "#3A6D8C"
                            }
                        ],
                        "paddingAll": "md"
                    }
                ],
                "paddingAll": "none"
            }
        }
    )
    
    # 發送訊息
    line_bot_api.reply_message(event.reply_token, flex_message)

def view_all_questions(event):
    # 從資料庫獲取所有問題
    questions = Question.objects.all().order_by('-category', '-created_at')
    
    if not questions:
        respond_message(event, "目前沒有任何問題")
        return
    
    bubbles = create_question_bubble(questions)

    # 創建 Carousel Flex Message
    flex_message = FlexSendMessage(
        alt_text='所有問題',
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )
    
    # 發送訊息
    line_bot_api.reply_message(event.reply_token, flex_message)

def toggle_answertopic_richmenu(event):
    line_id = event.source.user_id
    rich_menu_answertopic_id = get_rich_menu_id_by_name(line_bot_api2, "richmenu-answertopic")
    line_bot_api2.link_rich_menu_id_to_user(line_id, rich_menu_answertopic_id)

def view_question_by_topic(event):
    topic = event.message.text.replace("查看主題:", "").strip()
    questions = Question.objects.filter(category=topic).order_by('-created_at')
    if not questions:
        respond_message(event, "目前沒有任何問題")
        return
    bubbles = create_question_bubble(questions)
    flex_message = FlexSendMessage(
        alt_text='特定主題問題',
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

def answer_question(event, user):
    try:
        message = event.message.text
        (question_id, answer) = message.split("\n")
        question_id = question_id.replace("問題編號：", "").strip()
        answer = answer.replace("你的回答：", "").strip()
        question = Question.objects.get(id=question_id)
        Answer.objects.create(question=question, responder=user, content=answer)
        question.status = 'answered'
        question.response_counter += 1
        question.save()
        respond_message(event, "回答已成功送出！")
    except Exception as e:
        print(e)
        respond_message(event, "發生錯誤，請再試一次")
    

def respond_message(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

def create_question_bubble(questions):
    # 為每個問題創建一個 bubble
    bubbles = []
    for question in questions:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": question.category,  # 問題主題
                        "weight": "bold",
                        "color": color_map[question.category],
                        "size": "md",
                        "align": "center"  # 置中
                    },
                    {
                        "type": "text",
                        "text": question.content,  # 問題內容
                        "wrap": True,
                        "weight": "regular",
                        "size": "sm",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"提問時間：{question.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                                "size": "xs",
                                "color": "#8C8C8C",
                                "wrap": True
                            }
                        ],
                        "margin": "md"
                    }
                ],
                "paddingAll": "md"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "我來回答",
                            "data": f"action=answer",
                            "inputOption": "openKeyboard",
                            "fillInText": f"問題編號：{question.id}\n你的回答："
                        },
                        "color": color_map[question.category]
                    }
                ]
            }
        }
        bubbles.append(bubble)
    return bubbles