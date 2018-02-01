import re
import time

import requests


URL = 'https://mobile.rwe-smarthome.de/MobileWeb'
request_validation_re = re.compile(r'<input name="__RequestVerificationToken" type="hidden" value="(.*?)" />')


def main():
    session = requests.Session()
    res = session.get(URL + '/Logon/Logon')

    tokens = request_validation_re.findall(res.text)

    res = session.post(
        'https://mobile.rwe-smarthome.de/MobileWeb/Logon',
        data={
            '__RequestVerificationToken': tokens[0],
            'UserName': '<YOUR USERNAME>',
            'Password': '<YOUR PASSWORD>',
            'RememberMe': 'false',
            'ReturnUrl': '',
            'LanguageDropDown': 'Deutsch'
        }
    )
    assert res.status_code == 200

    variable_id = '5d6b996d-4af8-c0b5-bb3c-f69ed60b2bd0'

    res = session.get(
        URL + '/JsonApi/GetLogicalDeviceState',
        params={
            '_': int(time.time()),
            'Type': 'LogicalDeviceState',
            'Value': 'null',
            'IsResolveRequired': 'true',
            'Metadata': '',
            'Id': variable_id
        },
        headers={
            'X-Requested-With': 'XMLHttpRequest'
        }
    )
    print res.text

    res = session.get(
        URL + '/JsonApi/SetActuatorValue/',
        params={
            '_': int(time.time()),
            'Id': variable_id,
            'Value': '1',
            'IsContainer': 'false'
        },
        headers={
            'X-Requested-With': 'XMLHttpRequest'
        }
    )
    print res.text

if __name__ == '__main__':
    main()
