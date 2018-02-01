import requests

def get_data_doc_number(user, password, tipo_doc, numero_doc, format='json'):
    '''
        # url = 'http://py-devs.com:8888/api'
        url = 'http://py-devs.com/api'
        tipo_doc = 'dni' o 'ruc'
    '''
    url = 'http://py-devs.com/api'
    # url = 'http://localhost:8000/api'
    url = '%s/%s/%s' % (url, tipo_doc, str(numero_doc))
    res = {'error': True, 'message': None, 'data': {}}
    try:
        response = requests.get(url, auth=(user, password))
    except requests.exceptions.ConnectionError, e:
        res['message'] = 'Error en la conexion'
        return res

    if response.status_code == 200:
        res['error'] = False
        res['data'] = response.json()
    else:
        try:
            res['message'] = response.json()['detail']
        except Exception, e:
            res['error'] = True
    return res


res = get_data_doc_number('demorest', 'demo1234', 'dni', '09389109', format='json')
print 'error', res['error']
print 'message', res['message']
print 'data', res['data']

res = get_data_doc_number('demorest', 'demo1234', 'ruc', '20100017491', format='json')
print 'error', res['error']
print 'message', res['message']
print 'data', res['data']