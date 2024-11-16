from decouple import config

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    RichMenuRequest,
    RichMenuArea,
    RichMenuSize,
    RichMenuBounds,
    URIAction,
    MessageAction,
    PostbackAction,
    RichMenuSwitchAction,
    CreateRichMenuAliasRequest,
    UpdateRichMenuAliasRequest
)

channel_access_token = config('LINE_ACCESS_TOKEN')

configuration = Configuration(
    access_token=channel_access_token
)


def rich_menu_object_signup_json():
    return {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": False,
        "name": "richmenu-signup",
        "chatBarText": "📌選擇您的世代",
        "areas": [
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 1250,
                    "height": 1686
                },
                "action": {
                    "type": "postback",
                    "data": "action=choose_generation&generation=青世代",
                    "displayText": "青世代"
                }
            },
            {
                "bounds": {
                    "x": 1251,
                    "y": 0,
                    "width": 1250,
                    "height": 1686
                },
                "action": {
                    "type": "postback",
                    "data": "action=choose_generation&generation=銀世代",
                    "displayText": "銀世代"
                }
            }
        ]
    }

def rich_menu_object_main_json():
    return {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": False,
        "name": "richmenu-main",
        "chatBarText": "📌選單開關點我",
        "areas": [
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 833,
                    "height": 1686
                },
                "action": {
                    "type": "postback",
                    "data": "action=show_menu"
                }
            },
            {
                "bounds": {
                    "x": 834,
                    "y": 0,
                    "width": 833,
                    "height": 843
                },
                "action": {
                    "type": "postback",
                    "data": "action=ask_question"
                }
            },
            {
                "bounds": {
                    "x": 834,
                    "y": 844,
                    "width": 833,
                    "height": 843
                },
                "action": {
                    "type": "postback",
                    "data": "action=send_image"
                }
            },
            {
                "bounds": {
                    "x": 1667,
                    "y": 0,
                    "width": 833,
                    "height": 843
                },
                "action": {
                    "type": "postback",
                    "data": "action=answer_question"
                }
            },
            {
                "bounds": {
                    "x": 1667,
                    "y": 844,
                    "width": 833,
                    "height": 843
                },
                "action": {
                    "type": "postback",
                    "data": "action=show_articles"
                }
            }
        ]
    }

def rich_menu_object_questiontopic_json():
    return {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": False,
        "name": "richmenu-questiontopic",
        "chatBarText": "📌選擇感興趣的主題",
        "areas": [
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 2500,
                    "height": 200
                },
                "action": {
                    "type": "richmenuswitch",
                    "richMenuAliasId": "richmenu-alias-main",
                    "data": "richmenu-changed-to-main"
                }
            },
            {
                "bounds": {
                    "x": 0,
                    "y": 200,
                    "width": 833,
                    "height": 743
                },
                "action": {
                    "type": "postback",
                    "data": "action=ask_question_topic",
                    "inputOption": "openKeyboard",
                    "fillInText": "主題:傳統技藝 \n"
                }
            },
            {
                "bounds": {
                    "x": 0,
                    "y": 944,
                    "width": 833,
                    "height": 743
                },
                "action": {
                    "type": "postback",
                    "data": "action=ask_question_topic",
                    "inputOption": "openKeyboard",
                    "fillInText": "主題:人生經驗 \n"
                }
            },
            {
                "bounds": {
                    "x": 834,
                    "y": 200,
                    "width": 833,
                    "height": 743
                },
                "action": {
                    "type": "postback",
                    "data": "action=ask_question_topic",
                    "inputOption": "openKeyboard",
                    "fillInText": "主題:歷史方面 \n"
                }
            },
            {
                "bounds": {
                    "x": 834,
                    "y": 944,
                    "width": 833,
                    "height": 743
                },
                "action": {
                    "type": "postback",
                    "data": "action=ask_question_topic",
                    "inputOption": "openKeyboard",
                    "fillInText": "主題:健康養生 \n"
                }
            },
            {
                "bounds": {
                    "x": 1667,
                    "y": 200,
                    "width": 833,
                    "height": 743
                },
                "action": {
                    "type": "postback",
                    "data": "action=ask_question_topic",
                    "inputOption": "openKeyboard",
                    "fillInText": "主題:佳餚食譜 \n"
                }
            },
            {
                "bounds": {
                    "x": 1667,
                    "y": 944,
                    "width": 833,
                    "height": 743
                },
                "action": {
                    "type": "postback",
                    "data": "action=ask_question_topic",
                    "inputOption": "openKeyboard",
                    "fillInText": "主題:其他 \n"
                }
            }
        ]
    }


