import json
import logging

from django.core.cache import cache
from chat.models import ChatUser
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from datetime import datetime
from .utils import clear_receiver_id_for_user, validate_user_pair

CACHE_KEY_FORMAT = 'user_channels_key_{}'
CHANNEL_KEY_EXPIRED = 60 * 60 * 24

channel_layer = get_channel_layer()
logger = logging.getLogger('socket')


class ChatConsumer(AsyncWebsocketConsumer):
    groups = ["broadcast"]

    MESSAGES_SCHEMA = {
        'MSG': ['message', 'type', 'stamp']
    }

    async def websocket_connect(self, message):
        logger.info('\n\nself.scope.user: {}'.format(self.scope.get('user')))
        logger.info('channel: {}'.format(self.channel_name))
        try:
            user = self.scope.get('user')
            receiver = self.scope.get('receiver')
            await self.accept()
            if await self.connected_user_invalid():
                logger.info('connected_user_invalid')
                return await self.close(code=3008)

            await self.websocket_check_old_connection(user)

            contact_socket_id = self.get_channel_id_for_user(receiver.id)
            if contact_socket_id:
                if user.id == receiver.id:
                    return await self.send_connection_is_set(message=self.channel_name)
                contact_connection_payload = {
                    "type": "send.connection_is_set",
                    "message": self.channel_name
                }
                await channel_layer.send(contact_socket_id, contact_connection_payload)
                return await self.send_connection_is_set()

            return await self.send_contact_not_connected()
        except Exception as exc:
            logger.info("ChatConsumer connect {}".format(exc))
            logger.error("ChatConsumer connect {}".format(exc))
            await self.close(code=3500)

    async def websocket_check_old_connection(self, user):
        """
        check exist connection and close if exits
        """
        logger.info('check_old_connection user {}'.format(user.id))
        exist_channel_id = self.get_channel_id_for_user(user_id=user.id)
        if exist_channel_id:
            logger.info('exist connection {}'.format(exist_channel_id))
            payload = {
                "type": "websocket.close_connection",
                "code": 3009
            }
            await channel_layer.send(exist_channel_id, payload)
        self.set_channel_id_for_user(self.channel_name, user.id)

    async def websocket_close_connection(self, payload):
        logger.info('call disconnect for chanel: {}'.format(self.channel_name))
        logger.info('disconnect payload: {}'.format(payload))
        try:
            user = self.scope.get('user')
            if user and user.id:
                logger.info('disconnect: user:{}'.format(self.scope['user']))
                self.delete_channel_id_for_user(user_id=user.id)
                contact_socket_id = self.get_channel_id_for_user(user.receiver_id)
                if contact_socket_id:
                    contact_connection_payload = {
                        "type": "send.contact_not_connected",
                    }
                    await channel_layer.send(contact_socket_id, contact_connection_payload)
                # await clear_receiver_id_for_user(user.id)
        except Exception as exc:
            logger.error('ChatConsumer/disconnect: {}'.format(exc))

    async def websocket_disconnect(self, payload):
        code = payload.get('code')
        if code:
            await self.close(code=code)
        await self.close()

    async def websocket_receive(self, message):
        """
        ENTRYPOINT FOR ALL MESSAGES
        """
        logger.info('-' * 40)
        logger.info('\n')
        logger.info('websocket_receive {}'.format(message))
        user = self.scope.get('user')

        if await self.connected_user_invalid():
            return await self.close(code=3008)
        if not await validate_user_pair(user.id):
            return await self.send_contact_not_connected()
        await self.handle_type_message(message['text'])

    async def send(self, text_data=None, bytes_data=None, close=False):
        logger.info('send: {}'.format(text_data))
        try:
            await super().send(text_data, bytes_data, close)
        except Exception as exc:
            logger.info("send Exception: {}".format(exc))

    async def connected_user_invalid(self):
        user = self.scope.get('user')
        receiver = self.scope.get('receiver')
        logger.info("connected_user_invalid u:{} c:{}".format(user, user.receiver_id))
        if all([
            user,
            receiver,
            isinstance(user, ChatUser),
            isinstance(receiver, ChatUser),
        ]):
            logger.info('result false')
            return False
        logger.error("Got connection from invalid user")
        logger.info('result true')
        return True

    @staticmethod
    def set_channel_id_for_user(channel_id, user_id):
        if not all([user_id, channel_id]):
            raise Exception('Unauthorized!')
        logger.info('CACHE / set_channel_id_for_user {}'.format(user_id))
        cache.set(CACHE_KEY_FORMAT.format(user_id), channel_id, CHANNEL_KEY_EXPIRED)

    @staticmethod
    def get_channel_id_for_user(user_id):
        logger.info('CACHE / get_channel_id_for_user {}'.format(user_id))

        channel_id = cache.get(CACHE_KEY_FORMAT.format(user_id))
        return channel_id

    @staticmethod
    def delete_channel_id_for_user(user_id):
        logger.info('CACHE delete_channel_id_for_user {}'.format(user_id))
        cache.delete(CACHE_KEY_FORMAT.format(user_id))

    def validate_message_schema(self, message: dict, message_type):
        if len(self.MESSAGES_SCHEMA.get(message_type)) != len(message.keys()):
            raise KeyError('Invalid schema for message / invalid keys length')
        for name in self.MESSAGES_SCHEMA.get(message_type):
            if name not in message:
                logger.error('Invalid schema for message: {}' % message)
                raise KeyError('Invalid schema for message / key not in message')

    async def handle_type_message(self, message):
        try:
            decoded_message = json.loads(message)
            if type(decoded_message) != dict:
                raise Exception('Message is not dict')
            message_type = decoded_message.get('type')

            if message_type not in self.MESSAGES_SCHEMA.keys():
                # todo: send message invalid
                return
            self.validate_message_schema(decoded_message, message_type)
            logger.info('decoded_message: {}'.format(decoded_message))
            if message_type == 'MSG':
                user = self.scope.get('user')
                contact_id = user.receiver_id
                if not contact_id:
                    raise KeyError('Contact not found')
                contact_socket_id = self.get_channel_id_for_user(contact_id)
                logger.info('contact_socket id:%s channel:%s' % (contact_id, contact_socket_id))
                if contact_socket_id:
                    logger.info('if contact_socket_id')
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
            logger.info('Exception: {}'.format(exc))

    async def send_json(self, data):
        try:
            text_data = json.dumps(data)
            await self.send(text_data=text_data)
        except Exception as exc:
            logger.info('Exception send_json: {}'.format(exc))

    async def chat_message(self, event):
        logger.info('chat_message event: {}'.format(event))
        await self.send_json({
            'type': 'MSG',
            'message': event['message'],
            'stamp': round(datetime.now().timestamp() * 1000)
        })

    # async def request_contact_name(self):
    #     response_message = {
    #         'code': 1003,
    #         'message': 'Set up your contact / {}'.format(self.channel_name),
    #         'stamp': round(datetime.now().timestamp() * 1000)}
    #     await self.send_json(response_message)

    async def send_contact_not_connected(self, message=None):
        response_message = {
            'code': 3003,
            'type': 'ERR',
            'message': 'Your contact is not connected or not paired',
            'stamp': round(datetime.now().timestamp() * 1000)}
        await self.send_json(response_message)

    async def send_connection_is_set(self, message=None):
        logger.info('send_connection_is_set: {}'.format(message))
        msg = 'Connection is set'
        if message:
            msg = f'Connection is set / channel: {message}'
        response_message = {
            'code': 3004,
            'type': 'INFO',
            'message': msg,
            'stamp': round(datetime.now().timestamp() * 1000)}
        await self.send_json(response_message)
