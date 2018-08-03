import requests


client_id = '4PCZ8MisjtQKwDNQw0SjYGrp032e1xoz029i6NqW'
client_secret = 'rguCFxVUY37VBnSumVfsMJchNNJRNQRfeqoez9fE7R3fpm9ZF3hKPcPYs3oEfFYeY1Qw' \
                'P89H5Voe51UnnmjENQWgVcUzrwttY9Zhad3LH5QkQ13hqWpSrtCIQbrJ8TmT'

url = 'http://127.0.0.1:8000/token/token?grant_type=client_credentials&client_id={id}&' \
              'client_secret={secret}'.format(id=client_id, secret=client_secret)

response = requests.post(url)
print(requests.post(url))
