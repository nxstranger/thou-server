import json

from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def post(request):
    print('called')
    payload = json.dumps({'access': 'qweqw'})
    return HttpResponse(status=200, content=payload)
