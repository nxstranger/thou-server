import json
import logging

from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from urllib.parse import parse_qs
from datetime import datetime

CACHE_KEY_FORMAT = 'user_channels_key_{}'
CHANNEL_KEY_EXPIRED = 60 * 60 * 24

channel_layer = get_channel_layer()
logger = logging.getLogger('socket')


class ChatConsumer(AsyncWebsocketConsumer):
    groups = ["broadcast"]

    MESSAGES_SCHEMA = {
        'MSG': ['message', 'type', 'stamp', 'contact']
    }

    async def websocket_connect(self, message):
        print('self.scope: {}'.format(self.scope))
        print('self.scope.user: {}'.format(self.scope.get('user')))
        try:
            await self.accept()
            user = self.scope.get('user')
            if any([
                not user,
                isinstance(user, AnonymousUser)
            ]):
                await self.close(code=3008)
            else:
                await self.send_contact_not_connected()
        except Exception as exc:
            print("ChatConsumer connect {}".format(exc))
            logger.error("ChatConsumer connect {}".format(exc))
            await self.close(code=3500)

    async def websocket_disconnect(self, message):
        print('call disconnect {}'.format(datetime.now()))
        try:
            user = self.scope.get('user')
            if user and user.id:
                print('disconnect: user:{}'.format(self.scope['user']))
                self.delete_channel_id_for_user(user_id=self.scope['user'])
        except Exception as exc:
            logger.error('ChatConsumer/disconnect: {}'.format(exc))
        print('disconnected')

    async def websocket_receive(self, message):
        print('websocket_receive {}'.format(message))
        await self.handle_type_message(message['text'])

    async def send(self, text_data=None, bytes_data=None, close=False):
        print('send: {}'.format(text_data))
        try:
            await super().send(text_data, bytes_data, close)
        except Exception as exc:
            print("send Exception: {}".format(exc))

    @staticmethod
    def set_channel_id_for_user(channel_id, user_id):
        if not all([user_id, channel_id]):
            raise Exception('Unauthorized!')
        cache.set(CACHE_KEY_FORMAT.format(user_id), channel_id, CHANNEL_KEY_EXPIRED)

    @staticmethod
    def get_channel_id_for_user(user_id):
        channel_id = cache.get(CACHE_KEY_FORMAT.format(user_id))
        return channel_id

    @staticmethod
    def delete_channel_id_for_user(user_id):
        cache.delete(CACHE_KEY_FORMAT.format(user_id))

    def validate_message_schema(self, message: dict, message_type):
        if len(self.MESSAGES_SCHEMA.get(message_type)) != len(message.keys()):
            raise KeyError('Invalid schema for message / invalid keys length')
        for name in self.MESSAGES_SCHEMA.get(message_type):
            if name not in message:
                logger.error('Invalid schema for message: {}' % message)
                raise KeyError('Invalid schema for message / key not in message')

    async def handle_type_message(self, message):
        print('-' * 40)
        print('\n')
        try:
            decoded_message = json.loads(message)
            if type(decoded_message) != dict:
                raise Exception('Message is not dict')
            msg_type = decoded_message.get('type')

            if msg_type not in self.MESSAGES_SCHEMA.keys():
                return
            self.validate_message_schema(decoded_message, msg_type)
            print('decoded_message: {}'.format(decoded_message))
            if decoded_message.get('type') == 'MSG':
                contact_id = decoded_message.get('contact')
                # contact_id = self.scope['user_id']
                if not contact_id:
                    raise KeyError('Contact not found')
                contact_socket_id = self.get_channel_id_for_user(contact_id)
                print('contact_socket id:%s channel:%s' % (contact_id, contact_socket_id))
                if contact_socket_id:
                    print('if contact_socket_id')
                    payload = {
                        'type': 'chat.message',
                        'message': decoded_message.get('message'),
                        # 'stamp': round(datetime.now().timestamp() * 1000)
                    }
                    await channel_layer.send(contact_socket_id, payload)
                else:
                    logger.info('Active channel for user is not found')
                    await self.send_contact_not_connected()
        except Exception as exc:
            print('Exception: {}'.format(exc))

    async def send_json(self, data):
        try:
            text_data = json.dumps(data)
            await self.send(text_data=text_data)
        except Exception as exc:
            print('Exception send_json: {}'.format(exc))

    async def chat_message(self, event):
        print('chat_message event: {}'.format(event))
        await self.send_json({
            'type': 'MSG',
            'message': event['message'],
            'stamp': round(datetime.now().timestamp() * 1000)
        })

    async def request_contact_name(self):
        response_message = {
            'code': 1003,
            'message': 'Set up your contact / {}'.format(self.channel_name),
            'stamp': round(datetime.now().timestamp() * 1000)}
        await self.send_json(response_message)

    async def send_contact_not_connected(self):
        response_message = {
            'code': 'INFO',
            'message': 'Your contact is not connected',
            'stamp': round(datetime.now().timestamp() * 1000)}
        await self.send_json(response_message)
