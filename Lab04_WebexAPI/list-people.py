import requests
import json

access_token = ''
url = 'https://webexapis.com/v1/people'
headers = {
    'Authorization': 'Bearer {}'.format(access_token),
    'Content-Type': 'application/json'
}
params = {
    'email': '67070066@kmitl.ac.th'
}
res = requests.get(url, headers=headers, params=params)
print(json.dumps(res.json(), indent=4))

