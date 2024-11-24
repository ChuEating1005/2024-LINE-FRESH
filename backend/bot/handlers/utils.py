from linebot import LineBotApi
from linebot.v3.messaging import MessagingApi, ApiClient, Configuration
from linebot.models import (
    TextSendMessage,
    FlexSendMessage
)
from django.conf import settings
from ..models import User, AudioMessage, Conversation, Question, Answer, Article, Comment, Image
from .openAI_handlers import OpenAIHandler
import re
import json
from django.http import JsonResponse
from .image_generation import generate_images_from_text


configuration = Configuration(access_token=settings.LINE_ACCESS_TOKEN)
liff_id = settings.LIFF_ID
line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)
line_bot_api2 = MessagingApi(ApiClient(configuration))

color_map = {
    '傳統技藝': '#DBD4C6',
    '歷史文化': '#7D6252',
    '佳餚食譜': '#A2AFA6', 
    '人生經驗': '#AB8C83',
    '科技新知': '#8E9AA8',
    '其他': '#D2D2D0'
}
color_map_text = {
    '傳統技藝': '#25231f',
    '歷史文化': '#fffded',
    '佳餚食譜': '#1b1f1c', 
    '人生經驗': '#f5f5f5',
    '科技新知': '#f6faff',
    '其他': '#333331'
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

def debug_richmenu(event):
    line_id = event.source.user_id
    profile = line_bot_api.get_profile(line_id)
    # Get the rich menu ID by name
    rich_menu_main_id = get_rich_menu_id_by_name(line_bot_api2, "richmenu-main")
    if rich_menu_main_id:
        # Link the main rich menu to the user after signup
        line_bot_api2.link_rich_menu_id_to_user(line_id, rich_menu_main_id)
    else:
        print("Rich menu with the specified name not found.")

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
    bubble = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "請選擇要查看的問題：",
                    "wrap": True,
                    "weight": "bold", 
                    "size": "lg",
                    "align": "center",
                    "color": "#25231f"
                }
            ],
            "paddingAll": "xl",
            "backgroundColor": "#DBD4C6",
            "height": "50px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "md",
                    "margin": "md",
                    "action": {
                        "type": "message",
                        "label": "🔎 查看全部  ",
                        "text": "查看全部"
                    },
                    "color": "#808C83"
                },
                {
                    "type": "button",
                    "style": "primary",
                    "height": "md", 
                    "margin": "md",
                    "action": {
                        "type": "message",
                        "label": "📌 特定主題  ",
                        "text": "特定主題"
                    },
                    "color": "#7D6252"
                }
            ],
            "paddingAll": "md",
            "backgroundColor": "#DBD4C6"
        }
    }
    flex_message = FlexSendMessage(
        alt_text='請選擇要查看的問題',
        contents={
            "type": "carousel",
            "contents": [bubble]
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
        asker = question.asker
        Answer.objects.create(question=question, responder=user, content=answer)
        question.status = 'answered'
        question.response_counter += 1
        question.save()
        respond_message(event, "回答已成功送出！")
        if question.response_counter == 5:
            article = generate_QA(event, question)
            flex_message_asker = FlexSendMessage(
                alt_text='文章已生成',
                contents={
                    "type": "bubble",
                    "size": "kilo",
                    "hero": {
                        "type": "image",
                        "url": article.cover,
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "您的問題已經整理成文章了！",
                                "weight": "bold",
                                "size": "md",
                                "wrap": True,
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": article.title, 
                                "weight": "bold",
                                "color": color_map_text[article.category],
                                "size": "md",
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": article.description,  
                                "color": color_map_text[article.category],
                                "wrap": True,
                                "weight": "regular",
                                "size": "sm",
                                "margin": "md",
                            }
                        ],
                        "paddingAll": "md",
                        "backgroundColor": color_map[article.category] + 'DD'
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "style": "link",
                                "height": "sm",
                                "action": {
                                    "type": "uri",
                                    "label": "👆查看文章",
                                    "uri": f"https://liff.line.me/{liff_id}/{article.id}"
                                },
                                "color": color_map_text[article.category]
                            }
                        ],
                        "backgroundColor": color_map[article.category]
                    }
                }
            )

            flex_message_responder = FlexSendMessage(
                alt_text='文章已生成',
                contents={
                    "type": "bubble",
                    "size": "kilo",
                    "hero": {
                        "type": "image",
                        "url": article.cover,
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "您回答的問題已經整理成文章了！",
                                "weight": "bold",
                                "size": "md",
                                "wrap": True,
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": article.title, 
                                "weight": "bold",
                                "color": color_map_text[article.category],
                                "size": "md",
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": article.description,  
                                "color": color_map_text[article.category],
                                "wrap": True,
                                "weight": "regular",
                                "size": "sm",
                                "margin": "md",
                            }
                        ],
                        "paddingAll": "md",
                        "backgroundColor": color_map[article.category] + 'DD'
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "style": "link",
                                "height": "sm",
                                "action": {
                                    "type": "uri",
                                    "label": "👆查看文章",
                                    "uri": f"https://liff.line.me/{liff_id}/{article.id}"
                                },
                                "color": color_map_text[article.category]
                            }
                        ],
                        "backgroundColor": color_map[article.category]
                    }
                }
            )
            
            # 使用 push message 發送文章連結
            line_bot_api.push_message(
                asker.line_id,
                flex_message_asker
            )

            responders = Answer.objects.filter(question=question).values_list('responder__line_id', flat=True).distinct()
            # 發送給所有回答者
            for responder_line_id in responders:
                if responder_line_id != asker.line_id:  # 避免重複發送給提問者
                    line_bot_api.push_message(
                        responder_line_id,
                        flex_message_responder
                    )
            question.delete()
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

