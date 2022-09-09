from urllib.parse import urlparse, parse_qs
# from channels.auth import AuthMiddlewareStack

# from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.backends import TokenBackend

from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from django.core.exceptions import ValidationError
from django.conf import settings


# class TokenAuthMiddleware:
#     def __init__(self, inner):
#         self.inner = inner
#
#     def __call__(self, scope):
#         query_string = scope['query_string']
#         if query_string:
#             try:
#                 parsed_query = parse_qs(query_string)
#                 token_key = parsed_query[b'user'][0].decode()
#                 token_name = 'token'
#                 if token_name == 'token':
#                     user, _ = ('admin', 'lolo') # Ваша функция аутентификации
#                     scope['user'] = user
#                     close_old_connections()
#             except AuthenticationFailed:
#                 scope['user'] = AnonymousUser()
#         else:
#             scope['user'] = AnonymousUser()
#         return self.inner(scope)
#
#
# def ws_token_auth_mw(inner):
#     return TokenAuthMiddleware(AuthMiddlewareStack(inner))

def validate_token(token):
    try:
        jwt_signing_key = settings.JWT_KEY
        valid_data = TokenBackend(algorithm='HS256', signing_key=jwt_signing_key).decode(token, verify=True)
        user = valid_data['user_id']
        # user = 'user'
        # request.user = user
        # print('valid_data', valid_data)
        print('validate_token', user)
        return user
    except ValidationError as v:
        print("validation error", v)


def handle_token(scope):
    query_string = scope['query_string']
    if query_string:
        try:
            parsed_query = parse_qs(query_string)
            token_key = parsed_query[b'user'][0].decode()
            token_name = 'token'
            print('token_key')
            print(token_key)
            if token_key:
                user = validate_token(token_key)

                scope['user'] = user
                close_old_connections()
        except AuthenticationFailed:
            scope['user'] = AnonymousUser()
    else:
        scope['user'] = AnonymousUser()
    # return self.inner(scope)
