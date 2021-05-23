from django.conf import settings
from linebot import LineBotApi
from linebot .models.send_messages import TextSendMessage

line_bot_api = LineBotApi(settings.LINE_TOKEN)


def reply_text(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )


def push_message(room, msg):
    line_bot_api.push_message(
        room.room_id,
        TextSendMessage(text=msg)
    )


def get_user_name(user_id):
    try:
        res = line_bot_api.get_profile(user_id)
        return res.display_name
    except Exception:
        return 'NoNameUser'


def get_group_name(group_id):
    try:
        res = line_bot_api.get_group_summary(group_id)
        return res.group_name
    except Exception:
        return 'NoNameGroup'
