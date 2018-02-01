# coding:utf-8

import requests
import pytesseract
from bs4 import BeautifulSoup
from cStringIO import StringIO
from PIL import Image

SUNAT_FORM_URL = 'http://ww1.sunat.gob.pe/cl-ti-itmrconsruc/'


def ruc_info_from_dni(dni):
    session = requests.Session()
    session.get(SUNAT_FORM_URL + 'jcrS00Alias')
    session.get(SUNAT_FORM_URL + 'frameCriterioBusqueda.jsp')
    captcha = session.get(SUNAT_FORM_URL + 'captcha?accion=image&nmagic=0')
    captcha = pytesseract.image_to_string(Image.open(StringIO(captcha.content)))
    formdata = {
        'accion': 'consPorTipdoc',
        'razSoc': '',
        'nroRuc': '',
        'nrodoc': dni,
        'contexto': 'ti - it',
        'search1': '',
        'codigo': captcha,
        'tQuery': 'on',
        'tipdoc': '1',
        'search2': dni,
        'coddpto': '',
        'codprov': '',
        'coddist': '',
        'search3': '',
    }

    result = session.post(SUNAT_FORM_URL + 'jcrS00Alias', data=formdata)
    result = BeautifulSoup(result.content, 'html.parser')
    result = [td.text.strip() for td in
              result.find('table', attrs={'cellpadding': 2}).find_all('td')]
    result = list(zip(*[iter(result)] * 4))
    return [
        {'ruc': item[0],
         'name': item[1],
         'location': item[2],
         'status': item[3]}
        for item in result
    ]

# Returns [{'status': u'_', 'ruc': u'_', 'name': u'_', 'location': u'_'}] or []
print ruc_info_from_dni('________')
