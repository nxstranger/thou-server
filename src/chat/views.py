import json

from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, response
from rest_framework.decorators import action
from .models import ChatUser
from .serializers import ChatUserSetContactSerializer


class ChatUserViewSet(viewsets.ViewSet):
    queryset = ChatUser.objects.all().filter(is_active=True)
    permission_classes = (permissions.IsAuthenticated,)

    @action(
        detail=False,
        methods=['PUT'],
        permission_classes=(permissions.IsAuthenticated, ),
    )
    def update_contact(self, request):
        print('update_contact request {}'.format(request))
        # print('update_contact request {}'.format(request.user))
        # print('update_contact request {}'.format(request.user.id))
        print('update_contact request {}'.format(request.data))
        user = request.user
        serializer = ChatUserSetContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = self.queryset.get(username=serializer.data.get('contact_name'))
            print('contact'.format(contact))
            if contact:
                user.receiver = contact
                user.save()
                return response.Response(status=200)
        else:
            print('s not valid')
        # user = get_object_or_404(queryset, pk=pk)
        # serializer = UserSerializer(user)
        return response.Response(status=400)




# @csrf_exempt
# def put_user_data(request):
#     print('called')
#     # print(request.scope)
#     print(request.body)
#     data = request.body.decode('utf-8')
#     payload = json.loads(data)
#     try:
#         contact = payload.get('contactName')
#         print('contact: {}'.format(contact))
#         password = payload.get('password')
#         # if username == 'admin' and password == 'qwe1qwe1qwe':
#         #     response_data = json.dumps({'access': 'qweqweqeqwewqew'})
#         return HttpResponse(status=200)
#     except Exception as exp:
#         print('Invalid data: {}'.format(exp))
#     return HttpResponse(status=401)
