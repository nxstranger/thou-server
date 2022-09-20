from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatUserViewSetMixin

router = DefaultRouter()
router.register(r'', ChatUserViewSetMixin)

urlpatterns = [
    path('', include(router.urls))
]
