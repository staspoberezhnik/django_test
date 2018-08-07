import base64

import requests
from decouple import config

client_id = config('client_id')
client_secret = config('client_secret')

auth_key = '%s:%s' % (client_id, client_secret)

response = requests.post(
    url='http://127.0.0.1:8000/token/',
    data=dict(grant_type='client_credentials'),
    headers={
        'Authorization': 'Basic %s' % base64.b64encode(auth_key.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded',
    }
)
access_token = response.json()['access_token']
protected_data = requests.get(
    url='http://127.0.0.1:8000/protected_data/',
    headers={
        'Authorization': 'Bearer %s' % access_token
    }
)
print(protected_data)
print(response.json())
