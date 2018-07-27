import phonenumbers
import requests
from django.core.exceptions import ValidationError
from django.db.models import Q
from phonenumbers import NumberParseException
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from decouple import config

from django_project.settings import API_KEY

client = Client(config('account_sid'), config('auth_token'))


def send_register_sms(username, receiver=None):
    if receiver is None:
        return None
    else:
        try:
            message = username + ' you are successfully register'
            client.messages.create(
                to=receiver,
                from_=config('sms_sender'),
                body=message,
            )
        except TwilioRestException:
            return None


def city_autocomplete(value):
    url = 'https://maps.googleapis.com/maps/api/place/autocomplete' \
          '/json?input={city}&types=(cities)&language=us&key={key}'.format(city=value, key=API_KEY)
    request = requests.get(url).json()
    cities = [city for city in request['predictions']]
    results = []
    for city in cities:
        results.append({'id': city["description"], 'text': city["description"]})
    return results


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


def get_friendship_request(sender, receiver):
    from register.models import FriendshipStatus
    try:
        status = FriendshipStatus.objects.get(
            Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
        )
    except FriendshipStatus.DoesNotExist:
        status = None
    return status


def get_friendship_status(status, sender):
    friend_status = None
    if status:
        if status.sender == sender and status.status is False:
            friend_status = 'send'
        else:
            friend_status = 'receive'
    return friend_status
