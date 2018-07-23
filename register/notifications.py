from twilio.rest import Client
from decouple import config

client = Client(config('account_sid'), config('auth_token'))


def send_register_sms(username, receiver=None):
    if receiver is None:
        return None
    else:
        message = username + ' you are successfully register'
        client.messages.create(
            to=receiver,
            from_=config('sms_sender'),
            body=message,
        )
