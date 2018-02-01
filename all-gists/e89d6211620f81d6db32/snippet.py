# -*- coding: utf-8 -*-
__author__ = 'alexdzul'
"""
El script identifica las carpetas llamadas "migrations" dentro de nuestro proyecto y elimina todos los archivos *.py
omitiendo los __init__.py.

Instrucciones:
=============
1. Copia este archivo "remove_migrations.py" dentro de la carpeta de tu proyecto.
    Ejemplo:
            MyProject/
                |-MyProject/
                |-manage.py
                |-README.md
                |-remove_migrations.py <---- Aqui va el archivo
2. Cambia el valor de la variable APPS_FOLDER con la ruta de la carpeta que contiene tus apps
3. Ejecuta el script con "python remove_migrations.py"

Advertencia:
============
-Se cuidadoso al utilizar este script ya que los archivos son eliminados permanentemente.
-Te sugerimos comprobar que has configurado correctamente la ruta de tu carpeta de aplicaciones en la variable "APPS_FOLDER"

Mejoras:
========
- Se integra compatibilidad con Python 3.
"""
import six
import os
import sys
from distutils.util import strtobool

# Cambiar el valor de acuerdo a la configuración de tu proyecto.
APPS_FOLDER = "AllPro/apps"  # <- Ruta de nuestra carpeta contenedora de apps


BASE_DIR = os.getcwd()  # <- Obtenemos la ruta de nuestro archivo.
FULL_PATH = os.path.join(BASE_DIR, APPS_FOLDER)  # <- Ruta completa para iniciar el proceso de eliminado


def delete_migrations_files():
    """
    Author: Alex Dzul @alexjs88
    Función que nos permite recorrer las carpetas de nuestro proyecto y elimina archivos que se encuentren en las
    carpetas llamadas "migrations".
    Nota: La función omite la eliminación de los archivos __init__.py
    """
    num_compile_files = num_migrations_files = 0
    print("\nAnalizing your project .... \n")
    for (path, ficheros, archivos) in os.walk(FULL_PATH):
        if 'migrations' in ficheros:  # <- Si existe una carpeta entonces continua el flujo
            for fichero in ficheros:  # <- Recorre los ficheros
                if fichero == "migrations":  # <-- Si encuentra una carpeta migrations entonces entra a ellas
                    migrations_path = os.path.join(path, fichero)
                    for (child_path, ficheros_2, archivos_2) in os.walk(migrations_path):
                        for archivo in archivos_2:
                            file_path = os.path.join(child_path, archivo)
                            if archivo[-3:] == "pyc":  # Si son compilados entonces eliminamos
                                os.remove(file_path)
                                print("[Compiled File] ", file_path)
                                num_compile_files += 1
                            else:
                                if not archivo == "__init__.py":  # <- Excluye los archivos __init__.py
                                    if archivo[-2:] == "py":  # <- Si es un archivo *.py lo elimina
                                        os.remove(file_path)
                                        print("[Migration File] ", file_path)
                                        num_migrations_files += 1
    print("\n======================= Execution Summary ===========================")
    if num_compile_files == 0 and num_migrations_files == 0:
        print("All your migrations folder are empty. Nothing was deleted")
    else:
        print("Python files: {0}".format(num_migrations_files))
        print("Compiled Python files: {0}".format(num_compile_files))
    print("=====================================================================\n")


def user_yes_no_query():
    """
    Author: Alex Dzul @alexjs88
    Función que muestra en pantalla un aviso para que el usuario responde YES o NO.
    Si responde YES --> Se ejecuta la función delete_migrations_files()
    Si responde NO ---> La función se detiene sin ninguna acción a ejecutar.
    Si responde algo más --> La función solicita escribir una respuesta válida Y/N.
    """
    sys.stdout.write('Are you sure you want to delete all migrations files? [y/n]: ')
    while True:
        try:
            if six.PY2:  # Python 2?
                respuesta = strtobool(raw_input().lower())
            else:  # Python 3
                respuesta = strtobool(input().lower())
            if respuesta:
                delete_migrations_files()
            else:
                sys.stdout.write('\nOk, nothing was deleted\n\n')
            return True
        except ValueError:
            sys.stdout.write('Please enter: \'y\' o \'n\'.\n')


user_yes_no_query()  # Ejecuta el script