from rest_framework import serializers


class ChatUserSetContactSerializer(serializers.Serializer):
    contact_name = serializers.CharField(max_length=100, required=True)
