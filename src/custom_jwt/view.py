import os

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __int__(self):
        super().__init__()

    def validate(self, attrs):
        data = super().validate(attrs)
        data['name'] = attrs['username']
        del data['refresh']
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

