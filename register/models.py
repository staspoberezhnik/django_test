import phonenumbers
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumbers import NumberParseException
from django.utils.translation import gettext_lazy as _

#
# def upload_location(avatars, filename):
#     return '{}/{}'.format(avatars, filename)


def validate_phone_number(phone_number):
    valid = True
    try:
        phone = phonenumbers.parse(phone_number, None)
    except NumberParseException:
        valid = False
    else:
        if not phonenumbers.is_valid_number(phone):
            valid = False
    if valid is False:
        raise ValidationError('Phone number is not valid', code='invalid')


class User(AbstractUser):
    email = models.EmailField(_('email address'), blank=False, unique=True)
    city = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(
        max_length=20,
        blank=False,
        validators=[validate_phone_number],
        unique=True,
        help_text='Input full number with country code'
    )
    photo = models.ImageField(upload_to='avatars', blank=True, null=True)

    def __str__(self):
        name = self.get_full_name()
        return name if name else self.username
