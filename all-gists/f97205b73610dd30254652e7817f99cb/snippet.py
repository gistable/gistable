# solution for:
# https://stackoverflow.com/questions/12544056/how-to-i-get-the-current-ipython-notebook-name
#
# aimed at:
# IPython 4.2.0 and Python 3.5

import json
import os
import urllib.request
import ipykernel
connection_file_path = ipykernel.get_connection_file()
connection_file = os.path.basename(connection_file_path)
kernel_id = connection_file.split('-', 1)[1].split('.')[0]

response = urllib.request.urlopen('http://127.0.0.1:8888/api/sessions')
sessions = json.loads(response.read().decode())
for sess in sessions:
    if sess['kernel']['id'] == kernel_id:
        print(sess['notebook']['path'])
        break