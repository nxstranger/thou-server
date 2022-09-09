from django.urls import path
from .views import post

urlpatterns = [
    path('login/', post),
]
