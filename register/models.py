from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .notifications import validate_phone_number


#
# def upload_location(avatars, filename):
#     return '{}/{}'.format(avatars, filename)


class User(AbstractUser):
    email = models.EmailField(_('email address'), blank=False, unique=True)
    city = models.CharField(max_length=50, blank=True)
    friends = models.ManyToManyField('User')
    phone_number = models.CharField(
        max_length=20,
        blank=False,
        validators=[validate_phone_number],
        unique=True,
        help_text='Input full number with country code'
    )
    photo = models.ImageField(upload_to='avatars', blank=True, null=True)

    def __str__(self):
        return self.username


class FriendshipStatus(models.Model):

    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    status = models.BooleanField()

    def get_friendship_request(self, receiver):
        try:
            status = FriendshipStatus.objects.get(
                Q(sender=self.sender, receiver=receiver) | Q(sender=receiver, receiver=self.sender)
            )
        except FriendshipStatus.DoesNotExist:
            status = None
        return status