def response_article(event):
    bubble = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "請選擇你的輸入方式(請點擊)",
                    "wrap": True,
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": "#25231f"
                }
            ],
            "paddingAll": "xl",  # 增加內邊距
            "backgroundColor": "#DBD4C6",
            "height": "50px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "md",
                    "margin": "md",
                    "action": {
                        "type": "postback",
                        "label": "✏️ 打字輸入  ",
                        "data": "action=answer",
                        "inputOption": "openKeyboard",
                        "fillInText": "發表文章：",
                        
                    },
                    "color": "#808C83",
                },
                {
                    "type": "button",
                    "style": "primary", 
                    "height": "md",
                    "margin": "md",
                    "action": {
                        "type": "postback",
                        "label": "🎤 語音輸入  ",
                        "data": "action=audio",
                        "inputOption": "openVoice",
                        
                    },
                    "color": "#7D6252",
                }
            ],
            "paddingAll": "md",
            "backgroundColor": "#DBD4C6"
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
    # 先回覆「產生圖文中」
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="產生圖文中，請稍候...✍🏻")
    )
    # 生成文章的程序
    openai = OpenAIHandler()
    articles = openai.generate_article(context)
    title_match = re.search(r"# (.+)", articles)
    description_match = re.search(r"## Description\n(.+)", articles)
    category_match = re.search(r"### Category\n(.+)", articles)
    tags_match = re.search(r"### Tags\n\[(.+)\]", articles)

    if tags_match:
        tags_string = tags_match.group(1)  # 获取标签的原始字符串，如 '"tag1", "tag2"'
        # 移除多余的引号和空格
        tags = [tag.strip().strip('"') for tag in tags_string.split(",")]
    else:
        tags = []

    if category_match:
        category = category_match.group(1)
    else:
        category = "其他"

    title = title_match.group(1) if title_match else None
    description = description_match.group(1) if description_match else None

    # 创建文章并存入数据库
    articles = re.sub(r"### Tags\n\[(.+)\]", "", articles)
    articles = re.sub(r"### Category\n(.+)", "", articles)
    articles = re.sub(r"# (.+)", "", articles, 1)
    articles = re.sub(r"## Description\n(.+)", "", articles)
    article = create_article(get_user(event), title, description, articles, category, tags, input_text=context)
    
    # 創建 Flex Message
    flex_message = FlexSendMessage(
        alt_text='文章已生成',
        contents={
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": article.cover,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "你的故事已經轉換成文章了！",
                            
                        "weight": "bold",
                        "size": "md",
                        "wrap": True,
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": article.title, 
                        "weight": "bold",
                        "color": color_map_text[article.category],
                        "size": "md",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": article.description,  
                        "color": color_map_text[article.category],
                        "wrap": True,
                        "weight": "regular",
                        "size": "sm",
                        "margin": "md",
                    }
                ],
                "paddingAll": "md",
                "backgroundColor": color_map[article.category] + 'DD'
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "👆查看文章",
                            "uri": f"https://liff.line.me/{liff_id}/{article.id}"
                        },
                        "color": color_map_text[article.category]
                    }
                ],
                "backgroundColor": color_map[article.category]
            }
        }
    )
    
    # 使用 push message 發送文章連結
    line_bot_api.push_message(
        event.source.user_id,
        flex_message
    )


    
def generate_QA(event, question):
    openai = OpenAIHandler()
    answers = Answer.objects.filter(question=question)
    answers_text =  "\n".join([f"{i+1}. {answer.content}" for i, answer in enumerate(answers)])
    articles = openai.generate_QA(question.content, question.category,answers_text)
    description_match = re.search(r"## Description\n(.+)", articles)
    description = description_match.group(1) if description_match else None
    tags_match = re.search(r"### Tags\n\[(.+)\]", articles)

    if tags_match:
        tags_string = tags_match.group(1)  # 获取标签的原始字符串，如 '"tag1", "tag2"'
        # 移除多余的引号和空格
        tags = [tag.strip().strip('"') for tag in tags_string.split(",")]
    else:
        tags = []

    description = description_match.group(1) if description_match else None

    # 创建文章并存入数据库
    articles = re.sub(r"### Tags\n\[(.+)\]", "", articles)
    articles = re.sub(r"# (.+)", "", articles, 1)
    articles = re.sub(r"## Description\n(.+)", "", articles)
    article = create_article(question.asker, question.content, description, articles, question.category, tags, input_text=question.content + answers_text)
    return article

