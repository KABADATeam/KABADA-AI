import requests

pload = {'username': 'Olivia', 'password': '123'}
# r = requests.post('http://localhost:2222/post_json', data=pload, verify=False)
r = requests.post('http://localhost:2222/post_json', json=pload, verify=False)
print(r.text)