import httplib2
import json
import time

base_url = 'http://localhost/services_test/api/external_tasks'

def t2():
    login_data = {
        'username': 'tasks',
        'password': 'tasks'
    }
    headers = {'Content-type': 'application/json'}
    http = httplib2.Http()
    response, json_content = http.request(
        base_url + '/user/login.json', 
        'POST', 
        headers=headers,
        body=json.dumps(login_data)
    )

    session_cookie = response['set-cookie']
    headers['Cookie'] = session_cookie

    node_url = base_url + '/node'
    r, c = http.request(
        node_url + '/1.json',
        'GET',
        headers=headers
    )

    node_data = {
        'title': 'Task.%s' % time.time(),
        'type': 'external_task',
        'field_data': {
            'und': [
                {"value": "Data",}
            ],
        },
    }
    r, c = http.request(
        node_url,
        'POST',
        headers=headers,
        body=json.dumps(node_data)
    )
    node_c = json.loads(c)
    nid = node_c['nid']

    update_data = {
        'field_data': {
            'und': [
                {"value": "New Data",}
            ],
        },
    }
    r, c = http.request(
        node_url + '/' + nid,
        'PUT',
        headers=headers,
        body=json.dumps(update_data)
    )
    print r, c


if __name__ == '__main__':
    t2()
