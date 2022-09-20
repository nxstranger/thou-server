import logging
from urllib.parse import parse_qs
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.backends import TokenBackend
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.conf import settings
from chat.models import ChatUser
from asgiref.sync import sync_to_async
logger = logging.getLogger('socket')


class TokenAuthMiddleware:
    """
    SOCKET AUTH MIDDLEWARE
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope['query_string']
        if query_string:
            try:
                parsed_query = parse_qs(query_string)
                token_key = parsed_query[b'user'][0].decode()
                user_id = self.validate_token(token_key)
                user = await self.get_user(user_id)
                scope['user'] = user
                receiver = await self.get_user(user.receiver_id)
                scope['receiver'] = receiver
            except AuthenticationFailed:
                logger.error('TokenAuthMiddleware/AuthenticationFailed: {}')
                scope['user'] = AnonymousUser()
            except Exception as exc:
                logger.error('TokenAuthMiddleware: {}'.format(exc))
        try:
            return await self.app(scope, receive, send)
        except Exception as exc:
            logger.error('ERR await self.app: {}'.format(exc))

    @staticmethod
    def validate_token(token):
        try:
            jwt_signing_key = settings.JWT_KEY
            valid_data = TokenBackend(algorithm='HS256', signing_key=jwt_signing_key).decode(token, verify=True)
            user = valid_data['user_id']
            return user
        except ValidationError as v_exc:
            logger.error("TokenAuthMiddleware/validate_token {}".format(v_exc))
            return None

    @sync_to_async
    def get_user(self, user_id):
        try:
            return ChatUser.objects.get(id=user_id)
        except Exception as exc:
            logger.error('TokenAuthMiddleware/get_user: {}'.format(exc))
            return AnonymousUser()


def ws_token_auth_mw(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