def create_article(user, title, description, content, category, tags, input_text):
    article = Article.objects.create(
        title=title, 
        author=user,
        description=description,
        content=content, 
        category = category, 
        tags = tags, 
        input_text = input_text
    )
    generate_images_from_text(article.id, content)
    article.cover = Image.objects.filter(article=article).order_by('number').first().image_url
    article.save()
    return article
    
def select_article(user):
    line_id = user.line_id
    # Get the rich menu ID by name
    rich_menu_questiontopic_id = get_rich_menu_id_by_name(line_bot_api2, "richmenu-article")
    if rich_menu_questiontopic_id:
        # Link the main rich menu to the user after signup
        line_bot_api2.link_rich_menu_id_to_user(line_id, rich_menu_questiontopic_id)
    else:
        print("Rich menu with the specified name not found.")

def list_all_article_by_topic(topic):
    # 查詢所有文章，按 `likes` 降序排序
    articles = Article.objects.filter(category=topic).order_by('-likes')

    # 將 QuerySet 轉換為 JSON 格式的列表
    articles_list = [
        {
            "title": article.title,
            "description": article.description,
            "author": article.author.display_name,
            "url": f'article/{article.id}',
            "cover": article.cover,
            "id": article.id ,
            "tags": article.tags
        }
        for article in articles
    ]

    return articles_list

def get_article_by_id(article_id):
    article = Article.objects.get(id=article_id)
    images = Image.objects.filter(article=article).order_by('number')
    images_list = [image.image_url for image in images]

    content = article.content
    
    # 改進的正則表達式模式
    sections = content.split('### ')
    article_sections = {'introduction': '', 'development': '', 'conclusion': ''}
    
    for section in sections:
        if not section.strip():  # 跳過空部分
            continue
        
        if section.startswith('引言'):
            article_sections['introduction'] = section.replace('引言', '').strip()
        elif section.startswith('發展'):
            article_sections['development'] = section.replace('發展', '').strip()
        elif section.startswith('結局'):
            article_sections['conclusion'] = section.replace('結局', '').strip()

    article_json = {
        "id": article.id,
        "title": article.title,
        "time": article.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "author": article.author.display_name,
        "author_pic": article.author.pic_url,
        "introduction": article_sections['introduction'],
        "development": article_sections['development'],
        "conclusion": article_sections['conclusion'],
        "tags": article.tags,
        "images": images_list,
        "likes": article.likes,
        "liked_by": article.liked_by
    }
    return preprocess_article(article_json)

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
    state = ""
    for article in articles:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "hero": {  # 加入封面圖片區域
                "type": "image",
                "url": article.cover,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": article.title, 
                        "weight": "bold",
                        "color": color_map_text[article.category],
                        "size": "md",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": article.description,  
                        "color": color_map_text[article.category],
                        "wrap": True,
                        "weight": "regular",
                        "size": "sm",
                        "margin": "md",
                    }
                ],
                "paddingAll": "md",
                "backgroundColor": color_map[article.category] + 'DD'  # 使用主題顏色作為背景
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "color": color_map_text[article.category],
                        "action": {
                            "type": "uri",  
                            "label": "👆查看文章",  
                            "uri": f"https://liff.line.me/{liff_id}/{article.id}"  
                        }
                    }
                ],
                "backgroundColor": color_map[article.category] # 使用主題顏色作為背景
            }
        }
        bubbles.append(bubble)
    return bubbles

def preprocess_article(article):
    def process_section(content, image_url=None):
        processed_content = []
        if content:
            # 處理數字列表
            content = re.sub(r'(\d+)\. \*\*(.*?)\*\*', r'<strong>\1. \2</strong>', content)
            # 處理其他 markdown 格式
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    processed_content.append(f'<p>{line}</p>')
        
        if image_url:
            processed_content.append(
                f'<div class="article-image">'
                f'<img src="{image_url}" alt="Section image">'
                f'</div>'
            )
        
        return '\n'.join(processed_content)

    # 處理每個段落並添加對應的圖片
    images = article.get('images', [])
    article['introduction'] = process_section(article['introduction'], 
                                           images[0] if len(images) > 0 else None)
    article['development'] = process_section(article['development'], 
                                          images[1] if len(images) > 1 else None)
    article['conclusion'] = process_section(article['conclusion'], 
                                         images[2] if len(images) > 2 else None)

    return article
