import logging

from ..models import ChatUser
from asgiref.sync import sync_to_async

logger = logging.getLogger('socket')


@sync_to_async
def clear_receiver_id_for_user(user_id):
    print('clear_receiver_id_for_user, user: {}'.format(user_id))
    if not user_id:
        return
    chat_user = ChatUser.objects.get(id=user_id)
    chat_user.receiver_id = None
    chat_user.save()


@sync_to_async
def validate_user_pair(sender_id):
    try:
        pair_exist = ChatUser.objects.filter(
            id=sender_id,
            receiver__receiver_id=sender_id
        )

        print('pair_exist: {}'.format(pair_exist))
        if pair_exist:
            return True
        return False
        # sender = ChatUser.objects.get(id=sender_id)
        # receiver_id = sender.receiver_id
        # if not receiver_id:
        #     return False
        #
        # receiver = ChatUser.objects.get(id=receiver_id)
        # if all([
        #     sender,
        #     receiver,
        #     sender.receiver_id == receiver.id,
        #     receiver.receiver_id == sender.id,
        # ]):
        #     return True
        # return False
    except Exception as exc:
        logger.error('validate_user_pair: {}'.format(exc))
        return False
