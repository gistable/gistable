#!/usr/bin/env python
import json
import os

import requests

def main():
    module = AnsibleModule(
        argument_spec=dict(
            cert_path=dict(required=True),
            key_path=dict(required=True),
            names=dict(type='list', required=True),
            common_name=dict(required=True),
            hosts=dict(type='list', required=True),
            cfssl_url=dict(default='http://localhost:8888')
        ),
        supports_check_mode=True,
    )

    cert_path = module.params['cert_path']
    key_path = module.params['key_path']
    names = module.params['names']
    common_name = module.params['common_name']
    hosts = module.params['hosts']
    cfssl_url = module.params['cfssl_url']

    changed = False

    if not os.path.exists(cert_path):
        if not module.check_mode:
            url = cfssl_url + '/api/v1/cfssl/newcert'

            data = {
                'request': {
                    'CN': common_name,
                    'names': names,
                    'hosts': hosts,
                }
            }

            # NOTE json kwarg not present in older versions of requests
            response = requests.post(url, data=json.dumps(data)).json()

            with open(cert_path, 'w') as fp:
                fp.write(response['result']['certificate'])

            # FIXME should use umask or similar to ensure file is never world readable
            with open(key_path, 'w') as fp:
                fp.write(response['result']['private_key'])

        changed = True

    module.exit_json(changed=changed)

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