def create_action(action):
    if action['type'] == 'postback':
        if action.get('displayText'):
            return PostbackAction(data=action.get('data'), displayText=action.get('displayText'))
        elif action.get('inputOption'):
            return PostbackAction(data=action.get('data'), inputOption=action.get('inputOption'), fillInText=action.get('fillInText'))
        else:
            return PostbackAction(data=action.get('data'))
    else:
        return RichMenuSwitchAction(
            rich_menu_alias_id=action.get('richMenuAliasId'),
            data=action.get('data')
        )

def delete_all_rich_menus(line_bot_api):
    try:
        # Fetch the list of all rich menus
        response = line_bot_api.get_rich_menu_list()
        rich_menus = response.richmenus
        
        # Iterate over each rich menu and delete it
        for rich_menu in rich_menus:
            line_bot_api.delete_rich_menu(rich_menu_id=rich_menu.rich_menu_id)
            print(f"Deleted rich menu with ID: {rich_menu.rich_menu_id}")
    except Exception as e:
        print(f"Failed to delete rich menus. Error: {e}")

def main():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)

        # Delete all existing rich menus
        delete_all_rich_menus(line_bot_api)

        # Create rich menu for signup
        rich_menu_object_signup = rich_menu_object_signup_json()

        areas = [
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=info['bounds']['x'],
                    y=info['bounds']['y'],
                    width=info['bounds']['width'],
                    height=info['bounds']['height']
                ),
                action=create_action(info['action'])
            ) for info in rich_menu_object_signup['areas']
        ]

        rich_menu_to_signup_create = RichMenuRequest(
            size=RichMenuSize(width=rich_menu_object_signup['size']['width'],
                              height=rich_menu_object_signup['size']['height']),
            selected=rich_menu_object_signup['selected'],
            name=rich_menu_object_signup['name'],
            chat_bar_text=rich_menu_object_signup['chatBarText'],
            areas=areas
        )

        rich_menu_signup_id = line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_to_signup_create
        ).rich_menu_id

        # Upload image to rich menu signup
        with open('./static/richmenu-signup.png', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_signup_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/png'}
            )

        # Create rich menu for main
        rich_menu_object_main = rich_menu_object_main_json()

        areas = [
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=info['bounds']['x'],
                    y=info['bounds']['y'],
                    width=info['bounds']['width'],
                    height=info['bounds']['height']
                ),
                action=create_action(info['action'])
            ) for info in rich_menu_object_main['areas']
        ]
        
        rich_menu_to_main_create = RichMenuRequest(
            size=RichMenuSize(width=rich_menu_object_main['size']['width'],
                              height=rich_menu_object_main['size']['height']),
            selected=rich_menu_object_main['selected'],
            name=rich_menu_object_main['name'],
            chat_bar_text=rich_menu_object_main['chatBarText'],
            areas=areas
        )

        rich_menu_main_id = line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_to_main_create
        ).rich_menu_id

        # Upload image to rich menu main
        with open('./static/richmenu-main.png', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_main_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/png'}
            )

        # Create rich menu for question topic
        rich_menu_object_questiontopic = rich_menu_object_questiontopic_json()

        areas = [
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=info['bounds']['x'],
                    y=info['bounds']['y'],
                    width=info['bounds']['width'],
                    height=info['bounds']['height']
                ),
                action=create_action(info['action'])
            ) for info in rich_menu_object_questiontopic['areas']
        ]

        rich_menu_to_questiontopic_create = RichMenuRequest(
            size=RichMenuSize(width=rich_menu_object_questiontopic['size']['width'],
                              height=rich_menu_object_questiontopic['size']['height']),
            selected=rich_menu_object_questiontopic['selected'],
            name=rich_menu_object_questiontopic['name'],
            chat_bar_text=rich_menu_object_questiontopic['chatBarText'],
            areas=areas
        )

        rich_menu_questiontopic_id = line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_to_questiontopic_create
        ).rich_menu_id

        # Upload image to rich menu question topic
        with open('./static/richmenu-questiontopic.png', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_questiontopic_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/png'}
            )

        # Set rich menu signup as the default rich menu
        line_bot_api.set_default_rich_menu(rich_menu_id=rich_menu_signup_id)

        # Update alias for rich menu main
        alias_main = UpdateRichMenuAliasRequest(
            rich_menu_alias_id='richmenu-alias-main',
            rich_menu_id=rich_menu_main_id
        )
        line_bot_api.update_rich_menu_alias(
            update_rich_menu_alias_request=alias_main,
            rich_menu_alias_id='richmenu-alias-main'
        )

main()