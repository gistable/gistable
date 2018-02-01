# coding: utf-8
#
# fuckda.py - Uso de certificados de la FNMT con Python
#
# Autor: Juan Luis Cano Rodríguez <juanlu001@gmail.com>
#
# Instrucciones:
#
# 1. Exportar certificado (CERTIFICADO.p12)
#    https://www.sede.fnmt.gob.es/preguntas-frecuentes/exp-imp-y-elim-de-certificados
# 2. Extracción de la clave privada
#    $ openssl pkcs12 -in CERTIFICADO.p12 -nocerts -out cert.key
# 3. Extracción del certificado
#    $ openssl pkcs12 -in CERTIFICADO.p12 -clcerts -nokeys -out cert.crt
# 4. Ejecución del script
#    $ python fuckda.py
# 5. Visualización del resultado
#    $ python -m http.server & xdg-open http://0.0.0.0:8000/output.html

import os.path
import requests

URL = 'https://apuc.cert.fnmt.es/appsUsuario/comprobacion/ChequearCert'

CERT = os.path.abspath("cert.crt")
KEY = os.path.abspath("cert.key")

req = requests.get(URL, cert=(CERT, KEY), verify=False)

with open("output.html", 'wb') as f:
    content = req.text.encode(req.encoding)
    f.write(content)
