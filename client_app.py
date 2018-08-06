import base64

import requests

client_id = '4PCZ8MisjtQKwDNQw0SjYGrp032e1xoz029i6NqW'
client_secret = 'rguCFxVUY37VBnSumVfsMJchNNJRNQRfeqoez9fE7R3fpm9ZF3hKPcPYs3o' \
                'EfFYeY1QwP89H5Voe51UnnmjENQWgVcUzrwttY9Zhad3LH5QkQ13hqWpSrtCIQbrJ8TmT'

auth_key = '%s:%s' % (client_id, client_secret)

response = requests.post(
    url='http://127.0.0.1:8000/token/',
    data=dict(grant_type='client_credentials'),
    headers={
        'Authorization': 'Basic %s' % base64.b64encode(auth_key.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded',
    }
)


protected_data = requests.get(
    url='http://127.0.0.1:8000/protected_data/',
    headers={
        'Authorization': 'Bearer %s' % response.json()['access_token']
    }
    )

print(protected_data.json())
print(response.json())
