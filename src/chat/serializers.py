from rest_framework import serializers
from .models import ChatUser


class ChatUserSetContactSerializer(serializers.Serializer):
    contact_name = serializers.CharField(max_length=100, required=True)


class ChatUserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatUser
        fields = ['id', 'username', 'first_name', 'is_active']
