"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from graphene_django.views import GraphQLView

from custom_jwt.view import MyTokenObtainPairView


schema_view = get_schema_view(
    openapi.Info(
      title="WS chat API",
      default_version='v1',
      description="Qwe qwe",
      contact=openapi.Contact(email="qwe@qwe.qwe"),
      license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

version_prefix = 'v1'
rest_urls = [
    path('/chat_users/', include('chat.urls')),
]

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),            # noqa
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),                      # noqa
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),                               # noqa

    # rest drf
    re_path(r'^auth/login$', MyTokenObtainPairView.as_view(), name='rest_login'),
    re_path(r'^api/{}'.format(version_prefix), include(rest_urls)),

    # graphql
    re_path(r'^graphql$', GraphQLView.as_view(graphiql=True)),
]
