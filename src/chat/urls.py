from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatUserViewSet

router = DefaultRouter()
router.register(r'', ChatUserViewSet)

urlpatterns = [
    path('', include(router.urls))
]
