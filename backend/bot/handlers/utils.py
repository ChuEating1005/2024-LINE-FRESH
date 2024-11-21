from linebot import LineBotApi
from linebot.v3.messaging import MessagingApi, ApiClient, Configuration
from linebot.models import (
    TextSendMessage,
    FlexSendMessage
)
from django.conf import settings
from ..models import User, AudioMessage, Conversation, Question, Answer, Article, Comment

from .openAI_handlers import OpenAIHandler
import re
import json
from django.http import JsonResponse
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
######################### Default Function ###############################################
def respond_message(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

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
######################### User Function ###############################################
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



######################### Question Function ###############################################
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

######################### Answer Function ###############################################
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
        if question.response_counter == 5:
            article = generate_QA(event, question)
            question.delete()
            respond_message(event, f"回答已成功送出！恭喜成為第五名回答者！點擊下方連結觀看文章：\n{settings.CURRENT_BASE_URL}/article/{article.id}")
        else:
            respond_message(event, "回答已成功送出！")
    except Exception as e:
        print(e)
        respond_message(event, "發生錯誤，請再試一次")

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

def response_article_for_testing(event):
    bubble = {
        "type": "bubble",
        "size": "mega",  # 或 "giga" 視需要調整大小
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "請用語音功能錄製您的故事並送出，或是用文字輸入(語音輸入錄製完直接送出即可、文字輸入請點下方按鈕)",  # 問題主題
                    "wrap": True,  # 啟用換行,
                    "weight": "bold",
                    "size": "md",
                    "align": "center"  # 置中
                }
            ],
            "paddingAll": "sm"  # 減少內距
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
                        "label": "使用打字輸入發表文章",
                        "data": "action=answer",  # postback action data
                        "inputOption": "openKeyboard",
                        "fillInText": "發表文章："  # 用戶點擊按鈕後顯示的文字
                    }
                }
            ]
        }
    }
    flex_message = FlexSendMessage(
        alt_text='發表文章',
        contents={
            "type": "carousel",
            "contents": [bubble] 
        }
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

######################### Article Function ###############################################
def generate_article(event, context):
    openai = OpenAIHandler()
    articles = openai.generate_article(context)
    title_match = re.search(r"# (.+)", articles)
    description_match = re.search(r"## (.+)", articles)
    tags_match = re.search(r"### Tags\n\[(.+)\]", articles)

    if tags_match:
        tags_string = tags_match.group(1)  # 获取标签的原始字符串，如 '"tag1", "tag2"'
        # 移除多余的引号和空格
        tags = [tag.strip().strip('"') for tag in tags_string.split(",")]
    else:
        tags = []

    print(tags)
    title = title_match.group(1) if title_match else None
    description = description_match.group(1) if description_match else None

    # 创建文章并存入数据库
    articles = re.sub(r"### Tags\n\[(.+)\]", "", articles)
    article = create_article(event, title, description, articles, tags, input_text=context)
    respond_message(event, f"你的文章連結:\n{settings.CURRENT_BASE_URL}/article/{article.id}")


    
def generate_QA(event, question):
    openai = OpenAIHandler()
    answers = Answer.objects.filter(question=question)
    answers_text =  "\n".join([f"{i+1}. {answer.content}" for i, answer in enumerate(answers)])
    articles = openai.generate_QA(question.content, question.category,answers_text)
    description_match = re.search(r"## (.+)", articles)
    description = description_match.group(1) if description_match else None
    tags_match = re.search(r"### Tags\n\[(.+)\]", articles)

    if tags_match:
        tags_string = tags_match.group(1)  # 获取标签的原始字符串，如 '"tag1", "tag2"'
        # 移除多余的引号和空格
        tags = [tag.strip().strip('"') for tag in tags_string.split(",")]
    else:
        tags = []
    tags.append(question.category)
    articles = re.sub(r"### Tags\n\[(.+)\]", "", articles)
    return create_article(event, question.content, description, articles,tags, input_text=question.content + answers_text)

def create_article(event, title, description, content, tags, input_text):
    user = get_user(event)
    return Article.objects.create(title=title, author=user,
                           description=description,content=content, tags = tags, input_text = input_text)
    
def select_article(user):
    line_id = user.line_id
    # Get the rich menu ID by name
    rich_menu_questiontopic_id = get_rich_menu_id_by_name(line_bot_api2, "richmenu-article")
    if rich_menu_questiontopic_id:
        # Link the main rich menu to the user after signup
        line_bot_api2.link_rich_menu_id_to_user(line_id, rich_menu_questiontopic_id)
    else:
        print("Rich menu with the specified name not found.")

def list_all_article():
    # 查詢所有文章，按 `likes` 降序排序
    articles = Article.objects.all().order_by('-likes')

    # 將 QuerySet 轉換為 JSON 格式的列表
    articles_list = [
        {
            "title": article.title,
            "description": article.description,
            "content": article.content,
            "url": f'article/{article.id}',
            "id": article.id ,
            "tags": article.tags
        }
        for article in articles
    ]

    return articles_list

def get_article_by_id(article_id):
    article = Article.objects.get(id=article_id)
    article_json = {
            "title": article.title,
            "description": article.description,
            "content": article.content,
            "url": f'article/{article.id}',
            "id": article.id  ,
            "tags": article.tags
        }
    return article_json

def view_popular_articles(event):
    articles = Article.objects.all().order_by('-likes')[:10]
    
    if not articles:
        respond_message(event, "目前沒有任何文章")
        return
    
    bubbles = create_article_bubble(articles)

    # 創建 Carousel Flex Message
    flex_message = FlexSendMessage(
        alt_text='熱門文章',
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )
    
    # 發送訊息
    line_bot_api.reply_message(event.reply_token, flex_message)


def create_article_bubble(articles):
    # 為每個問題創建一個 bubble
    bubbles = []
    for article in articles:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": article.title, 
                        "weight": "bold",
                        "size": "md",
                        "align": "center"  # 置中
                    },
                    {
                        "type": "text",
                        "text": article.description,  
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
                                "text": f"發表時間：{article.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
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
                    "style": "link",  
                    "action": {
                        "type": "uri",  
                        "label": "查看文章",  
                        "uri": f"{settings.CURRENT_BASE_URL}/article/{article.id}"  
                    }
                }
            ]
            }
        }
        bubbles.append(bubble)
    return bubbles