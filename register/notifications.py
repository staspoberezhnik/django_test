import base64
import random
import datetime
import phonenumbers
import requests
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from phonenumbers import NumberParseException
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from decouple import config
from django_project.settings import GOOGLE_API_KEY

UNICODE_ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789')
CLIENT_SECRET_GENERATOR_LENGTH = 128
CLIENT_ID_GENERATOR_LENGTH = 40
ACCESS_TOKEN_EXPIRATION = 60 * 60

client = Client(config('twilio_sid'), config('twilio_token'))


def send_register_sms(username, receiver=None):
    if receiver is None:
        return None
    else:
        try:
            message = username + ' you are successfully register'
            client.messages.create(
                to=receiver,
                from_=config('twilio_sender'),
                body=message,
            )
        except TwilioRestException:
            return None


def city_autocomplete(value):
    url = 'https://maps.googleapis.com/maps/api/place/autocomplete' \
          '/json?input={city}&types=(cities)&language=us&key={key}'.format(city=value, key=GOOGLE_API_KEY)
    request = requests.get(url).json()
    cities = [city for city in request['predictions']]
    results = []
    for city in cities:
        results.append({'id': city["description"], 'text': city["description"]})
    return results


def search_near_users(city, destination):
    url = 'https://maps.googleapis.com/maps/api/distancematrix/' \
          'json?origins={city}&destinations={destination}&key={key}'.format(city=city,
                                                                            destination=destination,
                                                                            key=GOOGLE_API_KEY)
    request = requests.get(url).json()
    if request['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
        return None
    return request['rows'][0]['elements'][0]['distance']['value']


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


def generate_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for _ in range(length))


def generate_client_id():
    return generate_token(length=CLIENT_ID_GENERATOR_LENGTH)


def generate_client_secret():
    return generate_token(length=CLIENT_SECRET_GENERATOR_LENGTH)


def get_expiration_time():
    return timezone.now() + datetime.timedelta(seconds=ACCESS_TOKEN_EXPIRATION)


class CsrfExemptMixin(object):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CsrfExemptMixin, self).dispatch(request, *args, **kwargs)


class AuthMixin(object):
    app = None

    def dispatch(self, request, *args, **kwargs):
        from .models import MyApplication
        try:
            auth = request.META.get('HTTP_AUTHORIZATION').replace('Basic ', '')
            client_id, client_secret = base64.b64decode(auth).decode().split(':')
        except (AttributeError, UnicodeDecodeError, Exception) as e:
            return HttpResponseForbidden()
        try:
            self.app = MyApplication.objects.get(client_id=client_id, client_secret=client_secret)
        except MyApplication.DoesNotExist:
            return HttpResponseForbidden()
        return super(AuthMixin, self).dispatch(request, *args, **kwargs)
