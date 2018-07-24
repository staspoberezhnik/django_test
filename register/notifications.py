import requests
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
