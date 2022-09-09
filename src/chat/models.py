from django.contrib.auth.models import AbstractUser, models


class ChatUser(AbstractUser):
    is_connected = models.BooleanField(default=False, null=False)

    receiver = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        default=None,
        null=True
    )