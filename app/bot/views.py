from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from bot.line import handler


@csrf_exempt
def line_endpoint(request):
    if request.method == 'POST':
        signatrue = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        print(body)
        handler.handle(body, signatrue)

    return HttpResponse()
