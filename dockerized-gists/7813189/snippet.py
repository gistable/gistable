#coding=utf-8

"""
Por: Rafa Vázquez
http://sloydev.com/

Este script genera una animación gif a partir de un archivo de vídeo, colocando opcionalmente un fondo en cada frame.
Está pensado para convertir los vídeos obtenidos en Android mediante 'adb shell screenrecord' o con la herramienta de Android Studio.
Un ejemplo del resultado puede verse en http://i.imgur.com/Opu5aG3.gif

Requiere:
- ffmpeg en línea de comandos (http://www.ffmpeg.org/)
- imagemagick en línea de comandos (http://www.imagemagick.org/)
En OSX se pueden instalar fácilmente con homebrew. En Linux supongo que se podrán instalar por repositorio. En Windows, pues no he mirado.

OJO: Es el producto/prueba de un par de horas de investigación en Google, no esperes gran cosa.
Hay cosas mejorables, algunas obvias que no tengo ganas ni tiempo de hacer ahora; y otras no tan obvias que necesitarían más investigación.
Ha sido desarrollado y probado bajo OSX con un par de vídeos solamente. Osease, tendrá fallos no controlados. 
Debería funcionar bien en Linux teniendo instaladas las herramientas anteriores, y en Windows habría que cambiar ligeramente los parámetros de inicialización. Creo.

Mejoras obvias:
- Tratar la resolución dinámicamente según la entrada y adaptar la salida a escala.
- Permitir configuración mediante entrada de parámetros en línea de comandos.
- Configurar / ajustar la posición de los frames respecto al fondo, en vez de centrarlo y punto. So chapucero!
- Hacer la inicialización en condiciones, no esos comandos en bruto que petarán en Windows y quedan feos.
- Comprobación de requisitos. Que te avise si falta por instalar algo en vez de explotar y ya.
- Uso de apis (si hay) en vez de ejcutar comandos por os.system(). Seguro que alguna contraindicación habrá.
- Traducción al inglés. Hoy me dio por escribir los comentarios y demás en español, tampoco creo que el script llegue más allá.

Mejoras no tan obvias:
- Que la imagen final no pese tantísimo, sin perder demasiada calidad. Otros métodos que probé dejan resultados feos. Quizá sea cuestión de encontrar un equilibrio, no me dio por probar mucho.

Comenta si te sirve, tanto para usarlo como para hacer tu propio mecanismo. No seas rata ;)
Si te apetece contribuír mejoras (no ideas, código xD) comenta y lo iré actualizando ^^

Referencias / "no habría sido posible sin...": 
- http://stackoverflow.com/questions/12100072/how-to-extract-slides-from-a-video-using-python
- https://github.com/lelandbatey/configDebDev/blob/master/helpFiles.md#converting-videos-to-animated-gifs
- http://www.imagemagick.org/script/composite.php
- http://www.imagemagick.org/Usage/anim_basics/

Imagen usada de fondo para capturas con un Nexus 5: http://imgur.com/kfbDbTp (cutre, lo sé xD)
"""

import os

VIDEO_FILE = "video.mp4"
OUTPUT_FILE = "anim.gif"
DEVICE_FILE = "background.jpg"

FRAMES_DIR = "./frames/"
COMPOSITE_DIR = "./composite/"

SCREENSHOTS_RESOLUTION = "270x480"
FPS = 7 #Frames per second to capture. The more, the bigger (filesize)
USE_DEVICE_FRAME = True
DEBUG = False


# Crea las carpetas necesarias, prepara el estado inicial del script
os.system("rm -r frames")
os.system("rm -r composite")
os.system("mkdir composite")
os.system("mkdir frames")

# Saca los frames del vídeo
print 'Sacando frames del vídeo...'
extract_frames_command = "ffmpeg -i video.mp4 -r {} -s {} -f image2 {}img%3d.png".format(FPS, SCREENSHOTS_RESOLUTION, FRAMES_DIR)
os.system(extract_frames_command)

file_names = sorted((fn for fn in os.listdir(FRAMES_DIR) if fn.endswith('.png')))

if DEBUG: raw_input("Frames extraídos, pulsa enter para continuar")

# Junta los frames con el marco del móvil
if USE_DEVICE_FRAME:
	print 'Poniendo frames sobre el fondo...'
	for i, fname in enumerate(file_names):
		output_file = COMPOSITE_DIR+fname
		input_file = FRAMES_DIR+fname
		os.system('composite -gravity center {} {} {}'.format(input_file, DEVICE_FILE, output_file))

	if DEBUG: raw_input("Marco del dispositivo adjuntado, pulsa enter para continuar")

# Crea un gif a partir de los frames sueltos
print 'Creando gif a partir de los frames...'
final_frames_dir = COMPOSITE_DIR if USE_DEVICE_FRAME else FRAMES_DIR
make_gif_command = "convert -layers Optimize -delay 1x{} {}img*.png {}".format(FPS, final_frames_dir, OUTPUT_FILE)
os.system(make_gif_command)

print "Listo! :)"