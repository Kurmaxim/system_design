import requests,json


for i in range(1001,100000):
    url = 'http://localhost:8000/users/?tags=Users'
    headers = {'content-type': 'application/json', 'accept': 'application/json'}
    user = dict()
    user['first_name']=f'Ivan{i}'
    user['last_name']=f'Ivanov{i}'
    json_request = json.dumps(user, ensure_ascii=False).encode('utf-8')
    response = requests.post(url = url,headers=headers,data=json_request)
    if response.status_code != 200:
        print(response.status_code)
        break