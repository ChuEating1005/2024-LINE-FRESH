from linebot import LineBotApi
from linebot.v3.messaging import MessagingApi, ApiClient, Configuration
from linebot.models import TextSendMessage
from django.conf import settings
from ..models import User, AudioMessage, Conversation, Question, Answer, Article, Comment

line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)
configuration = Configuration(access_token=settings.LINE_ACCESS_TOKEN)

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
        line_bot_api2 = MessagingApi(ApiClient(configuration))
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

def create_question(event, user, group):
    try:
        question = Question.objects.create(asker=user, content=event.message.text, category=group)
        return question
    except Exception as e:
        print(e)
        return None
def respond_message(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )