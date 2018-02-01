# Instalación de paqueterias
sudo apt-get install libapache2-mod-wsgi

# Vamos a la carpeta
cd /etc/apache2

# Agregamos esta linea dentro del http.conf (site 1, site 2, depende la configuración de sus virtual host) Tiene que apuntar directo a un archivo .wsgi que tiene que estar preferente mente alado de la carpeta de su proyecto.

WSGIScriptAlias / /home/ajamaica/django.wsgi

# Reinicien apache si algo falla debuggen con :
tail -f 100 /var/log/apache2/error.log

# El archivo django.wsgi debe contener (recuerden borrar todo lo que tenga #)

import os
import sys

path = '/home/ajamaica/' # Cambiar a ruta actual
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'curso.settings'  # Nombre de su proyecto dando la ubicación del modulo

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# Reinicien apache y recen un poquito. 

# Algunos tips. 
- Si usan SSL creen otro virtual host y hagan redirects directo en el httpdconf. 
- Usen Postgresql
- No copien los archivos media. Solo haz un simblink y permitan /admin_media/ a la ruta de dist-packages de django. Así todo lo que este en su server puede usar los mismos recursos. 

