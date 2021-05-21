from django.http import HttpResponse
from django.conf import settings

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)


line_bot_api = LineBotApi(settings.LINE_TOKEN)
handler = WebhookHandler(settings.LINE_SECRET)


def line_endpoint(request):
    print('hello')
    return HttpResponse("Hello LINE Bot", 200)
