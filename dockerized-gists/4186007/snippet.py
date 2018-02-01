# -*- coding: utf-8 -*-

## Basado en el script originalmente publicado en
## http://www.jansipke.nl/using-python-to-add-new-posts-in-wordpress/

import datetime
import xmlrpclib
from xml.sax.saxutils import escape
import json
import markdown
import time

def html2(text = '', html = ''):
    if 'YouTubeVideo' in text:
        for linea in html:
            if 'src=' in linea:
                kk = (linea.split('src=')[1]).split('\n')[0]
                return 'youtube', kk.split('embed/')[1].split('"')[0]
    elif 'HTML' in text:
        for linea in html:
            if 'src=' in linea:
                return 'url', (linea.split('src=')[1]).split(' ')[0]
    else:
        return 'cagada', None

## Parámetros a introducir por el usuario
wp_url = "http://tublog.wordpress.com/xmlrpc.php"
wp_username = "usuario"
wp_password = "password"
notebook = '/ruta/a/tu/fichero.ipynb'
wp_blogid = ""
## No habría que tocar nada más, en principio

datosnb = json.loads(open(notebook, 'r').read())
server = xmlrpclib.ServerProxy(wp_url)

## Título del post
title = escape(datosnb['metadata']['name'])

post = ""

## posibles formatos de salidas (añadid las que queráis)
formats = ['png','jpg','jpeg','gif','html']

cont = 0

for celda in datosnb['worksheets'][0]['cells'][:]:
    
    if celda['cell_type'] == 'markdown':
        
        for info in celda['source'][:]:
            post += markdown.markdown(info)
            post += """\n"""
        
    if celda['cell_type'] == 'code' and celda['language'] == 'python':
        
        post += """[sourcecode language='python']\n"""
        
        for linea in celda['input'][:]:
            
            post += """%s""" % linea
            
        post += """[/sourcecode]"""
        post += """\n"""
        
        if celda['outputs']:
            
            post += """La salida del anterior código mostrará lo siguiente"""
            post += """\n"""
            
            for output in celda['outputs'][:]:
                
                for formato in formats:
                    
                    if formato in output.keys():
                        
                        if formato != 'html':
                            
                            fich = (output[formato]).decode('base64')
                            fich = xmlrpclib.Binary(fich)
                            if formato == 'jpg':
                                
                                ext = 'jpeg'
                                
                            else:
                                
                                ext = formato
                                
                            imgtitle = title.replace(' ','_').replace('.','-')
                            data = {'name': imgtitle + str(cont) + '.' + ext,
                                    'type': 'image/' + ext,
                                    'bits': fich,
                                    'overwrite': 'true'}
                            cont += 1
                            image_id = server.wp.uploadFile(wp_blogid, 
                                                            wp_username, 
                                                            wp_password, 
                                                            data)
                            urlimg = image_id['url']
                            post += """<img src="%s"/>""" % urlimg
                            post += """\n"""
                            
                        else:
                            
                            salida, url = html2(text = output['text'][0], 
                                                html = output[formato])
                            if salida == 'youtube':
                                kk = '[youtube=http://www.youtube.com/watch?v='
                                post += """%s%s]\n""" % (kk, url)
                            if salida == 'url':
                                post += """Link a <a href="%s">%s</a>\n""" % (url, url)
                            post += """\n"""

date_created = xmlrpclib.DateTime(datetime.datetime.now())
## La categoría debe existir previamente en el blog
## Se podrían comprobar las categorías del blog y crearlas si no existen
## pero eso vendría en la próxima iteración
categories = ["Recursos"]
tags = [ "ipython", "XML-RPC", "prueba de concepto"]
wp_blogid = ""
status_published = 0
data = {'title': title, 
        'description': post,
        'post_type': 'post',
        'dateCreated': date_created,
        'mt_allow_comments': 'open',
        'mt_allow_pings': 'open',
        'post_status': 'draft',
        'categories': categories, 
        'mt_keywords': tags}
post_id = server.metaWeblog.newPost(wp_blogid, 
                                    wp_username, 
                                    wp_password, 
                                    data, 
                                    status_published)