# -*- coding: cp1252 -*-
'''
[Programación en Python]
'''
'''
Python tiene veintiocho palabras clave:

and       continue  else      for       import    not       raise 
assert    def       except    from      in        or        return 
break     del       exec      global    is        pass      try 
class     elif      finally   if        lambda    print     while 
'''

'''
Operadores

__add__(self,other)
__sub__(self,other)
__mul__(self,other)
__floordiv__(self,other)
__mod__(self,other)
__divmod__(self,other)
__pow__(self,other)
__and__(self,other)
__xor__(self,other)
__or__(self,other)
'''

'''
and  exec	not
assert	finally	or
break	for	pass
class	from	print
continue	global	raise
def	if	return
del	import	try
elif	in	while
else	is	with
except	lambda	yield
'''
'''
import os
retvalue = os.system("ps -p 2993 -o time --no-headers")
print retvalue
  
import subprocess as sub
p = sub.Popen('your command',stdout=sub.PIPE,stderr=sub.PIPE)
output, errors = p.communicate()
print output
  
import os
p = os.popen('command',"r")
while 1:
    line = p.readline()
    if not line: break
    print line
  
output = subprocess.check_output(["command", "arg1", "arg2"]);
'''
'''
random.random() # devuelve un float en el intervalo [0,1)

random.uniform(a,b) # devuelve un float en el intervalo [a,b)

random.choice(lista) # escoge un elemento al azar

 random.randint(10,30)
'''
#298

import sys,os

class Servicio:

  def __init__(self):
    print "Inicio"

  def getSistema(self):#nt, posix
    return os.name

  def getPlataforma(self):#win32,win64,linux2,darwin
    return sys.platform

  def windows(self):
    print "estas en un sistema Windows"

  def linux(self):
    print "estas en un sistema Linux"

  def macosx(self):
    print "estas en un sistema Mac OS"



def main():
  servicio=Servicio()

  if servicio.getPlataforma()=="win32" or servicio.getPlataforma()=="win64" and servicio.getSistema()=="nt":
    servicio.windows()
  elif servicio.getPlataforma()=="linux2" and servicio.getSistema()=="posix":
    servicio.linux()
  else:
    macosx()


if __name__=="__main__":
  main()


#297
'''
class Base(object):
    def __init__(self):
        print "Inicio de la clase Base"
 
    def __del__(self):
        print "Fin de la clase Base"
 
 
class Miembro(object):
    def __init__(self):
        print "Inicio de la clase Miembro"
 
    def __del__(self):
        print "Fin de la clase Miembro"
 
 
class Hija(Base):
   
    Miembro1 = Miembro()
 
 
c = Hija()
 
del(c)
'''

#296

'''
archivo=open('archivo.txt').read(200)
escritura= open('prueba.txt','ab').write(archivo)

'''

#295

'''
archivo=open('archivo.txt').read()
escritura= open('prueba.txt','a').write(archivo)

'''

#294
'''
archivo=open('archivo.txt').read(100)
escritura= open('prueba.txt','wb').write(archivo)
'''

#293
'''
archivo=open('archivo.txt').readlines()
escritura= open('prueba.txt','w').writelines(archivo)
'''

#292
'''
archivo=open('archivo.txt').read()
escritura= open('prueba.txt','w').write(archivo)
'''

#291
'''
archivo= open('archivo.txt', 'rb')
try:
    while True:
        trozo= archivo.read(10)
        if not trozo:
            break
        print trozo+"@@"
finally:
    archivo.close( )
'''

#290
'''
archivo = open('archivo.txt')
try:
    for linea in archivo:
     print linea
finally:
    archivo.close( )
'''
#289
'''
archivo = open('archivo.txt')
try:
    lista_x_lineas= archivo.read().split('h')
    print lista_x_lineas[0]
finally:
    archivo.close( )

'''

#288
'''
archivo = open('archivo.txt')
try:
    lista_x_lineas= archivo.read().splitlines()
    print lista_x_lineas[0]
finally:
    archivo.close( )
'''

#287
'''
archivo = open('archivo.txt')
try:
    lista_x_lineas= archivo.read().splitlines()
    print lista_x_lineas[0]
finally:
    archivo.close( )
'''

#286
'''
archivo = open('archivo.txt')
try:
    contenido = archivo.read()
    print contenido
finally:
    archivo.close( )
'''

#285
'''
books = ["The Pragmatic Programmer", "Code Complete", "Programming Perls", "The Mythical Man Month"]
print "original: ",books
books.sort()
print "ordenado: ",books
'''

#284
'''
from Tkinter import*
import sys
from math import*
 
def Factorial(n):
  if n==0:
    return 1
  else:
    return n*Factorial(n-1)

def Obtener_Fact():
  print "El factorial del número : ",numero.get()," es ",Factorial(numero.get())
  res=Factorial(numero.get())
  lblt=Label(Formulario1,text="Resultado: "+str(res))
  lblt.grid(row=3,column=0)
#------------------------------------------------------------------------------------------
Formulario1=Tk()
Formulario1.title('[Factorial]')
Formulario1.resizable(width=TRUE,height=TRUE)
#------------------------------------------------------------------------------------------
Etiqueta=Label(Formulario1,text="Factorial del número")
numero=IntVar()
txtnumero=Entry(Formulario1,textvariable=numero,width=15)

BotonCalcula=Button(Formulario1,text="Calcular",command=Obtener_Fact,width=10)
txtnumero.grid()
Etiqueta.grid()
BotonCalcula.grid(row=0,column=1)
BotonSalir=Button(Formulario1,text="Salir",command=exit,width=10)
BotonSalir.grid(row=1,column=1)

#------------------------------------------------------------------------------------------
Formulario1.mainloop()
#------------------------------------------------------------------------------------------
'''


#283
'''
import sys

def activa():
  print "estas trabajando sobre un sistema windows"

def mensaje():
  print "estas trabajando en un sistema diferente a Windows"

def main():
  sistema=sys.platform
  
  if sistema=="win32" or sistema=="win64":
    activa()
  else:
    mensaje()

if __name__=="__main__":
  main()
'''

#282
'''
import os,sys
so=os.name
platf=sys.platform
print "sistema operativo: ",so," plataforma: ",platf
'''

#281
'''
print "I need to practice more English" if True else "I need more fun"
teams = ["Packers", "49ers", "Ravens", "Patriots"]
for index, team in enumerate(teams):
    print index, team

numbers = [1,2,3,4,5,6]
even = []
for number in numbers:
    if number%2 == 0:
        even.append(number)

print even


numbers = [1,2,3,4,5,6]
even = [number for number in numbers if number%2 == 0]
print even


teams = ["Packers", "49ers", "Ravens", "Patriots"]
print {key: value for value, key in enumerate(teams)}


items = [0]*3
print items


teams = ["Packers", "49ers", "Ravens", "Patriots"]
print ", ".join(teams)



data = {'user': 1, 'name': 'Max', 'three': 4}
try:
    is_admin = data['admin']
except KeyError:
    is_admin = False




data = {'user': 1, 'name': 'Max', 'three': 4}
is_admin = data.get('admin', False)

#http://maxburstein.com/blog/python-shortcuts-for-the-python-beginner/

'''

#280
'''
class Persona:

  def __init__(self,nombre,edad):
    self.nombre=nombre
    self.edad=edad

  def getNombre(self):
    return self.nombre

  def getEdad(self):
    return self.edad



def main():
  persona= Persona("Fernando",30)
  print "nombre: ",persona.getNombre(),"  edad: ",persona.getEdad()


if __name__=="__main__":
  main()
'''

#279
'''
import os, sys

def main():
  nombre="Fernando"
  edad=2
  cad= "vacio" if (nombre=="" or edad<=0) else "lleno"
  print cad


if __name__=="__main__":
  main()
'''

#278 lambda
'''
lista=[2,4,6,8,10,12]
print reduce(lambda x,y: x+y,lista)#42
print map(lambda x: x**2,lista)#[4, 16, 36, 64, 100, 144]
print filter(lambda x: x%3==0,lista)#[6,12]
'''

#277 lambda
'''
doble=lambda x: x**2
numero=3
print "el doble de %d es %d"%(numero,doble(numero))

lista=[23,33,45,55,61,72,89,92,102,190,209,288]
print filter(lambda x: x%5==0,lista)
print map(lambda x: x**2,lista)
print reduce(lambda x, y: x+y,lista)
'''


#276
'''
import sys,os

cont=1
codigo=""
def main():
  global cont,codigo
  try:
    codigo="type "+str(sys.argv[0])
    cad=str(sys.argv[1])
    lista=list(cad)

    for i in lista:
      print i, " no. ",cont
      cont=cont+1

    os.system(codigo)

  except IOError as e:
    print e

if __name__=="__main__":
  main()
'''

#275
'''
import sys,os

def validar(nombre):
  if sys.argv[1]==nombre:
    print "correcto"
    sys.exit()

  else:
    print "usuario no aceptado"

def main():
  nombre="fernando"
  try:
    validar(nombre)
  except TypeError, ValueError:
    print "Error"

if __name__=="__main__":
  main()

'''

#274
'''
class Vehiculo:
  velocidadMaxima=120

  def acelerar(self,a):
    print "mas rapido ",a

  def frenar(self):
    print "parar"


class Camion(Vehiculo):
  velocidadMaxima=100

  def carga(self,c):
    print "mi carga ",c

  def frenar(self):
    Vehiculo.frenar(self)
    print "frenazo del camion"


def main():
  v=Vehiculo()
  v.acelerar(120)
  c=Camion()
  
  c.carga(v)
  c.acelerar(450)
  c.frenar()

if __name__=="__main__":
  main()

'''


#273
'''
dicc={'nombre':'Fernando','edad':32,'direccion':'zaragoza','lenguajes':['Python','Groovy','Scala']}
print dicc
print dicc.has_key('nombre')
print dicc.items()
for i in dicc:
  print"llave: ",i,"  valor: ",dicc[i]

otro=dicc.copy()
print otro
dicc.clear()
print dicc
'''
#272
'''
lista=[2,4,6,8,10,12,2,453,4,32,2,"Fer"]
print "datos: ",lista
print"no. de 2 en la lista: ",lista.count(2)
print"no. de str en la lista: ",lista.count("Fer")
cad="Fernando"
otra=list(cad)
otra.reverse()
print "lista en reversa: ",otra
'''
#271
'''
import random

lista=[]
rango=range(0,7)

for i in rango:
  lista.append(random.uniform(i,9))

print "lista: ",lista
'''
#270
'''
import random

lista=[]
rango=range(0,7)

for i in rango:
  lista.append(random.random())

print "lista: ",lista
'''

#269
"""
http://pastebin.com/BZ9XRg8Z
Endlessly bouncing ball - demonstrates animation using Python and TKinter
"""
'''
import time
 
# Initial coordinates
x0 = 10.0
y0 = 30.0
 
ball_diameter = 30
 
# Get TKinter ready to go
from Tkinter import *
window = Tk()
canvas = Canvas(window, width=400, height=300, bg='white')
canvas.pack()
 
# Lists which will contain all the x and y coordinates. So far they just
# contain the initial coordinate
x = [x0]
y = [y0]
 
# The velocity, or distance moved per time step
vx = 10.0    # x velocity
vy = 5.0    # y velocity
 
# Boundaries
x_min = 0.0
y_min = 0.0
x_max = 400.0
y_max = 300.0
 
# Generate x and y coordinates for 500 timesteps
for t in range(1, 500):
 
    # New coordinate equals old coordinate plus distance-per-timestep
    new_x = x[t-1] + vx
    new_y = y[t-1] + vy
 
    # If a boundary has been crossed, reverse the direction
    if new_x >= x_max or new_x <= x_min:
        vx = vx*-1.0
 
    if new_y >= y_max or new_y <= y_min:
        vy = vy*-1.0
 
    # Append the new values to the list
    x.append(new_x)
    y.append(new_y)
 
# For each timestep
for t in range(1, 500):
 
    # Create an circle which is in an (invisible) box whose top left corner is at (x[t], y[t])
    canvas.create_oval(x[t], y[t], x[t]+ball_diameter, y[t]+ball_diameter, fill="blue", tag='blueball')
    canvas.update()
 
    # Pause for 0.05 seconds, then delete the image
    time.sleep(0.05)
    canvas.delete('blueball')
 
# I don't know what this does but the script won't run without it.
window.mainloop()
'''

#268
'''
from Tkinter import *

def decimalABinario():
  numeroBinario=""
  resto=0
  numeroDecimal=int(texto.get())
  while (numeroDecimal>=2):
    resto=numeroDecimal%2
    numeroDecimal=(int)(numeroDecimal/2)
    numeroBinario+=(str)(resto)
  numeroBinario+=(str)(numeroDecimal)
  lista=list(numeroBinario)
  lista.reverse()
  print "\nNumero decimal leido: ",texto.get(),"\nNumero binario obtenido: ",lista

def quitar():
  exit()

root=Tk()
root.title('Decimal a binario')

lblDecimal=Label(root,text="Número decimal: ")
lblDecimal.grid(row=0,column=0)

texto=StringVar()

txtMensaje=Entry(root,textvariable=texto)
txtMensaje.grid(row=0,column=1)

btnCalcular=Button(root,text="Calcular",command=decimalABinario,width=20)
btnCalcular.grid(row=0,column=2)

btnQuitar=Button(root,text="Quitar",command=quitar,width=20)
btnQuitar.grid(row=0,column=3)

root.mainloop()
'''


#267
'''
import os,sys

def inicio():
  os.system("python -V")

inicio()
'''

#265
'''
import os, sys
os.system(sys.argv[1])
'''
#264
'''
import os

folder=os.getenv("temp")
print "Carpeta: ",folder
'''

#263
'''
import os, sys

def inicio(cmd):
  comando=os.popen(cmd)
  salida=comando.read()
  comando.close()
  return salida

print inicio(sys.argv[1])
'''


#262
'''
import sys,os

try:
  a=os.popen("netstat -b 5 > activas.txt")
  try:
    print "**************"
    print "  Conexiones"
    print "**************"
    for i in a.readlines():
      print i
  finally:
    print listo
except:
  print "Ha ocurrido un error"
'''

#261
'''
import os, sys
#ver conexiones activas 
try:
  a=os.popen("netstat")
  for linea in a.readlines():
    print linea

finally:
  print "Listo"

'''

#260
'''
import os, sys
os.system("help")
sys.exit(0)
'''

#259
'''
import os, sys

try:
  archivo=sys.argv[1]
  try:
    ejecuta="wscript "
    ejecuta+=archivo
    os.system(ejecuta)
  except IndexError,IOError:
    print "Ha ocurrido un error"
  finally:
    print "Listo"

except IOError,IndexError:
  print "Error, ha ocurrido un error"
'''

#258
'''
import os

try:
  archivo="archivo.vbs"
  try:
    ejecuta="wscript "
    ejecuta+=archivo
    os.system(archivo)
  finally:
    print "listo"
except IOError:
  print "Error"
'''

#257
'''
import os
print "Se puede invocar un programa"
os.system("wscript archivo.vbs")
'''
#256
'''
f = open("archivo.vbs","w")
f.write('set shell = createobject("wscript.shell") shell.run "nombre del archivo",vbhide ')
f.close()
'''
#255
'''
class Servicios:

  def __init__(self,num1,num2):
    self.num1=num1
    self.num2=num2
    print "Listo..."

  def suma(self):
    return self.num1 + self.num2

  def resta(self):
    return self.num1 - self.num2

  def producto(self):
    return self.num1 * self.num2

  def division(self):
    return self.num1 / self.num2

  

def main():
  obj=Servicios(20.0,3.0)
  

  print "num1: ",obj.num1
  print "num2: ",obj.num2
  print "Suma: ",obj.suma()
  print "Resta: ",obj.resta()
  print "Producto: ",obj.producto()
  print "Division: ",obj.division()


if __name__=="__main__":
  main()

'''


#254
'''
print ("[+] Usuario : Administrador")
 
 
usuario = ('gordo','flaco','negro')
usuario1 = input("Ingrese un usuario : ")
 
while(usuario1 in usuario):
    print("Usuario Correcto")
    break
else:
    print("Usuario Erroneo")
'''
 #253
'''
contrasena=input("Ingrese una Contraseña : ")
while (contrasena=="administrador"):
    print("Contraseña Correcta!")
    print("Bienvenido al programon papaaaa!")
    break
else:
    print("ContraseÃ±a Incorrecta!")
 
input()
'''

#252

'''
def vocal(entrada):
  for cont in entrada:
    print cont

vocal("Fernando")
'''

#251
'''
def vocal(entrada):

  for cont in entrada:
    #print cont
    if cont=='a': 
      return True
    elif cont=='e':
      return True
    elif cont=='i':
      return True
    elif cont=='o':
      return True
    elif cont=='u':
      return True
    else:
      return False


entrada=raw_input("Introduce texto: ")
numvocal=0
if vocal(entrada):
  numvocal+=1

print "no. vocales: ",numvocal

'''
#250

'''
numeroDecimal=0 
numeroBinario="" 
resto=0 
print "Numero decimal a binario" 
numeroDecimal=int(raw_input('Introduce numero decimal:')) 
print "Numero decimal leido: ",numeroDecimal 
while (numeroDecimal>=2): 
    resto=numeroDecimal%2 
    numeroDecimal=(int)(numeroDecimal/2) 
    numeroBinario+=(str)(resto) 

numeroBinario+=(str)(numeroDecimal) 
lista=list(numeroBinario) 
lista.reverse() 
print "Numero binario obtenido: ",lista  
'''

#249

'''
def vocal(entrada):
  a,e,i,o,u=0,0,0,0,0
  for cont in entrada:
    if cont=='a':
      a+=1
    elif cont=='e':
      e+=1
    elif cont=='i':
      i+=1
    elif cont=='o':
      o+=1
    elif cont=='u':
      u+=1
    else:
      print ""

  print "Vocales leidas:"
  print "no. de a leidas: ",a
  print "no. de e leidas: ",e
  print "no. de i leidas: ",i
  print "no. de o leidas: ",o
  print "no. de u leidas: ",u


entrada=raw_input("Introduce texto:")
vocal(entrada)  
'''


#248
'''
cont=0
valor=raw_input("Palabra: ")
for i in valor:
       cont+=1
print cont," caracteres"
'''

#247
'''
cad="Fernando"
abc=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','ñ','o','p','q','r','s','t','u','v','w','x','y,','z']
cont=0
for i in cad:
       print i,"",abc[cont]
       cont+=1
'''

#246
'''
cad="Fernando"
for i in cad:
       print i


lista=list(cad)
print lista

for i in lista:
       print i
'''

#245
 # File name: tkMessageBoxDemo.py
 # Author: S.Prasanna
'''
 import tkMessageBox
if __name__ == "__main__":
       root = Tk()
       root.title("tkMessageBox Demo Widget")
       root["padx"] = 20
       root["pady"] = 20
       tkinterLabel = Label(root)
       tkinterLabel["text"] = "tkMessageBox demo running...."
       tkinterLabel.pack()
       tkMessageBox.showinfo(title="Tk Info box", \
       message="This is a Tk Info/Message box used to display output")
       tkMessageBox.showerror(title="Tk Error message box", \
                              message="This is a Tk Error Message box used to display errors")
       tkMessageBox.showwarning(title="Tk Warning message box", \
                                message="This is a Tk Warning Message box used to display warnings")

    if (tkMessageBox.askokcancel(title="Tk Ok/Cancel box", \ message="Select an option, OK or Cancel") == 1):
           tkMessageBox.showinfo(title="Tk Ok/Cancel box", \
        message="You selected OK option")
    else:
      tkMessageBox.showinfo(title="Tk Ok/Cancel box", \
        message="You selected Cancel option")
     if (tkMessageBox.askretrycancel(title="Tk Retry/Cancel box", \
     message="Select an option, Retry or Cancel") == 1):
         tkMessageBox.showinfo(title="Tk Retry/Cancel box", \
        message="You selected Retry option")
     else:
       tkMessageBox.showinfo(title="Tk Retry/Cancel box", \
        message="You selected Cancel option")
    if (tkMessageBox.askyesno(title="Tk Yes/No box", \
   message="Select an option, Yes or No") == 1):
       tkMessageBox.showinfo(title="Tk Yes/No box", \
       message="You selected Yes option")
    else:
        tkMessageBox.showinfo(title="Tk Yes/No box", \
       message="You selected No option")
    if (tkMessageBox.askquestion(title="Tk Question box", \
    message="Is 1 + 1 = 2") == "yes"):
        tkMessageBox.showinfo(title="Tk Question box", \
      message="Correct Answer")
    else:
      tkMessageBox.showinfo(title="Tk Question box", \
        message="Wrong Answer")
 tkinterLabel["text"] = "tkMessageBox demo complete...."
 root.mainloop()

'''

#244

## {{{ http://code.activestate.com/recipes/578396/ (r1)
'''
import random
import sys
import string

def main(argv):

	if (len(sys.argv) != 5):
		sys.exit('Usage: simple_pass.py <upper_case> <lower_case> <digit> <special_characters>')
    
	password = ''
	
	for i in range(len(argv)):
		for j in range(int(argv[i])):
			if i == 0:
				password += string.uppercase[random.randint(0,len(string.uppercase)-1)]
			elif i == 1:
				password += string.lowercase[random.randint(0,len(string.lowercase)-1)]
			elif i == 2:
				password += string.digits[random.randint(0,len(string.digits)-1)]
			elif i == 3:
				password += string.punctuation[random.randint(0,len(string.punctuation)-1)]
	
	print 'You new password is: ' + ''.join(random.sample(password,len(password)))

if __name__ == "__main__":
	main(sys.argv[1:])
## end of http://code.activestate.com/recipes/578396/ }}}
'''


#243
'''
import time
import sys

def update_progress_bar():
	print '\b.',
	sys.stdout.flush()
	
print 'Iniciando ',
sys.stdout.flush()

#task 1
time.sleep(1)
update_progress_bar()

#task 2 
time.sleep(1)
update_progress_bar()

#task 3 
time.sleep(1)
update_progress_bar()

#Add as many tasks as you need. 

print ' Listo!'
'''


#242
'''
import time
import sys

def do_task():
	time.sleep(1)

def example_1(n):
	steps = n/10
	for i in range(n):
		do_task()
		if i%steps == 0:
			print '\b.',
			sys.stdout.flush()
	print ' Listo!'
	
print 'Iniciando ',
sys.stdout.flush()
example_1(100)
'''

#241
#http://thelivingpearl.com/2012/12/31/creating-progress-bars-with-python/
'''
import time
import sys

def do_task():
	time.sleep(1)

def example_1(n):
	for i in range(n):
		do_task()
		print '\b.',
		sys.stdout.flush()
	print ' Listo!'
	
print 'Iniciando',
example_1(10)
'''


#240
'''
import sys

#print "",sys.argv[0] #este es el nombre del programa
print "Hola: ",sys.argv[1]
nombre=sys.argv[1]
suma,num=0, 0
for i in range(len(nombre)):
       #print i
       i+=1
       print i
       num=int(i)
       suma+=num

print "No. de caracteres: %d"%(i)
print "Sumatoria: %d"%(suma)
'''


#239
#https://github.com/zebus3d

#!/usr/bin/env python
'''
import random, sys, os

def clear_so():
    # si el resultado de sys.plataform comienza con esas letras, entonces es unix:
    if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        os.system("clear") #Ejecutamos el comando propio de el sistema correspondiente.
    # si el resultado de sys.plataform comienza con esas letras, entonces es windows
    elif sys.platform.startswith("win") or sys.platform.startswith("dos") or sys.platform.startswith("ms"):
        os.system("cls") #Ejecutamos el comando propio de el sistema correspondiente.

clear_so()

animales = ["perro","gato","hamster","pato","gallina","gnu","serpiente","cabra"]
aa = random.choice(animales) # <-- palabra oculta
xx = list(aa) # lista o array con cada letra de la palabra
bb = [] # lista o array vacio

# rellenando el array con asteriscos el numero de veces correspondiente:
for i in xx:
    bb.append("*")

# impresion de los asteriscos en pantalla:
def asteriscos():
    for i in aa:
        #print("*", end=" ") # <-- python 3
        print "*",

# imprimimos lo que tenemos hasta el momento:
def imprimir():
    for i in bb:
    	print i,

# si es una letra unica en la palabra:
def accion1():
    pi = int( aa.index(ui[0]) ) # <-- posicion index de la letra introducida por el usuario.
    #print(pi)
    bb[pi] = ui[0] # <-- seteamos el valor introducido por el usuario en la posicion correspondiente.

# si existen mas de una cohincidencias en la misma palabra:
def accion2():
    pi = int( aa.index(ui[0]) ) # <-- posicion index de la letra introducida por el usuario.
    if aa.count(ui[0]) != 1: # <-- si son mas de una las cohincidencias entonces...

        total = len(aa) # <-- el total de letras de la palabra.
        cohincidencias = aa.count(ui[0]) # <-- el numero de repeticiones.
        #print "son muchos, son " + str( aa.count(ui[0]) ) # <-- el numero de repeticiones.

        for i in range(cohincidencias):
            if bb[pi] == ui[0]: # si lo que tengo ya hechco es lo mismo que la solicitud entonces...
                rest = aa[pi+1:] # a partir de lo que tengo en adelante -->
                #print(rest) # <-- el resto.
                pi = int( rest.index(ui[0]) - len(rest) ) # <-- consultams la pos d la letra en el resto y restamos el resto.
                bb[pi] = ui[0]	# <-- seteamos el valor introducido por el usuario en la posicion correspondiente.
            else:
                accion1()

asteriscos()
print("\n")

while bb != xx:
   #ui = input('Escribe un caracter: ') #- python 3 entrata de texto del usuario.
   ui = raw_input('Escribe una letra: ') # <-- entrata de texto del usuario.

   try:
      if (ui[0] in aa): # <-- si esa letra esta en la palabra oculta entonces...

         # si tiene mas de dos veces repetida la letra en la misma palabra:
         nc = int( aa.count(ui[0]) )
         if nc == 1:
            clear_so()
            accion1()
            imprimir()
            print("\n")
         else:
            clear_so()
            accion2()
            imprimir()
            print("\n")
      else:
         clear_so()
         imprimir()
         print("")
         print("No contiene la letra " + str(ui[0]) )

   except IndexError:
      # si no esciben nada
      clear_so()
      imprimir()
      print("")
      

# se termina el programa, el usuario acerto:
print("Felicidades acertaste!!")
'''


#238

'''
def fib(n):
       if n==0:
              return 1
       else:
              return n * fib(n-1)

def combinatorio(m,n):
       return fib(m)/ (fib(n)*fib(m-n))

print fib(5)
print combinatorio(6,2)
'''

#237

'''
class Alma:
       def hola(self):
              print "Hola soy Alma"

class Fernando(object):

       def __init__(self,object):
              self.object=object
       
       def algo(self):
              print "Debes hacer algo <<< dice Fer"

alma=Alma()
alma.hola()
fernando=Fernando(alma)
fernando.algo()

'''
       

#236
'''
class Fernando:
       pass

class Alma:
       def hola(self):
              print "Hola soy Alma"

class Hermanos(Fernando,Alma):
       pass

hermano=Hermanos()
hermano.hola()

'''

#235
'''
lista=[2,4,6,8,10,12]
print [x for x in lista]

lista2=[x for x in lista if x<10]
print lista2

lista3=[x for x in lista if x%3==0]
print lista3

for x in [x for x in lista if x%5==0]:
       print x

minimo=min(lista)
print minimo
maximo=max(lista2)
print maximo

print cmp(lista,lista2)
print cmp(lista,lista3)
print cmp(lista3,lista2)
'''


#234
'''
rango=range(0,12)
tam=len(rango)
lista=[]
cont=0
while cont < tam:
       if cont%3==0:
              lista.append(cont)
       cont+=1
print lista

print [x for x in lista]
print [x for x in lista if x%3==0]
print [x for x in lista if x%5==0]
print [x for x in lista if x%3==0 and x%5==0]
print [x**2  for x in lista if x>0]

for i,element in enumerate(lista):
       lista[i]='%d: %s'%(i,lista[i])
       print lista[i]
'''

#233

'''
dic={'nombre':'Fernando','edad':30}

print dic
print "nombre: ",dic['nombre']
print "edad: ",dic['edad']

dic['nombre']='Ariel'
dic['edad']=32
print dic

dic.clear()
print dic
'''

#232

'''
try:
       arch=open("prueba","w")
       try:
              arch.write("esta es una prueba")
       finally:
              print "listo"
              arch.close()

except IOError:
       print "ha ocurrido un error"

'''

#231
'''
def main():
       from math import sqrt, pow, sin
       x=9.021
       print "x= %f"%(x)
       raiz=sqrt(x)
       pot=pow(x,2)
       res=sin(x)
       print "raiz= %f , potencia= %f , seno= %f "%(raiz,pot,res)

if __name__=="__main__":
       main()
'''

#230
'''
cad='Hola usuario de Python'
lista=["Hola usuario",[3,44,21],type("cadena"),5.4]
tupla=(("queso","perro","maiz"),45,0.99,'c')
diccionario={'nombre':"Fernando",'edad':30,'profesion':"ingeniero",'telefono':"7221312456",'domicilio':"Toluca"}

print "Cadenas:"
print cad[0]
print cad[0:4]
print cad[3:7]
print cad[5:11]

print "\nListas:"
print lista[1]
print lista[0:3]

print "\nTuplas:"
print tupla[1]
print tupla[2:]

print "\nDiccionarios:"
print diccionario['nombre']

for i in diccionario:
       print i
'''

#229

'''
Function	Description
int(x [,base])

Converts x to an integer. base specifies the base if x is a string.

long(x [,base] )

Converts x to a long integer. base specifies the base if x is a string.

float(x)

Converts x to a floating-point number.

complex(real [,imag])

Creates a complex number.

str(x)

Converts object x to a string representation.

repr(x)

Converts object x to an expression string.

eval(str)

Evaluates a string and returns an object.

tuple(s)

Converts s to a tuple.

list(s)

Converts s to a list.

set(s)

Converts s to a set.

dict(d)

Creates a dictionary. d must be a sequence of (key,value) tuples.

frozenset(s)

Converts s to a frozen set.

chr(x)

Converts an integer to a character.

unichr(x)

Converts an integer to a Unicode character.

ord(x)

Converts a single character to its integer value.

hex(x)

Converts an integer to a hexadecimal string.

oct(x)

Converts an integer to an octal string.
'''


#228
'''
dict = {}
dict['one'] = "This is one"
dict[2]     = "This is two"

tinydict = {'name': 'john','code':6734, 'dept': 'sales'}


print dict['one']       # Prints value for 'one' key
print dict[2]           # Prints value for 2 key
print tinydict          # Prints complete dictionary
print tinydict.keys()   # Prints all the keys
print tinydict.values() # Prints all the values
'''


#227

'''
tuple = ( 'abcd', 786 , 2.23, 'john', 70.2  )
list = [ 'abcd', 786 , 2.23, 'john', 70.2  ]
tuple[2] = 1000    # Invalid syntax with tuple
list[2] = 1000     # Valid syntax with list

'''


#226

'''
tuple = ( 'abcd', 786 , 2.23, 'john', 70.2  )
tinytuple = (123, 'john')

print tuple           # Prints complete list
print tuple[0]        # Prints first element of the list
print tuple[1:3]      # Prints elements starting from 2nd till 3rd 
print tuple[2:]       # Prints elements starting from 3rd element
print tinytuple * 2   # Prints list two times
print tuple + tinytuple # Prints concatenated lists
'''


#225
'''
list = [ 'abcd', 786 , 2.23, 'john', 70.2 ]
tinylist = [123, 'john']

print list          # Prints complete list
print list[0]       # Prints first element of the list
print list[1:3]     # Prints elements starting from 2nd till 3rd 
print list[2:]      # Prints elements starting from 3rd element
print tinylist * 2  # Prints list two times
print list + tinylist # Prints concatenated lists
'''


#224

'''
import sys

try:
  # open file stream
  file = open(file_name, "w")
except IOError:
  print "There was an error writing to", file_name
  sys.exit()
print "Enter '", file_finish,
print "' When finished"
while file_text != file_finish:
  file_text = raw_input("Enter text: ")
  if file_text == file_finish:
    # close the file
    file.close
    break
  file.write(file_text)
  file.write("\n")
file.close()
file_name = raw_input("Enter filename: ")
if len(file_name) == 0:
  print "Next time please enter something"
  sys.exit()
try:
  file = open(file_name, "r")
except IOError:
  print "There was an error reading file"
  sys.exit()
file_text = file.read()
file.close()
print file_text
'''


#223
'''
from datetime import datetime

t=datetime.now()
print t

'''


#222
'''
import urllib2
f = urllib2.urlopen('https://graph.facebook.com/macks.r2r/picture')
print f.geturl()
'''


#221
'''
import sys, getopt

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'test.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   print 'Input file is "', inputfile
   print 'Output file is "', outputfile

if __name__ == "__main__":
   main(sys.argv[1:])

'''


#220
'''
import sys

print 'numero de argumentos: ', len(sys.argv), ' argumentos.'
print 'Lista de argumentos:', str(sys.argv)
'''

#219

#print(int('0x7dd', 16)) #imprime 2013
'''
Trabajando con archivos y directorios con Python¶
Listado de archivos en un directorio¶

Para buscar todos los archivos con una extensión, por ejemplo .jpg:

import glob
lista = glob.glob("*.jpg")

Para listar todos los archivos de un directorio:

import os
ficheros = os.listdir('/home/alumno/ejercicios/python') # linux
ficheros = os.listdir(r'c:Documents and SettingsalumnoEscritorioejerciciospython') #windows: cuidado con el caracter 

Directorio actual:

os.getcwd()
os.curdir

Tipos de ficheros¶

print michero, 'es un', 
if os.path.isfile(mifichero):
    print 'fichero'
if os.path.isdir(mifichero):
    print 'directorio'
if os.path.islink(mifichero):
    print 'enlace'

Último acceso a un fichero¶

ultimo_acceso = os.path.getatime('foto.jpg')
ultima_modificacion = os.path.getmtime('foto.jpg')
tiempo_en_dias = (time.time()- ultimo_acceso)/ (60*60*24)
print tiempo_en_dias

Eliminar ficheros y directorios¶

os.remove('mifoto.jpg')
for foto in glob.glob('*.jpg') + glob.glob('*.tif'):
    os.remove(foto)

Eliminar directorio:

import shutil
shutil.rmtree('midirectorio')

Copiar y renombrar ficheros¶

import shutil
shutil.copy(mifichero, copiafichero)

# copia también tiempo de último acceso y última modificación
shutil.copy2(mifichero, copiafichero)

# copia un árbol de directorios
shutil.copytree(raiz_de_directorio, copia_directorio)

Manipulando los paths y nombres¶

Rutas

>>> os.path.split('/home/alumno/python/ejercicios/ej1.py')
('/home/alumno/python/ejercicios', 'ej1.py')
>>> os.path.basename('/home/alumno/python/ejercicios/ej1.py')
'ej1.py'
>>> os.path.dirname('/home/alumno/python/ejercicios/ej1.py')
'/home/alumno/python/ejercicios'

Extensiones

>>> os.path.splitext('pelicula.avi')
('pelicula', '.avi')

Crear y moverse entre directorios¶

directorioOriginal = os.getcwd()
directorio = os.path.join(os.pardir, 'miNuevoDir')
if not os.path.isdir(directorio):
    os.mkdir(directorio)
os.chdir(directorio)
...
os.chdir(directorioOriginal) # vuelve al directorio inicial
os.chdir(os.environ['HOME']) # cambia al directorio home
'''


#218

'''
class Vidrio(object):

       def __init__(self):
              self.espesor=0
              self.textura=''
              self.pigmentacion=''

class Marco(object):

       def __init__(self):
              self.material=''
              self.color=''
              self.vidrio=Vidrio()

class Ventana(object):

       def __init__(self):
              self.marco=Marco()


def main():
       ventana=Ventana()
       print(ventana)
       


if __name__=="__main__":
       main()
'''

#217
'''
class Computadora(object):

       #constructor
       def __init__(self):
              self.tamanyo=""
              self.fabricante=''
              self.procesador=""
              self.sistemaOperativo=''
              self.ram=""
              self.discoduro=""
              self.tipo=""

       

def main():
       miPC=Computadora()
       miPC.tamanyo="pequeña"
       miPC.fabricante="Toshiba"
       miPC.procesador="AMD"
       miPC.sistemaOperativo="Windos 7"
       miPC.ram="2GB"
       miPC.discoduro="60GB"
       miPC.tipo="portatil"

       print "tamaño computadora: ",miPC.tamanyo
       print "fabricante: ",miPC.fabricante


if __name__=="__main__":
       main()
       
'''

#216

'''
archivo="prueba.txt"

def existe(arch):
       import os.path as ruta

       if ruta.isfile(arch):
              print "existe"

       else:
              print "no existe"


existe(archivo)

'''

#215

'''
archivo="prueba.txt"

def existe(arch):
       import os.path as ruta

       if ruta.exists(arch):
              print "existe"

       else:
              print "no existe"

existe(archivo)
'''


#214.
'''
import os as sistema
import os.path as ruta


valor= sistema.system("netstat -a")

print valor
'''

#213.
'''
def main():
       rango=range(0,11)#debe dar 55
       print "suma: ",sum(rango)

if __name__=="__main__":
       main()
'''

#212.
'''
lista=[]
print "Lista: ",lista
print "La lista es de tipo: ",type(lista)
print "El id de la lista es: ",id(lista)

for i in range(0,3):
       lista.append(i)

print "Lista: ",lista

lista[0]="Fernando"
lista[1]=30
lista[2]=["Ingeniero", "Programador","Diseñador"]
print "Lista: ",lista

cont=0
for i in lista:
       print i, " no.: ",cont
       cont+=1

'''

#211.
'''
class Persona:
       
       def verMsg(self):
              print "funcionando...en Python"

def ver(p):
      # p=Persona()
       p.verMsg()

def main():
       #persona=Persona()
       ver(Persona())
       
       
if __name__=='__main__':
       main()

'''

#210
'''
op1=2+8
op2=op1*4
op3=6+8
op4=op3/2
op5=op2*op4
print op5
'''

#209
'''
anyo="1981"
suma=0
for i in anyo:
       print i
       entero=int(i)
       suma+=entero

print "suma: %d" % (suma)

print [i for i in anyo if i !="9"]
'''

       


#208
'''
import turtle as tortuga

tortuga.setup(700,500)
raphael=tortuga.Screen()
raphael.bgcolor("lightblue")
raphael.title("Hola Leonardo desde codemomkey  28 de diciembre de 2012")

leonardo=tortuga.Turtle()
leonardo.color("red")
leonardo.pensize(3)
leonardo.forward(300)
leonardo.left(120)
leonardo.forward(300)
leonardo.exitonclick()

'''

#207
# http://www.openbookproject.net/thinkcs/archive/python/thinkcspyesp3e_abandonado/cap03.html
'''
import turtle as tortuga
tortuga.setup(700,500)
donatello=tortuga.Turtle()
donatello.forward(300)
donatello.left(91)
donatello.forward(200)
exit()
'''
#206.
'''
import math
MAX=10.0
x=2.0
cont=0
while x<MAX:
       print x, '\t',  math.log(x)/math.log(2.0)
       x=x+1.0
'''

#205.
#http://www.gulic.org/almacen/httlaclwp/
'''
import string
import re

print string.split("Mi gata come whiskas"," ")
print re.split("([^0-9])", "123+456*/")

cadena="una simple cadena"

print type(cadena)
print id(cadena)
'''


#204. pilas en Python

'''
class Pila:

       def __init__(self):
              self.items=[]

       def poner(self,item):
              self.items.append(item)

       def quitar(self):
              return self.items.pop()

       def esVacia(self):
              return (self.items==[])


def main():
       print "\t[Pilas en Python]"
       pila=Pila()
       pila.poner(89)
       pila.poner(33)
       pila.poner('+')

       #mostrar y eliminar los lementos de la pila
       while not pila.esVacia():
              print pila.quitar()


       
if __name__=='__main__':
       main()

'''

#203.
'''
global Local, Celular, Larga
def tipoServicio(t):
       if t==1:
              print "Llamada local"
       elif t==2:
              print "Llamada a celular"
       else:
              print "Llamada a larga distancia"

def menu():
       print "1. Local $2 por minuto"
       print "2. A celular $5 por minuto"
       print "3. Larga distancia $3 por minuto"
       print "4. Salir"
       
def main():
       Local=2
       Celular=5
       Larga=3
       tipo=0
       duracion=0
       costo=0

       while tipo<=0 or tipo>4:
              menu()
              tipo=int(raw_input('Elije: '))

              if tipo==4:
                     exit()
              else:
                     tipoServicio(tipo)

       while duracion<=0:
              duracion=int(raw_input('Duracion: '))

       if tipo==1:
              costo=duracion*Local
       elif tipo==2:
              costo=duracion*Celular
       elif tipo==3:
              costo=duracion*Larga
       else:
              print "no soportada"

       print "Costo: ",costo
       

if __name__=='__main__':
       main()

'''

#202. decoradores
'''
def avisar(f):
       def inner(*args, **kwargs):
              f(*args, **kwargs)
              print "Se ha ejecutado:  %s" % f.__name__
       return inner

@avisar
def abrir():
       print "abierto"

@avisar
def cerrar():
       print "cerrado"


#abrir=avisar(abrir)
#cerrar=avisar(cerrar)

abrir()
cerrar()
'''


#201. decoradores
'''
login=True

def admin(f):
       def comprobar(*args, **kwargs):
              if login:
                     f(*args, **kwargs)
              else:
                     print "no tiene permisos para ejecutar a funcion: %s"%f.__name__
       return comprobar


def decorador(f):
       def funcionDecorada(*args, **kwargs):
              print "funcion decorada: ",f.__name__
              f(*args, **kwargs)
       return funcionDecorada

@admin
@decorador
def suma(x,y):
       print  x+y

suma(3,55)
'''

#200. decoradores

'''
def d(a):
       
       def b(*args, **kwargs):
              a(*args, **kwargs)
              print "funcion ejecutada: %s"%a.__name__
       return b

def suma(x,y):
       print x+y

#invocar función
#suma(3,5)
#d(suma)(3,5)
suma(8,5)
decorada=d(suma)
decorada(8,9)
'''




#199.
'''
import random

def miJuego():
       aleatorio=random.randint(0,10) *10
       entero=int(raw_input('Introduce entero: '))
       print "... introduciste: %d"%(entero)
       if aleatorio==entero:
              print "¡acertaste!"
       else:
              print "fallaste, el numero aleatorio generado es: ",aleatorio
       
def main():
      miJuego()

if __name__=='__main__':
       main()
'''

#198.
'''
def leerDatos():
       try:
              dato=raw_input("Introduce algo y presiona Enter: ")
              imprimirDatos(dato)
       except:
              print "ha ocurrido una excepción"

def imprimirDatos(datos):
       try:
              print datos
       except:
              print "ha ocurrido una excepción"
         
def main():
       leerDatos()

if __name__ == '__main__':
        main()
'''

#197 
#cadena="hola en este dia muy fresco"
#print type(cadena)
#print id(cadena)


#196
#http://pp.com.mx/python/doc/python.html
'''
Lista = []
Numero = int(raw_input("Valor:"))
while Numero != 0 and Numero < 100:
       Lista.append(Numero)
       Numero = int(raw_input("\nValor:"))
       if Numero == 0:
              break
       if Numero == 0:
              print "\nTerminar"

 
# Verifico que la longitud de la lista sea mayor que 3.
  
Longitud = len(Lista)
if Longitud > 3:
       Filas = Longitud
       Columnas = Longitud
else:
       print "\nDatos insuficientes"

'''
#195
#Programa que acepte un año escrito en cifras arábigas y visualice el año en números romanos, dentro del rango 1000-1999
'''
autor: yo
fecha: 24 de diciembre de 2011
'''
'''
anyo,anyo_desglosado,aux=0,0,0
romano=""

while anyo<=0 and anyo<=1999:
    anyo=int(raw_input('Introduce año:'))
    print "Año en arábigo [",anyo,"]"
    print "\nAño desglosado: "

if (anyo>=1000):
    anyo_desglosado=anyo%1000
    romano=romano+"M"
    aux=1000
    print "arábigo:",aux
    
if (anyo_desglosado>=900):
    anyo_desglosado=anyo_desglosado%900
    romano=romano+"CM"
    aux=900
    print "arábigo:",aux

if (anyo_desglosado>=800):
    anyo_desglosado=anyo_desglosado%800
    romano=romano+"DCCC"      
    aux=800
    print "arábigo:",aux

if (anyo_desglosado>=700):
    anyo_desglosado=anyo_desglosado%700
    romano=romano+"DCC"          
    aux=700
    print "arábigo:",aux

if (anyo_desglosado>=600):
    anyo_desglosado=anyo_desglosado%600
    romano=romano+"DC"             
    aux=600
    print "arábigo:",aux

if (anyo_desglosado>=500):
    anyo_desglosado=anyo_desglosado%500
    romano=romano+"D"                
    aux=500
    print "arábigo:",aux


if (anyo_desglosado>=400):
    anyo_desglosado=anyo_desglosado%400
    romano=romano+"CD"                  
    aux=400
    print "arábigo:",aux

if (anyo_desglosado>=300):
    anyo_desglosado=anyo_desglosado%300
    romano=romano+"CCC"                           
    aux=300
    print "arábigo:",aux

if (anyo_desglosado>=200):
    anyo_desglosado=anyo_desglosado%200
    romano=romano+"CC"                                
    aux=200
    print "arábigo:",aux

if (anyo_desglosado>=100):
    anyo_desglosado=anyo_desglosado%100
    romano=romano+"C"                                  
    aux=100
    print "arábigo:",aux


if (anyo_desglosado>=90):
    anyo_desglosado=anyo_desglosado%90
    romano=romano+"XC"                                  
    aux=90
    print "arábigo:",aux

if (anyo_desglosado>=80):
    anyo_desglosado=anyo_desglosado%80
    romano=romano+"LXXX"                                           
    aux=80
    print "arábigo:",aux

if (anyo_desglosado>=70):
    anyo_desglosado=anyo_desglosado%70
    romano=romano+"LXX"                                               
    aux=70
    print "arábigo:",aux

if (anyo_desglosado>=60):
    anyo_desglosado=anyo_desglosado%60
    romano=romano+"LX"                                                     
    aux=60
    print "arábigo:",aux


if (anyo_desglosado>=50):
    anyo_desglosado=anyo_desglosado%50
    romano=romano+"L"                                                        
    aux=50
    print "arábigo:",aux

if (anyo_desglosado>=40):
    anyo_desglosado=anyo_desglosado%40
    romano=romano+"XL"                                                             
    aux=40
    print "arábigo:",aux

if (anyo_desglosado>=30):
    anyo_desglosado=anyo_desglosado%30
    romano=romano+"XXX"                                                                 
    aux=30
    print "arábigo:",aux

if (anyo_desglosado>=20):
    anyo_desglosado=anyo_desglosado%20
    romano=romano+"XX"                                                                 
    aux=20
    print "arábigo:",aux

if (anyo_desglosado>=10):
    anyo_desglosado=anyo_desglosado%10
    romano=romano+"X"                                                                        
    aux=10
    print "arábigo:",aux

if (anyo_desglosado==9):
    anyo_desglosado=anyo_desglosado%9
    romano=romano+"IX"                                                                            
    aux=9
    print "arábigo:",aux

if (anyo_desglosado==8):
    anyo_desglosado=anyo_desglosado%8
    romano=romano+"VIII"                                                                                 
    aux=8
    print "arábigo:",aux

if (anyo_desglosado==7):
    anyo_desglosado=anyo_desglosado%7
    romano=romano+"VII"                                                                                     
    aux=7
    print "arábigo:",aux

if (anyo_desglosado==6):
    anyo_desglosado=anyo_desglosado%6
    romano=romano+"VI"                                                                                         
    aux=6
    print "arábigo:",aux

if (anyo_desglosado==5):
    anyo_desglosado=anyo_desglosado%5
    romano=romano+"V"                                                                                             
    aux=5
    print "arábigo:",aux

if (anyo_desglosado==4):
    anyo_desglosado=anyo_desglosado%4
    romano=romano+"IV"                                                                                                 
    aux=4
    print "arábigo:",aux

if (anyo_desglosado==3):
    anyo_desglosado=anyo_desglosado%3
    romano=romano+"III"                                                                                                    
    aux=3
    print "arábigo:",aux

if (anyo_desglosado==2):
    anyo_desglosado=anyo_desglosado%2
    romano=romano+"II"                                                                                                         
    aux=2
    print "arábigo:",aux

if (anyo_desglosado==1):
    anyo_desglosado=anyo_desglosado%1
    romano=romano+"I"                                                                                                             
    aux=1
    print "arábigo:",aux


print "\nAño en romano: ",romano
'''

#194
'''
def inicio():
       print "\t[Calcular el IMC]"

def imc(p,t):
       return p/(t*t)

def clasificacion(result):
       cad=""
       if result<16:
              cad="infrapeso: delgadez severa"
       elif result<=16 or result<=16.99:
              cad="infrapeso: delgadez moderada"
       elif result<=17 or result<=18.49:
              cad="infrapeso: delgadez aceptable"
       elif result<=18.50 or result<=24.99:
              cad="peso normal"
       elif result<25 or result<=29.99:
              cad="obeso"
       elif result<=30 or result<=34.99:
              cad="obeso: tipo I"
       elif result<=35 or result<=40.0:
              cad="obeso: tipo II"
       elif result>=40:
              cad="obeso: tipo III"
       else:
              cad="no existe clasificacion"

       return cad

def main():
       peso, talla=0.0, 0.0
       inicio()

       while peso<=0:
              peso=float(raw_input('tu peso: '))

       while talla<=0:
              talla=float(raw_input('tu talla:'))

       print "peso: %.2f,  talla: %.2f "%(peso,talla)
       print "IMC obtenido: %f   %s"%(imc(peso,talla),clasificacion(imc(peso,talla)))

       
if __name__ == '__main__':
        main()
 '''

#193
'''
import os
print os.environ["HOME"]
'''


#192
'''
import logging
import sys
import os
import flickrapi

def get_photos_for_artist(artist=None):
       if not artist:
              logging.error('can not find photos for unknown artist')
              return None

        api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        flickr = flickrapi.FlickrAPI(api_key)
        gen = flickr.walk(tags=artist, content_type=1, per_page=10)
        return gen

def main():
    pass

if __name__ == '__main__':
        main()
'''

#191 info del sistema

#!/usr/bin/python
'''
import os
import time
 
numUsuario = os.getuid()
pidProceso = os.getpid()
donde = os.getcwd()
sistemaOperativo = os.uname()
tiempos = os.times()
horaRaw = time.time()
horaFormato = time.ctime(horaRaw)
 
print "Numero de usuario",numUsuario
print "PID",pidProceso
print "Directorio actual",donde
print "Informacion del sistema",sistemaOperativo
print "Informacion de tiempos del sistema",tiempos
 
print "\nLa hora/fecha actual es",horaRaw
print "Lo cual significa",horaFormato
'''



#190 vectores
'''
TAM=6
vector=[]
i=0

def analizar(v):
       positivos=0
       negativos=0
       ceros=0
       
       for i in v:
              if i<0:
                     negativos=negativos+1
              elif i>0:
                     positivos=positivos+1
              else:
                     ceros=ceros+1

       print "no. de positivos: ",positivos
       print "no. de negativos: ",negativos
       print "no. de ceros: ",ceros

for i in range(TAM):
       print "no.  %d"%(i)
       vector.append(int(raw_input('Valor: ')))

print "vector= ",vector
analizar(vector)
'''    


#189 arreglos
'''
vector=[]
TAM=7
positivos, negativos, ceros=0, 0, 0
for i in range(TAM):
    print i
    vector.append(int(raw_input('Valor: ')))

print "obtenemos   vector= ",vector
print ""

for j in vector:
    if j< 0:
        negativos=negativos+1
    elif j > 0:
        positivos=positivos+1
    else:
        ceros=ceros+1

print "positivos: ",positivos
print "negativos: ",negativos
print "ceros: ",ceros
'''

#188 matrices
'''
class Lista:
   lista = []
   suma = 0
   def llenarlista(self):
       x= int (raw_input("Ingrese Tamaño De La Lista:"))
       for i in range(x):
           #llenar lista
           self.lista.append(int(raw_input("Ingrese Numero:")))
       #imprimir lista
       for i in self.lista:
           print i
 
   def sumar(self):
       for i in self.lista:
           self.suma+= i
       print "La Suma De Los Datos Es:",self.suma
 
obj = Lista()
obj.llenarlista()
obj.sumar()
'''

#187 matrices
'''
FILAS=4
COLUMNAS=3
matriz=[]
for i in range(FILAS):
    for j in range(COLUMNAS):
        matriz.append(int(raw_input('Valor: ')))

print matriz
'''

#186 matrices
'''
from random import randint
 
n = int(raw_input("Ingrese FILAS: \n"))
m = int(input("Ingrese COLUMNAS: \n"))
matriz = []
 
for i in range(n):
    matriz.append([ randint(0, 100) for i in range(m)])
        
print matriz
'''

#185 matrices
'''
from random import randint
FILAS=int(raw_input('no. de filas: '))
COLUMNAS=int(raw_input('no. de columnas: '))
matriz=[]
for i in range(FILAS):
    for j in range(COLUMNAS):
        matriz.append(randint(0,100))

print matriz
'''
#184 matrices
'''
FILAS=4
COLUMNAS=3
matriz=[[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
for i in range(FILAS):
    for j in range(COLUMNAS):
        print matriz[i][j],"  -->",i,", ",j

'''

#183 matrices
'''
FILAS=4
COLUMNAS=3
matriz=[[0,0,0],[0,0,0],[0,0,0],[0,0,0]]

#llenar la matriz a mano
matriz[0][0]=3
matriz[0][1]=1
matriz[0][2]=2

matriz[1][0]=2
matriz[1][1]=10
matriz[1][2]=0

matriz[2][0]=5
matriz[2][1]=-10
matriz[2][2]=11

matriz[3][0]=8
matriz[3][1]=9
matriz[3][2]=100

#mostrar toda la matriz
print matriz
#el elemento con el indice 3
print matriz[3]
#el elemento con los indices 2,1
print matriz[2][1]

for i in range(FILAS):
    for j in range(COLUMNAS):
        print matriz[i][j]

'''


#182 matrices
'''
matriz=[]
matriz2=[]
matriz3=[]
resta=0
res=[]
res2=[]
res3=[]
suma=0
val=0
val1=0
n=[0,1,1,1,1]
val2=0
while True:
	print("Bienvenido:")
	menu=input("Si deseas ingresar: 1[MatrizxEscalar], 2[suma o resta de matriz], 3[Salir]: ")
	
	if menu==1:
		escalar=input("Introduce tu escalar: ")
		for i in range(5):
			a=input("Introduce la matriz: ")
			matriz3.append(a)
		for i in n:
			val2+=i
			suma=((matriz3[val2])*(escalar))
			res3.append(suma) 
		print(res3)
		
	if menu==2:
		for i in range(5):
			x=input("Introduce el primer numero:" )
			y=input("Introduce el primer numero de la segunda matriz:")
			matriz.append(x)
			matriz2.append(y)
		print(matriz)
		print(matriz2)
		
		while True:
			opcion= input("Introduce: [1]Suma, [2] resta, [3]Salir:  ")
			if opcion==1:
				for i in n:
					val+=i
					suma= matriz2[val]+matriz[val]
					res.append(suma)	
				print("la matriz resultante fue:"+str(res) )
			elif opcion==2:
				for i in n:
					val1+=i
					resta= matriz2[val]-matriz[val]
					res2.append(resta)	
				print("la matriz resultante fue:"+str(res2) )	
			elif opcion==3: 
				break	
	elif menu==3: break

'''

#181 matriz
'''
FILAS=4
COLUMNAS=3
matriz=[]
for i in range(FILAS):
    for j in range(COLUMNAS):
        matriz.append(i)

for i in range(FILAS):
    for j in range(COLUMNAS):
        print matriz
    
'''


#180 vectores
'''
FILAS=4
COLUMNAS=3
vector=[range(COLUMNAS) for i in range(FILAS)]
print vector
print "\n"
vector=[[None]*COLUMNAS for i in range(FILAS)]
print vector

'''



#179 vectores
'''
FILAS=4
COLUMNAS=3
vector=[None]*FILAS
for i in range(FILAS):
    vector[i]=[None]*COLUMNAS
    print vector[i]

'''

#178 vectores
'''
FILAS=4
COLUMNAS=4
vector=[]
for i in range(FILAS):
    vector.append([])
    for j in range(COLUMNAS):
        vector[i].append(None)
        print vector[i]

'''

#177.  M.C.M  y M.C.D.
'''
import sys
num1=0
num2=0
a=0
b=0
mcm=0
mcd=0
if len(sys.argv)>=2:
    print "nombre del programa: ",sys.argv[0]
    print "\nnumero 1: ",sys.argv[1],",numero 2:  ",sys.argv[2]
    num1=int(sys.argv[1])
    num2=int(sys.argv[2])
    a=num1
    b=num2
    while a!=b:
        if a>b:
            a=a-b
        else:
            b=b-a
    mcm=(num1*num2)/b
    mcd=b
    print "\nM.C.M. obtenido: ",mcm
    print "\nM.C.D. obtenido: ",mcd
else:
    print "no se introdujo ningún dato"

'''

#176.
#Esta clase representa cada nodo del grafo
'''
# http://www.gulic.org/almacen/httlaclwp/chap17.htm
# http://www.gulic.org/almacen/httlaclwp/
class nodo:
    def __init__(self, nombre):
        self.entrantes = []
        self.salientes = []
        self.nombre = nombre
    def addEntrante(self, nodo):
        self.entrantes.append(nodo)
        nodo.salientes.append(self)
    def addSaliente(self, nodo):
        self.salientes.append(nodo)
        nodo.entrantes.append(self)
    def addBidirec(self, nodo):
        self.salientes.append(nodo)
        self.entrantes.append(nodo)
        nodo.salientes.append(self)
        nodo.entrantes.append(self)

#Esta clase sirve para poder calcular el algoritmo de Disjtrka y se basa en la clase anterior
class DijksNodo(nodo):
    def __init__(self,name):
        nodo.__init__(self,name)
        self.data = [1000000,1000000]
    def addDijksInfo(self,puntos, procedencia):
        self.data = [puntos, procedencia]



#Se procede a crear los vertices 
a = DijksNodo("a")
b = DijksNodo("b")
c = DijksNodo("c")
d = DijksNodo("d")
e = DijksNodo("e")
f = DijksNodo("f")
g = DijksNodo("g")
h = DijksNodo("h")

#Se establecen las conexiones entre los vertices
a.addBidirec(b)
a.addBidirec(d)
b.addBidirec(c)
c.addBidirec(d)
c.addBidirec(h)
g.addBidirec(f)
g.addBidirec(h)
d.addBidirec(e)
e.addBidirec(f)

# Grafo construido 

a.addDijksInfo(0,a)
nodosSeleccionados = [a]
nodosInformados = 1
while nodosInformados != 8:
    # Primero se aniaden las puntuaciones a los nodos vecinos de los ya seleccionados
    nodosABuscar = []
    for nodo in nodosSeleccionados: 
        nodosABuscar.extend(nodo.salientes)
        nodosQueCalcular = nodo.salientes
        try:
            nodosQueCalcular.remove(nodosSeleccionados)
        except:
            pass
        for nodoVecino in nodosQueCalcular:
            puntuacion = nodo.data[0]+1
            if puntuacion < nodoVecino.data[0]:
                nodoVecino.addDijksInfo(nodo.data[0]+1, nodo)
    
    # Luego se busca cual va a ser el proximo nodo a seleccionar
    minimo = 1000000
    for nodoC in nodosABuscar:
        if nodoC.data[0] < minimo:
            nodoTarget = nodoC
    nodosSeleccionados.append(nodoTarget)
    nodosInformados += 1
 

nodoActual = g
numero = g.data[0]
while numero != 0:
  print " -> ",nodoActual.nombre, 
  numero = nodoActual.data[0]
  nodoActual = nodoActual.data[1]

'''

#175. primos
'''
from math import sqrt,floor
 
if __name__ == "__main__":
    n=int(raw_input('[+] Valor de n: '))
 
    numeros = [i for i in range(2,n+1)]  # {2...n}
 
    for i in numeros:
        if i > 0:
            for a in numeros[i-1:]:
                if a%i==0:
                    numeros[a-2]=0
 
    print "[+] Primos encontrados:"
    for i in numeros:
        if i > 0:
            print i
'''


#174 python gmail
#!/usr/bin/python
''' 
import sys
import re
import string
import httplib
import urllib2
import re
def StripTags(text):
    finished = 0
    while not finished:
        finished = 1
        start = text.find("<")
        if start >= 0:
            stop = text[start:].find(">")
            if stop >= 0:
                text = text[:start] + text[start+stop+1:]
                finished = 0
    return text
if len(sys.argv) != 2:
        print "\nExtracts emails from google results.\n"
        print "\nUsage : ./goog-mail.py <domain-name>\n"
        sys.exit(1)
 
domain_name=sys.argv[1]
d={}
page_counter = 0
try:
    while page_counter < 50 :
        results = 'http://groups.google.com/groups?q=' + str(domain_name)+'&hl=en&lr=&ie=UTF-8&start=' + repr(page_counter) + '&sa=N'
        request = urllib2.Request(results)
        request.add_header('User-Agent','Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)')
        opener = urllib2.build_opener()
        text = opener.open(request).read()
        emails = (re.findall('([\w\.\-]+@'+domain_name+')',StripTags(text)))
        for email in emails:
            d[email]=1
            uniq_emails=d.keys()
        page_counter = page_counter +10
except IOError:
    print "Can't connect to Google Groups!"+""
 
page_counter_web=0
try:
    print "\n\n+++++++++++++++++++++++++++++++++++++++++++++++++++++"+""
    print "+ Google Web & Group Results:"+""
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n"+""
 
    while page_counter_web < 50 :
        results_web = 'http://www.google.com/search?q=%40'+str(domain_name)+'&hl=en&lr=&ie=UTF-8&start='+ repr(page_counter_web) + '&sa=N'
        request_web = urllib2.Request(results_web)
        request_web.add_header('User-Agent','Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)')
        opener_web = urllib2.build_opener()
        text = opener_web.open(request_web).read()
        emails_web = (re.findall('([\w\.\-]+@'+domain_name+')',StripTags(text)))
        for email_web in emails_web:
            d[email_web]=1
            uniq_emails_web=d.keys()
        page_counter_web = page_counter_web +10
 
except IOError:
    print "Can't connect to Google Web!"+""
for uniq_emails_web in d.keys():
    print uniq_emails_web+""
'''

#########################################################

#http://www.java2s.com/Code/Python/CatalogPython.htm


#http://www.maestrosdelweb.com/editorial/guia-python-excepciones-helpers-refactoring/


#http://www.sromero.org/wiki/programacion/tutoriales/python/recorrer_arbol
#si se instala jython se debe AGREGAR el JAR  al classpath
'''
import sys
import os
from subprocess import call

def ensure_dir( d ):
	if not os.path.exists(d):
    	print ("creando directorio %s") % ( d )
        os.makedirs(d)

#------------------------------------

if(len(sys.argv) > 1):
    fichero = sys.argv[1]
    print "Abriendo " + fichero
    f = open( fichero, "r" )
    
    for line in f:
        datos = line.strip ()
    if ( len ( datos )> 3 ):
            print ("---%s--") % (datos)
        dir = ".\\" + datos
        print dir
        ensure_dir ( dir )

        cmd = "icacls " +  datos + " /remove \"Usuarios del dominio\""
        os.system( cmd )

        cmd = "icacls " +  datos + " /remove Everyone"
        os.system ( cmd )

        cmd = "icacls " +  datos + " /grant " + datos + ":F"
        os.system ( cmd )
    f.close()    
else:
    print "Debes indicar el nombre del archivo"


'''



'''
#!/usr/bin/python
import os, sys
from stat import *
 
def walktree(top, callback):
#   recursively descend the directory tree rooted at top,
  #   calling the callback function for each regular file
 
   for f in os.listdir(top):
       pathname = os.path.join(top, f)
       mode = os.stat(pathname)[ST_MODE]
       if S_ISDIR(mode):
           # It's a directory, recurse into it
           walktree(pathname, callback)
       elif S_ISREG(mode):
           # It's a file, call the callback function
           callback(pathname,f,top)
       else:
           # Unknown file type, print a message
           print 'Skipping %s' % pathname
 
def visitfile(fullname,file,path):
   print 'visiting', file, 'in', path, "=", fullname
 
if __name__ == '__main__':
   walktree(sys.argv[1], visitfile)

'''


'''
#!/usr/bin/python
 
import os
basedir= '/home/sromero/python'
 
#---------------------------------------------------
# Act over all files in the current directory
#---------------------------------------------------
def CheckFilesInDirectory(s1, directory, filelist):
   #print s2 # current dir
   for file in filelist:
      DoSomethingWithFile( directory, file )
 
#---------------------------------------------------
def DoSomethingWithFile( path, file ):
   fullpath = os.path.join(path, file)
   print fullpath
 
os.path.walk(basedir, CheckFilesInDirectory, 'somenull')

'''




'''
# De un directorio especifico:
 
[ name for name in os.listdir(thedir) if os.path.isdir(os.path.join(thedir, name)) ]
 
# Del directorio actual:
 
 directories=[d for d in os.listdir(os.path.curdir) if os.path.isdir(d)]
 
# o bien:
 
filter (os.path.isdir, os.listdir(os.getcwd()))`
 
# Funciones listas para usar:
 
def listdirs(folder):
   return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
 
def listdirs_fullnames(folder):
   return [
       d for d in (os.path.join(folder, d1) for d1 in os.listdir(folder))
       if os.path.isdir(d)
   ]
'''


'''
# Delete everything reachable from the directory named in 'top',
# assuming there are no symbolic links.
# CAUTION:  This is dangerous!  For example, if top == '/', it
# could delete all your disk files.
import os
for root, dirs, files in os.walk(top, topdown=False):
   for name in files:
       os.remove(os.path.join(root, name))
   for name in dirs:
       os.rmdir(os.path.join(root, name))

'''



'''
#(Posterior al os.walk):
 
for d in dirs[:]:
 if os.path.join(base, d) == EXCLUDED_DIR
  dirs.remove(d)
'''


'''
import os
from os.path import join, getsize
for root, dirs, files in os.walk('python/Lib/email'):
   print root, "consumes",
   print sum(getsize(join(root, name)) for name in files),
   print "bytes in", len(files), "non-directory files"
   if 'CVS' in dirs:
       dirs.remove('CVS')  # don't visit CVS directories

'''


'''
import os
for base, dirs, files in os.walk('/home/user'):
  print files
'''



'''
import os
for base, dirs, files in os.walk('/home/user'):
  print base

'''


'''
for root,dirs,files in os.walk(ruta_a_explorar):
    for file in [f for f in files if f.lower().endswith(extensiones_a_buscar)]:
        print(os.path.join(root, file))
'''



#http://code.google.com/p/asi-iesenlaces/wiki/ArchivosyDirectoriosConPython
'''
Directorio actual:

os.getcwd()
os.curdir
Tipos de ficheros
print michero, 'es un', 
if os.path.isfile(mifichero):
    print 'fichero'
if os.path.isdir(mifichero):
    print 'directorio'
if os.path.islink(mifichero):
    print 'enlace'
Ãšltimo acceso a un fichero
ultimo_acceso = os.path.getatime('foto.jpg')
ultima_modificacion = os.path.getmtime('foto.jpg')
tiempo_en_dias = (time.time()- ultimo_acceso)/ (60*60*24)
print tiempo_en_dias
Eliminar ficheros y directorios
os.remove('mifoto.jpg')
for foto in glob.glob('*.jpg') + glob.glob('*.tif'):
    os.remove(foto)
Eliminar directorio:

import shutil
shutil.rmtree('midirectorio')
Copiar y renombrar ficheros
import shutil
shutil.copy(mifichero, copiafichero)

# copia tambiÃ©n tiempo de Ãºltimo acceso y Ãºltima modificaciÃ³n
shutil.copy2(mifichero, copiafichero)

# copia un Ã¡rbol de directorios
shutil.copytree(raiz_de_directorio, copia_directorio)
Manipulando los paths y nombres
Rutas

>>> os.path.split('/home/alumno/python/ejercicios/ej1.py')
('/home/alumno/python/ejercicios', 'ej1.py')
>>> os.path.basename('/home/alumno/python/ejercicios/ej1.py')
'ej1.py'
>>> os.path.dirname('/home/alumno/python/ejercicios/ej1.py')
'/home/alumno/python/ejercicios'
Extensiones

>>> os.path.splitext('pelicula.avi')
('pelicula', '.avi')
Crear y moverse entre directorios
directorioOriginal = os.getcwd()
directorio = os.path.join(os.pardir, 'miNuevoDir')
if not os.path.isdir(directorio):
    os.mkdir(directorio)
os.chdir(directorio)
...
os.chdir(directorioOriginal) # vuelve al directorio inicial
os.chdir(os.environ['HOME']) # cambia al directorio home

'''


'''
import os
ficheros = os.listdir('/home/alumno/ejercicios/python') # linux
ficheros = os.listdir(r'c:\Documents and Settings\alumno\Escritorio\ejercicios\python') #windows: cuidado con el caracter \
'''



'''
import glob
lista = glob.glob("*.txt")
print lista
'''



'''
3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

yy = np.arange(24)
yy.shape = 6,4

mpl.rc('lines', linewidth=4)

fig = plt.figure()
mpl.rcParams['axes.color_cycle'] = ['r', 'g', 'b', 'c']
ax = fig.add_subplot(2,1,1)
ax.plot(yy)
ax.set_title('Changed default color cycle to rgbc')

ax = fig.add_subplot(2,1,2)
ax.set_color_cycle(['c', 'm', 'y', 'k'])
ax.plot(yy)
ax.set_title('This axes only, cycle is cmyk')

plt.show()

'''


'''
2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def update_line(num, data, line):
    line.set_data(data[...,:num])
    return line,

fig1 = plt.figure()

data = np.random.rand(2, 25)
l, = plt.plot([], [], 'r-')
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.xlabel('x')
plt.title('test')
line_ani = animation.FuncAnimation(fig1, update_line, 25, fargs=(data, l),
    interval=50, blit=True)
#line_ani.save('lines.mp4')

fig2 = plt.figure()

x = np.arange(-9, 10)
y = np.arange(-9, 10).reshape(-1, 1)
base = np.hypot(x, y)
ims = []
for add in np.arange(15):
    ims.append((plt.pcolor(x, y, base + add, norm=plt.Normalize(0, 30)),))

im_ani = animation.ArtistAnimation(fig2, ims, interval=50, repeat_delay=3000,
    blit=True)
#im_ani.save('im.mp4')

plt.show()
'''



#https://github.com/parente/pyttsx
#es necesario instalar win32com
#http://sourceforge.net/projects/pywin32/files/pywin32/
# de preferencia el *.exe
#http://packages.python.org/pyttsx/engine.html#examples
'''
1
import pyttsx
engine = pyttsx.init()
engine.say('mi gato come mucho.')
engine.say('es un gloton.')
engine.runAndWait()
'''




#código Jython
'''
from java.util import Random
from java.util import *

print Random
#codigo jython
r = Random()
r.nextInt()

for i in range(5):
	print r.nextDouble()
'''

'''
To do:
----------
1. List available animations using self.char.AnimationNames above
2. Get a RequestComplete event when the animation is done playing.
3. Change the voice to something else.

If you can do any of that, please send me a copy at
kamilche@mad.scientist.com. Thanks!

'''
'''
#http://pypi.python.org/pypi/comtypes
import comtypes
import comtypes.client
import time

class Genie:
CLSID_AgentServer = "{D45FD31B-5C6E-11D1-9EC1-00C04FD7081F}"
IID_IAgentEx = "{48D12BA0-5B77-11d1-9EC1-00C04FD7081F}"
CLSCTX_SERVER = 5
char = None
agent = None
animlist = ['Acknowledge', 'Alert', 'Announce',
'Blink', 'Confused', 'Congratulate',
'Congratulate_2', 'Decline', 'DoMagic1',
'DoMagic2', 'DontRecognize',
'Explain', 'GestureDown', 'GestureLeft',
'GestureRight', 'GestureUp',
'GetAttention', 'GetAttentionContinued',
'GetAttentionReturn',
'Greet', 'Hearing_1', 'Hearing_2',
'Hearing_3', 'Hearing_4',
'Idle1_1', 'Idle1_2', 'Idle1_3', 'Idle1_4',
'Idle1_5', 'Idle1_6',
'Idle2_1', 'Idle2_2', 'Idle2_3', 'Idle3_1',
'Idle3_2',
'LookDown', 'LookDownBlink',
'LookDownReturn', 'LookLeft',
'LookLeftBlink', 'LookLeftReturn',
'LookRight', 'LookRightBlink',
'LookRightReturn', 'LookUp', 'LookUpBlink',
'LookUpReturn',
'LookUpLeft', 'LookUpLeftBlink',
'LookUpLeftReturn',
'LookUpRight', 'LookUpRightBlink',
'LookUpRightReturn',
'MoveDown', 'MoveLeft', 'MoveRight',
'MoveUp', 'Pleased',
'Process', 'Processing', 'Read',
'ReadContinued', 'ReadReturn',
'Reading', 'RestPose', 'Sad', 'Search',
'Searching',
'StartListening', 'StopListening',
'Suggest',
'Surprised', 'Think', 'Thinking',
'Uncertain', 'Wave', 'Write',
'WriteContinued', 'WriteReturn', 'Writing',
'Hide', 'Show']
class Curry:
def __init__(self, fun, *args, **kwargs):
self.fun = fun
self.args = args[:]
self.kwargs = kwargs.copy()
def __call__(self, *args, **kwargs):
if kwargs and self.kwargs:
kw = self.kwargs.copy()
kw.update(kwargs)
else:
kw = kwargs or self.kwargs
return self.fun(*(self.args + args), **kw)

def __init__(self):
self.agent =
comtypes.client.CreateObject(self.CLSID_AgentServer,
self.CLSCTX_SERVER, self.IID_IAgentEx)
try:
self.agent.Connected = True
except comtypes.COMError, args:
if args[0] == -2147418094:
self.agent =
comtypes.client.CreateObject(self.CLSID_AgentServer,
self.CLSCTX_SERVER, self.IID_IAgentEx)
self.agent.Connected = True
else:
raise
self.agent.Characters.Load("mychar")
self.char = self.agent.Characters("mychar")
self.char.Show()

# How do I get the list of names from this?
print 'List of animations:'
anims = self.char.AnimationNames
print anims

def __getattr__(self, attrname):
if attrname in self.animlist:
return self.Curry(self.char.Play, attrname)
else:
return object.__getattr__(self, attrname)
def Move(self, x, y):
self.char.MoveTo(x, y)
def Play(self, anim):
try:
retval = self.char.Play(anim)
except:
print 'animation %s not found' % anim
return
def GestureAt(self, x, y):
self.char.GestureAt(x, y)
def Speak(self, text):
retval = self.char.Speak(text)
def Think(self, text):
self.char.Think(text)
def ChooseAgent(self):
self.agent.ShowDefaultCharacterProperties()
def GetAnimations(self):
return self.animlist
def Stop(self):
self.char.StopAll()

def main2():
genie = Genie()
genie.Move(400, 300)
genie.Greet()
genie.GestureAt(400, 600)
genie.Speak("You killed my father, prepare to die.")
time.sleep(5)
genie.Idle2_1()
genie.Think('Using Python to command me is cool!')
anims = genie.GetAnimations()
for i in range(len(anims)):
genie.Think('%d - %s' % (i, anims[i]))
genie.Play(anims[i])
time.sleep(5)
genie.Stop()

main2()

'''



'''


#################################################################


# Text To Speech using SAPI (Windows) and Python module pyTTS by Peter Parente
# download installer file pyTTS-3.0.win32-py2.4.exe  
# from:  http://sourceforge.net/projects/uncassist
# also needs: http://www.cs.unc.edu/Research/assist/packages/SAPI5SpeechInstaller.msi
# and pywin32-204.win32-py2.4.exe at this date the latest version of win32com
# from: http://sourceforge.net/projects/pywin32/
# tested with Python24 on a Windows XP computer   vagaseat   15jun2005
 
import pyTTS
import time
 
tts = pyTTS.Create()
 
# set the speech rate, higher value = faster
# just for fun try values of -10 to 10
tts.Rate = 1
print "Speech rate =", tts.Rate
 
# set the speech volume percentage (0-100%)
tts.Volume = 90
print "Speech volume =", tts.Volume
 
# get a list of all the available voices
print "List of voices =", tts.GetVoiceNames()
 
# explicitly set a voice
tts.SetVoiceByName('MSMary')
print "Voice is set ot MSMary"
 
print
 
# announce the date and time, does a good job
timeStr = "The date and time is " + time.asctime()
print timeStr
tts.Speak(timeStr)
 
print
 
str1 = """
A young executive was leaving the office at 6 pm when he found 
the CEO standing in front of a shredder with a piece of paper in hand. 
 
"Listen," said the CEO, "this is important, and my secretary has left. 
Can you make this thing work?"
 
"Certainly," said the young executive. He turned the machine on, 
inserted the paper, and pressed the start button.
 
"Excellent, excellent!" said the CEO as his paper disappeared inside 
the machine. "I just need one copy."
"""
print str1
tts.Speak(str1)
tts.Speak('Haah haa haah haa')
 
print
 
str2 = """
Finagle's fourth law:
  Once a job is fouled up, anything done to improve it only makes it worse.
"""
print str2
print
print "The spoken text above has been written to a wave file (.wav)"
tts.SpeakToWave('Finagle4.wav', str2)
 
print "The wave file is loaded back and spoken ..."
tts.SpeakFromWave('Finagle4.wav')
 
print
 
print "Substitute a hard to pronounce word like Ctrl key ..."
#create an instance of the pronunciation corrector
p = pyTTS.Pronounce()
# replace words that are hard to pronounce with something that 
# is spelled out or misspelled, but at least sounds like it
p.AddMisspelled('Ctrl', 'Control')
str3 = p.Correct('Please press the Ctrl key!')
tts.Speak(str3)
 
print
 
print "2 * 3 = 6"
tts.Speak('2 * 3 = 6')
 
print
 
tts.Speak("sounds goofy, let's replace * with times")
print "Substitute * with times"
# ' * ' needs the spaces
p.AddMisspelled(' * ', 'times')
str4 = p.Correct('2 * 3 = 6')
tts.Speak(str4)
 
print
 
print "Say that real fast a few times!"
str5 = "The sinking steamer sunk!"
tts.Rate = 3
for k in range(7):
    print str5
    tts.Speak(str5)
    time.sleep(0.3)
 
tts.Rate = 0
tts.Speak("Wow, not one mispronounced word!")

'''





#############################################################################
#http://www.loria.fr/~rougier/teaching/matplotlib/
#http://matplotlib.org/index.html
# Simple example of using general timer objects. This is used to update
# the time placed in the title of the figure.
'''
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def update_title(axes):
    axes.set_title(datetime.now())
    axes.figure.canvas.draw()

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

x = np.linspace(-3, 3)
ax.plot(x, x*x)

# Create a new timer object. Set the interval 500 milliseconds (1000 is default)
# and tell the timer what function should be called.
timer = fig.canvas.new_timer(interval=100)
timer.add_callback(update_title, ax)
timer.start()

#Or could start the timer on first figure draw
#def start_timer(evt):
#    timer.start()
#    fig.canvas.mpl_disconnect(drawid)
#drawid = fig.canvas.mpl_connect('draw_event', start_timer)

plt.show()
'''

'''
2
import sys
import os
import numpy as N
import wave

#http://codingmess.blogspot.mx/2008/07/how-to-make-simple-wav-file-with-python.html

class SoundFile:
   def  __init__(self, signal):
       self.file = wave.open('test.wav', 'wb')
       self.signal = signal
       self.sr = 44100

   def write(self):
       self.file.setparams((1, 2, self.sr, 44100*4, 'NONE', 'noncompressed'))
       self.file.writeframes(self.signal)
       self.file.close()

# let's prepare signal
duration = 4 # seconds
samplerate = 44100 # Hz
samples = duration*samplerate
frequency = 440 # Hz
period = samplerate / float(frequency) # in sample points
omega = N.pi * 2 / period

xaxis = N.arange(int(period),dtype = N.float) * omega
ydata = 16384 * N.sin(xaxis)

signal = N.resize(ydata, (samples,))

ssignal = ''
for i in range(len(signal)):
   ssignal += wave.struct.pack('h',signal[i]) # transform to binary

f = SoundFile(ssignal)
f.write()
print """########################################
#             Python                   #
########################################
"""
print '\narchivo creado'

'''









'''
import wave
import random
import struct
import datetime

SAMPLE_LEN = 44100 * 300 # 300 seconds of noise, 5 minutes

print "Create file using wave and writeframes twice in each iteration"

noise_output = wave.open('noise.wav', 'w')
noise_output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))

d1 = datetime.datetime.now()

for i in range(0, SAMPLE_LEN):
  value = random.randint(-32767, 32767)
  packed_value = struct.pack('h', value)
  noise_output.writeframes(packed_value)
  noise_output.writeframes(packed_value)

d2 = datetime.datetime.now()
print (d2 - d1), "(time for writing frames)"

noise_output.close()

d3 = datetime.datetime.now()
print (d3 - d2), "(time for closing the file)"

# --------------

print "Create a file directly writing to the file twice in each iteration"

noise_file = open('noise.raw', 'w')

d1 = datetime.datetime.now()

for i in range(0, SAMPLE_LEN):
  value = random.randint(-32767, 32767)
  packed_value = struct.pack('h', value)
  noise_file.write(packed_value)
  noise_file.write(packed_value)

d2 = datetime.datetime.now()
print (d2 - d1), "(time for writing frames)"

noise_file.close()

d3 = datetime.datetime.now()
print (d3 - d2), "(time for closing the file)"

# --------------

print "Create file using wave, storing frames in an array and using writeframes only once"

noise_output = wave.open('noise2.wav', 'w')
noise_output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))

d1 = datetime.datetime.now()
values = []

for i in range(0, SAMPLE_LEN):
  value = random.randint(-32767, 32767)
  packed_value = struct.pack('h', value)
  values.append(packed_value)
  values.append(packed_value)

value_str = ''.join(values)
noise_output.writeframes(value_str)

d2 = datetime.datetime.now()
print (d2 - d1), "(time for writing frames)"

noise_output.close()

d3 = datetime.datetime.now()
print (d3 - d2), "(time for closing the file)"

'''







'''

import numpy as N
import wave

class SoundFile:
   def  __init__(self, signal):
       self.file = wave.open('test.wav', 'wb')
       self.signal = signal
       self.sr = 44100

   def write(self):
       self.file.setparams((1, 2, self.sr, 44100*4, 'NONE', 'noncompressed'))
       self.file.writeframes(self.signal)
       self.file.close()

# let's prepare signal
duration = 4 # seconds
samplerate = 44100 # Hz
samples = duration*samplerate
frequency = 440 # Hz
period = samplerate / float(frequency) # in sample points
omega = N.pi * 2 / period

xaxis = N.arange(int(period),dtype = N.float) * omega
ydata = 16384 * N.sin(xaxis)

signal = N.resize(ydata, (samples,))

ssignal = ''
for i in range(len(signal)):
   ssignal += wave.struct.pack('h',signal[i]) # transform to binary

f = SoundFile(ssignal)
f.write()
print 'file written'

'''

'''
20
import doctest


def sumar_dos_numeros(a, b):
    """Suma dos numeros y retorna su resultado

    Argumentos:
    a -- primer sumando
    b -- segundo sumando

    Test:
    >>> sumar_dos_numeros(25, 10)
    35
    >>> sumar_dos_numeros(30, 20)
    50
    """
    resultado = a + b
    print a + b

if __name__ == "__main__":
    doctest.testmod()
    sumar_dos_numeros(5,6)
'''






'''
19
def probar_excepciones():
    dato = raw_input("Ingresar numero para pasar, letra para fallar: ")
    try:
        int(dato)
    except:
        print "ejecutando execpt, try ha fallado"
    else:
        print "ejecutando else, try se ha logrado"
    finally:
        print "finally se ejecuta siempre"

probar_excepciones()
'''



'''
18

x=9
y=0

try:
    result = x / y
except ZeroDivisionError:
    print "division por cero!"
else:
    print "resultado: ", result
finally:
    print "executing finally clause"

'''


'''
17
class Calculadora:
	def set_menu ( self ):
		print "Elige una opcion"
		print "SUMA\t \t1"
		print "RESTA\t\t 2"
		print "MULTIPLICACION\t\t 3"
		print "="*20
		self.opera = int(raw_input("OPCION: "))

	def set_operaciones ( self ):
		if self.opera ==1:
			print "HAS ELEGIDO SUMA"
			self.a=int(raw_input("Dame un numero: " ))
			self.b=int(raw_input("Dame otro numero: " ))
			self.c=self.a+self.b
			print "La suma es", self.c

		elif self.opera == 2 :
			print "HAS ELEGIDO RESTA"
			self.a=int(raw_input("Dame un numero: " ))
			self.b=int(raw_input("Dame otro numero: " ))
			self.c=self.a-self.b
			print "La resta es", self.c

		elif self.opera == 3 :
			print "HAS ELEGIDO MULTIPLICACION"
			self.a=int(raw_input("Dame un numero: " ))
			self.b=int(raw_input("Dame otro numero: " ))
			self.c=self.a*self.b
			print "La multiplicacion es", self.c
		else:
			print "ESA OPCION NO SE ENCUENTRA"

	def __init__ ( self ):
		self.set_menu()
		self.set_operaciones()


calc = Calculadora()
'''

########################################################################


'''
16
with open('archivo.txt') as archivo:
	for linea in archivo:
		print linea

'''

'''
15
arch=open('archivo.txt', 'w')
arch.write("Esto es\nuna prueba\nde lectura!")
arch.close()

'''


'''
14
arch=open('servicio.txt','r')
print arch.read()
print arch.readlines()
print arch.readline()
print arch.readline(4)
arch.close()

'''

'''
13
mi_diccionario = { 'nombre': 'fer', 'apellido': 'Carraro', 'pais':'Mexico' }

print mi_diccionario['pais']
print mi_diccionario.get('edad')

print ""

for (clave, valor) in mi_diccionario.items():
	print clave, ": ", valor


print ""

for clave in mi_diccionario:
	print clave, ": ", mi_diccionario[clave]

print ""

'''



'''
12
class Circular(list):
    
    def __init__(self, sequence):
        list.__init__(self, sequence)
        self.i = 0

    def _not_in_range(self, i):
        return i < 0 and i >= len(self)
            
    def set_index(self, i):
        if self._not_in_range(i):
	    raise IndexError, 'Can\'t set index out of range'
	else:
	    self.i = i

    def get_index(self):
        if self._not_in_range(self.i):
            self.i = len(self) - 1
        return self.i
            
    def next(self, n=1):
        if self == []:
	    return None
	if n < 0:
	    return self.prev(abs(n))    
	if self._not_in_range(self.i):
	    self.i = len(self) - 1
        if n >= len(self):
            n = n % len(self)
        try:
            self.set_index(self.i + n)
            return self[self.i]
        except IndexError:
            self.set_index(self.i + n - len(self))
            return self[self.i]
        
    def prev(self, n=1):
        if self == []:
            return None
	if n < 0:
	    return self.next(abs(n))
	if self._not_in_range(self.i):
	    self.i = len(self) - 1
        if n >= len(self):
            n = n % len(self)
        i = self.i - n
        if i >= 0:
            self.set_index(i)
        else:
            self.set_index(len(self) + i)
        return self[self.i]


if __name__ == '__main__':

    #Estas pruebas deberian organizarse con algun paquete de prueba de unidad
	
    seq = (1, 2, 3, 15, "www", 'u')            
    a = Circular(seq)

    for j in range(10):
	print a.next(), a.i

    for j in range(10):
	print a.prev(), a.i

    for j in range(10):
	print a.next(2), a.i

    for j in range(10):
	print a.prev(2), a.i

    for j in range(15):
	print a.next(7), a.i

    for j in range(15):
	print a.prev(7), a.i

    a += ['u']
    a.set_index(5)
    print a.get_index() == 5
    print a.pop() == 'u'
    print a.next() == 1
    print a.next(8) == 3
    print a.next(-2) == 1
    print a.next(-9) == 15
    b = Circular(a)
    a.set_index(4)
    b.set_index(4)
    print a.next(3) == b.prev(len(b) - 3)

'''

'''
11
import random
import threading
import time

class Filosofo(threading.Thread):
  def __init__(self, num, tenedor):
      threading.Thread.__init__(self)
      self.tenedor = tenedor
      self.num = num
      self.temp = self.num + 1 % 5

  def come(self):
      print "El filosofo "+str(self.num)+" come"

  def piensa(self):
      print "El filosofo "+str(self.num)+" piensa"

  def obtieneTenIzq(self):
      print "El filosofo "+str(self.num)+" obtiene tenedor izquierdo"
      print "obtiene el tenedor "+str(self.num)
      self.tenedor[self.num].acquire()

  def obtieneTenDer(self):
      print "El filosofo "+str(self.num)+" obtiene tenedor derecho"
      self.tenedor[self.temp].acquire()

  def liberaTenDer(self):
      print "El filosofo "+str(self.num)+" libera tenedor derecho"
      self.tenedor[self.temp].release()

  def liberaTenIzq(self):
      print "El filosofo "+str(self.num)+" libera tenedor izquierdo"
      self.tenedor[self.num].release()


  def run(self):
      while(True):
          self.piensa()
          self.obtieneTenIzq()
          self.obtieneTenDer()
          self.come()
          self.liberaTenDer()
          self.liberaTenIzq()

Nfilosofos = 5
                                                                                                                                            
tenedor = [1,1,1,1,1]

for i in range(0, 4):
  tenedor[i] = threading.BoundedSemaphore(1)

for i in range(0, 4):
  t = Filosofo(i, tenedor)
  t.start()
  time.sleep(0.5)

'''


'''
10
import threading

class hilo(threading.Thread):
    def __init__(self, num):
        threading.Thread.__init__(self)
        self.num = num

    def run(self):
        print "Soy el hilo", self.num

print "Soy el hilo principal"

for i in range(0, 10):
  t = hilo(i)
  t.start()
  t.join()
'''



'''
9
lista=['fer','uri','jon']
print lista[:2],"  -->",len(lista[:2])
lista.append('yez')
print lista
lista.remove('yez')
print lista
print lista.index('fer')
res= '<lgo'  in lista
print res

elemento=lista.pop()
print elemento 


print lista
print lista.count('fer')
lista.sort()
print lista
lista.reverse()
print lista
lista.insert(0,'carlos')
lista.extend(['juan','ana','luis'])
print lista




cad="fer,uriel,daniel"
'/'.split(cad)
print cad

litaCad=list(cad)
print litaCad

otra="mi gato come papas"
otra.join('/')
print '<->'.join(otra)


for i in range(len(lista)):
	print i


'''



'''
8

#!/usr/bin/python
#listas simples enlazadas con python
class Nodo: # en clase nodo definio el dato..y el apuntador al siguiente nodo "" sig""
    def __init__(self, dato):
        self.dato = dato
        self.sig = None
        
    def  __str__(self):#esta funcion me sirve para poder meter cualquier dato a la lista
        return str(self.dato)
        
class ListaEnlazada:#esta clase me ayuda a manejar la lista enlazada identificando la cabeza y el ultimo elemenyo
    def __init__(self): 
        self.cabeza =  None
        self.cola = None
        
    def agregarFinal(self, dato):  # funcion agregar al final
        nodo_nuevo = Nodo(dato)
        if self.cabeza == None: # aqui si no hay cabezera el elemento se vuelve la cabezera
            self.cabeza = nodo_nuevo
            
        if self.cola != None: # si si hay entonces se va a la cola.sig y esta apuntara a nodo nuevo
            self.cola.sig = nodo_nuevo
                    
        self.cola = nodo_nuevo

    def agregarInicio(self, dato):#aqui agregamos al inicio
        nodo_nuevo = Nodo(dato)
        if self.cabeza == None: # si no habia cabeza este se vuelve la cabeza
            self.cabeza = nodo_nuevo
        
        if self.cola != None: #cuando si habia mas datos entonces el nuevo elemento apuntara ala cabeza
            nodo_nuevo.sig = self.cabeza 
            self.cabeza =  nodo_nuevo # y la cabeza es el nuevo elemento(nodo nuevo)

    def eliminar(self, d):#para eliminar
        nodo = self.cabeza
        anterior = nodo#usamos anterior como auxiliar
        if self.cabeza.dato == d:  #si el dato a eliminar esta en la cabezera se elimina la cabeza y el cabeza.sig se vuelve la cabeza
            self.cabeza = self.cabeza.sig
        else:#si no se busca en el resto
            while nodo != None: 
                if nodo.dato == d:
                    anterior.sig = nodo.sig
                anterior = nodo
                nodo = nodo.sig

                       
    def imprimir(self):#aqui la funcion imprimir me ayuda a imprimir mientras haya elementos en la lista
        nodo = self.cabeza
        while nodo != None: 
            print nodo.dato
            nodo=nodo.sig#aqui se recorre






lista = ListaEnlazada()#creo un objeto nuevo que llamo lista
lista.agregarFinal(1)
lista.agregarFinal(2)
lista.agregarFinal(3)
lista.agregarInicio(7)
lista.agregarFinal(4)
lista.agregarFinal(5)
lista.agregarFinal(6)
lista.agregarInicio(10)
lista.eliminar(10)
lista.eliminar(7)
lista.imprimir()
'''



'''
7

import random

lista=[]
for x in range(1,50):
    valor=random.randint(1,300)
    lista.append(valor)
print lista
print '<br>'
del lista[0]
del lista[-1]
print lista
print '<br>'
suma=0
for x in range(1,len(lista)):
    suma=suma+lista[x]
lista.append(suma)
print lista
print '<br>'
lista.insert(1,125)
print lista
'''

'''
6

class Persona:

	def __init__(self,nombre,edad):
		self.nombre=nombre
		self.edad=edad


	def ver(self):
		print "Nombre %s"%self.nombre
		print "Edad %d"%self.edad


class Usuario(Persona):
	def __init__(self, nombre,edad):
		Persona.__init__(self,nombre,edad)
		

def main():
	obj=Usuario("fer",30)
	obj.ver()
	print type(obj)
	print type(Usuario)
	print type(Persona)


if __name__ == '__main__':
	main()

'''




'''
5

import smtplib
from email.mime.text import MIMEText
tx = open('servicio.txt', 'rb')
mensaje = MIMEText(tx.read())
tx.close()
mensaje['Subject'] = 'si ves esto es que funciono el codigo jajajajaja' #tema
mensaje['From'] = 'carraro.fernando@gmail.com'
#es es un mensaje
smtpserver = "smtp.gmail.com"
smtpuser = "carraro.fernando@gmail.com"#tu usr smtp, tu usuario gmail
smtppassword = "xb10dual"#tu pass smtp
SENDER = "carraro.fernando@gmail.com"
RECIPIENTS = "jhon.alex.pineda89@gmail.com" #email del destinatario
session = smtplib.SMTP(smtpserver, 587)
session.ehlo()
session.starttls()
session.ehlo()
session.login(smtpuser, smtppassword)
session.sendmail(SENDER, RECIPIENTS, mensaje.as_string())
session.quit()

'''



'''
4
from Tkinter import *

class App:
    def __init__(self, main):

        frame = Frame(main)
        frame.pack()

        self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

    def say_hi(self):
    	if self.hi_there["background"] == "green":  
    		self.hi_there["background"] = "yellow"

    	else:
    		self.hi_there["background"] = "green"

root = Tk()

app = App(root)

root.mainloop()

'''


'''
3
bA=True
bB=False

res="es verdadero" if bB == bA else "es falso"
print res
'''

'''
2
class Animal:

	def __init__(self,velocidad,velocidadMaxima):
		self.velocidad=velocidad
		self.velocidadMaxima=velocidadMaxima


	def avanzar(self):
		if self.velocidad==self.velocidadMaxima:
			print 'a lo maximo'

		else:
			self.velocidad+=10
			print 'vamos a %d por hora'% self.velocidad

	def detener(self):
		if self.velocidad==0:
			print 'se detuvo'

		else:
			self.velocidad-=10
			print 'vamos a %d por hora'% self.velocidad


class Aereo(Animal):
	def __init__(self,velocidad,velocidadMaxima):
		Animal.__init__(self,velocidad,velocidadMaxima)


class Terrestre(Animal):
	def __init__(self,velocidad,velocidadMaxima):
		Animal.__init__(self,velocidad,velocidadMaxima)


class Acuatico(Animal):
	def __init__(self,velocidad,velocidadMaxima):
		Animal.__init__(self,velocidad,velocidadMaxima)


class Gato(Aereo,Terrestre,Acuatico):
	pass


def main():
	g=Gato(10,60)
	for i in range(1,6):
		g.avanzar()

	print ""

	for j in range(1,6):
		g.detener()


if __name__ == '__main__':
	main()

'''

'''
1
#MRO
class Base1(object):  
    def amethod(self): print "Base1"  


class Base2(Base1):  
    pass

class Base3(object):  
    def amethod(self): print "Base3"

class Derived(Base2,Base3):  
    pass


def main():
	instance = Derived()  
	instance.amethod()  
	print Derived.__mro__

if __name__=='__main__':
	main()

'''


##############################################################




# usar enumeraciones:
# http://pypi.python.org/pypi/enum/
# Method Resolution Order

'''
14

class Base1(object):  
    def amethod(self): print "Base1"  

class Base2(Base1):  
    pass

class Base3(object):  
    def amethod(self): print "Base3"

class Derived(Base2,Base3):  
    pass

instance = Derived()  
instance.amethod()  
print Derived.__mro__

'''

'''
class Fecha:

    anyo="2012"
    mes="octubre"
    dia="16"
    hora="04:30 pm"
    minuto="30m"
    segundo="12s"

    def __init__(self,anyo,mes,dia,hora,minuto,segundo):
        self.anyo=anyo
        self.mes=mes
        self.dia=dia
        self.hora=hora
        self.minuto=minuto
        self.segundo=segundo


print dir(Fecha)
print Fecha.__dict__

'''



'''
13

from flufl.enum import Enum
class Colors(Enum):
    red = 1
    green = 2
    blue = 3

'''


'''
12
class Suite(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

s1 = Suite(['Heart', 'Club', 'Spade', 'Diamond'])
s1.Heart

'''



'''
11
alist = ['a1', 'a2', 'a3']

for i, a in enumerate(alist):
    print i, a

'''


'''
10
class TipoDocumento:
    XML="XML"
    DOC="DOC"
    DOCX="DOCX"
    PDF="PDF"
    
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

    def __init__(self,XML,DOC,DOCX,PDF):
        self.XML=XML
        self.DOC=DOC
        self.DOCX=DOCX
        self.PDF=PDF

    def asignarXML(self,XML):
        self.XML=XML

    def obtenerXML(self):
        return self.XML

    #más código

class Ofimatica:
    WORD="WORD"
    ADOBE="ADOBE"

    def __init__(self, WORD,ADOBE):
        self.WORD=WORD
        self.ADOBE=ADOBE

    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
        

def main():

    obj1=Ofimatica.ADOBE
    obj2=TipoDocumento.XML
    print "Software: ",obj1
    print "Tipo documento: ",obj2

    for i in enumerate(Ofimatica.ADOBE):
        print i
        

    
if __name__=='__main__':
    main()
    
'''



'''
9
import urllib
import urllib2
import requests # no se tiene esta lib
 
url = 'http://www.blog.pythonlibrary.org/wp-content/uploads/2012/06/wxDbViewer.zip'
 
print "downloading with urllib"
urllib.urlretrieve(url, "code.zip")
 
print "downloading with urllib2"
f = urllib2.urlopen(url)
data = f.read()
with open("code2.zip", "wb") as code:
    code.write(data)
 
print "downloading with requests"
r = requests.get(url)
with open("code3.zip", "wb") as code:
    code.write(r.content)
'''


'''
8
filename='prog01.py'
f = open(filename, 'r')
for line in f:
    print line
f.close()
'''


'''
7
class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
 
Numbers = Enum( "ONE TWO THREE".split() )
 
error = False
try:
    print Numbers.ONE
    print Numbers.TWO
    print Numbers.THREE
except:
    error = True
assert error == False
 
try:
    print Numbers.FOUR
except:
    error = True
assert error == True


'''

'''
6
class           Color : pass
class Red      (Color): pass
class Yellow   (Color): pass
class Blue     (Color): pass

class Toy: pass

myToy = Toy()

myToy.color = "blue"  # note we assign a string, not an enum

if myToy.color is Color:
    pass
else:
    print("My toy has no color!!!")    # produces:  My toy has no color!!!

myToy.color = Blue   # note we use an enum

print("myToy.color is", myToy.color.__name__)  # produces: myToy.color is Blue
print("myToy.color is", myToy.color)           # produces: myToy.color is <class '__main__.Blue'>

if myToy.color is Blue:
    myToy.color = Red

if myToy.color is Red:
    print("my toy is red")   # produces: my toy is red
else:
    print("I don't know what color my toy is.")

'''


'''
5
## {{{ http://code.activestate.com/recipes/67107/ (r1)
import types, string, pprint, exceptions

class EnumException(exceptions.Exception):
    pass

class Enumeration:
    def __init__(self, name, enumList):
        self.__doc__ = name
        lookup = { }
        reverseLookup = { }
        i = 0
        uniqueNames = [ ]
        uniqueValues = [ ]
        for x in enumList:
            if type(x) == types.TupleType:
                x, i = x
            if type(x) != types.StringType:
                raise EnumException, "enum name is not a string: " + x
            if type(i) != types.IntType:
                raise EnumException, "enum value is not an integer: " + i
            if x in uniqueNames:
                raise EnumException, "enum name is not unique: " + x
            if i in uniqueValues:
                raise EnumException, "enum value is not unique for " + x
            uniqueNames.append(x)
            uniqueValues.append(i)
            lookup[x] = i
            reverseLookup[i] = x
            i = i + 1
        self.lookup = lookup
        self.reverseLookup = reverseLookup
    def __getattr__(self, attr):
        if not self.lookup.has_key(attr):
            raise AttributeError
        return self.lookup[attr]
    def whatis(self, value):
        return self.reverseLookup[value]

Volkswagen = Enumeration("Volkswagen",
    ["JETTA",
     "RABBIT",
     "BEETLE",
     ("THING", 400),
     "PASSAT",
     "GOLF",
     ("CABRIO", 700),
     "EURO_VAN",
     "CLASSIC_BEETLE",
     "CLASSIC_VAN"
     ])

Insect = Enumeration("Insect",
    ["ANT",
     "APHID",
     "BEE",
     "BEETLE",
     "BUTTERFLY",
     "MOTH",
     "HOUSEFLY",
     "WASP",
     "CICADA",
     "GRASSHOPPER",
     "COCKROACH",
     "DRAGONFLY"
     ])

def demo(lines):
    previousLineEmpty = 0
    for x in string.split(lines, "\n"):
        if x:
            if x[0] != '#':
                print ">>>", x; exec x; print
                previousLineEmpty = 1
            else:
                print x
                previousLineEmpty = 0
        elif not previousLineEmpty:
            print x
            previousLineEmpty = 1

def whatkind(value, enum):
    return enum.__doc__ + "." + enum.whatis(value)

class ThingWithType:
    def __init__(self, type):
        self.type = type

demo("""
car = ThingWithType(Volkswagen.BEETLE)
print whatkind(car.type, Volkswagen)
bug = ThingWithType(Insect.BEETLE)
print whatkind(bug.type, Insect)

# Notice that car's and bug's attributes don't include any of the
# enum machinery, because that machinery is all CLASS attributes and
# not INSTANCE attributes. So you can generate thousands of cars and
# bugs with reckless abandon, never worrying that time or memory will
# be wasted on redundant copies of the enum stuff.

print car.__dict__
print bug.__dict__
pprint.pprint(Volkswagen.__dict__)
pprint.pprint(Insect.__dict__)
""")
## end of http://code.activestate.com/recipes/67107/ }}}


'''






'''
4
class enumSeason():
    Spring = 0
    Summer = 1
    Fall = 2
    Winter = 3
    def __init__(self, Type):
        self.value = Type
    def __str__(self):
        if self.value == enumSeason.Spring:
            return 'Spring'
        if self.value == enumSeason.Summer:
            return 'Summer'
        if self.value == enumSeason.Fall:
            return 'Fall'
        if self.value == enumSeason.Winter:
            return 'Winter'
    def __eq__(self,y):
       return self.value==y.value

s = enumSeason(enumSeason.Spring)
print s

'''

'''
3
class Enum(set):

	def __getattr__(self, name):
		
		if name in self:
			return name
        raise AttributeError



Animals = Enum(["DOG", "CAT", "HORSE"])
print Animals.DOG
'''


'''
2
def enum(**enums):
	return type('Enum',(),enums)

Numbers=enum(UNO=1,DOS=2,TRES=3)
print "valor: ",Numbers.TRES

'''


'''
1
class TipoDocumento:
	DOG=1
	CAT=2

def main():
	x=TipoDocumento.DOG
	print "valor: ",str(x)

if __name__ == "__main__":
    main()

'''



##############################################################
#173 timeit
'''
import timeit

def foo(x):
    return x+1

def main():
    t=timeit.Timer("foo(2)","main()")
    t.timeit()
    min(t.repeat(2,999))
    
if __name__=='__main__':
    main()
'''
#172 otro
'''
import sys

def main():
    valorObtenido=0
    cont=0
    if len(sys.argv)==0:
        print "error, faltan un parametro"

    else:
        print "completo: ",sys.argv
        print "en lista:"
        for i in sys.argv:
            print i
            valorObtenido= " es mayor a 7"  if (len(sys.argv)>=7) else " es menor a 7"
            cont+=1
        print "no. de elementos leidos: ",valorObtenido
        print "no. total de elementos en el arreglo: ",cont
            

#main
if __name__=='__main__':
    main()
'''

#171 otro
'''
import sys
if len(sys.argv)>=2:
    print sys.argv[1],"  tiene ",len(sys.argv[1]),"  caracteres"
else:
    print "sin argumentos"
'''
#170 otro
'''
cadena = "unemail@ficticio.dom";
if cadena.find("@") >= 0:
    print "Se ha encontrado la @ en el e-mail";
else:
    print "No se ha encontrado la @ en el e-mail";
'''

#169. otro
'''
t, vf, cont, aceleracion=12, 400, 0, 1.0
while cont <= 20:
    aceleracion=(vf-aceleracion)/t
    cont+=0.75
    print "resultado: ",aceleracion
    if (aceleracion==aceleracion):
        break
'''
#168. otro
'''
cont, suma, MAX=0, 0, 100
#sin función
while cont <= MAX:
    suma+=cont
    cont+=0.5
print "suma: %f"%(suma) #con formato
print "suma: ",suma #sin formato

#con función
def suma(maximo):
    cont, suma, MAX=0, 0, maximo
    while cont<=MAX:
        suma+=cont
        cont+=0.5

    return suma

print "suma: %f"%(suma(MAX))
print "suma: ",suma(MAX)
'''
    


#167. listas
'''
lista=[1,3,5,6,7,9,10,21,43,65,9]
lista_palabras=['pecera','oceano','manatial','rio','mar']
print len(lista)#longitud de la lista
print min(lista)#elemento menor de la lista
print max(lista)#elemento mayor de la lista
#print lista.index(0)
print lista.count(9)#número de veces que aparece el elemento dentro del paretesis
print lista[4] #nos devulve el elemento con el indice 4
print lista[-1]#nos devuelve el último elemento de  la lista

sec=' // '
print sec.join(lista_palabras)#unir una lsita y una cadena
print [1,2,3,4,5,6][0:6:2]
print (1, 2, 3, 4)[1:3]#Para obtener el segundo y tercer elemento de una tupla


print lista[:4]#sec[:4] devuelve los primeros 4 elementos (0, 1, 2, 3).
print lista[4:]#sec[4:] devuelve los elementos desde el 5º hasta el último.
#print [:]#sec[:] crea una secuencia con todos los elementos de la primera y es de hecho la forma usual de copiar una secuencia.
cadena="fernando"
cont=0
for i in cadena:
    print "letra: ",i,"  posicion no. :",cont
    cont+=1

'''


#166 ejemplo de clases en Python
'''
class ModeloDePresupuesto:
    # Datos comerciales 
    titulo = "PRESUPUESTO"
    encabezado_nombre = "Eugenia Bahit"
    encabezado_web = "www.eugeniabahit.com.ar"
    encabezado_email = "mail@mail.com"

    # Datos impositivos 
    alicuota_iva = 21

    # Propiedades relativas al formato 
    divline = "="*80

    # Setear los datos del cliente 
    def set_cliente(self): 
        self.empresa = raw_input('\tEmpresa: ')
        self.cliente = raw_input('\tNombre del cliente: ')

    # Setear los datos básicos del presupuesto 
    def set_datos_basicos(self): 
        self.fecha = raw_input('\tFecha: ')
        self.servicio = raw_input('\tDescripción del servicio: ')
        importe = raw_input('\tImporte bruto: $')
        self.importe = float(importe)
        self.vencimiento = raw_input('\tFecha de caducidad: ')

    # Calcular IVA 
    def calcular_iva(self): 
        self.monto_iva = self.importe*self.alicuota_iva/100

    # Calcula el monto total del presupuesto 
    def calcular_neto(self): 
        self.neto = self.importe+self.monto_iva

    # Armar el presupuesto 
    def armar_presupuesto(self): 
        """ 
            Esta función se encarga de armar todo el presupuesto 
        """
        txt = '\n'+self.divline+'\n'
        txt += '\t'+self.encabezado_nombre+'\n'
        txt += '\tWeb Site: '+self.encabezado_web+' | '
        txt += 'E-mail: '+self.encabezado_email+'\n'
        txt += self.divline+'\n'
        txt += '\t'+self.titulo+'\n'
        txt += self.divline+'\n\n'
        txt += '\tFecha: '+self.fecha+'\n'
        txt += '\tEmpresa: '+self.empresa+'\n'
        txt += '\tCliente: '+self.cliente+'\n'
        txt += self.divline+'\n\n'
        txt += '\tDetalle del servicio:\n'
        txt += '\t'+self.servicio+'\n\n'
        txt += '\tImporte: $%0.2f | IVA: $%0.2f\n' % (
                                  self.importe, self.monto_iva)
        txt += '-'*80
        txt += '\n\tMONTO TOTAL: $%0.2f\n' % (self.neto)
        txt += self.divline+'\n'
        print txt 
   
    # Método constructor 
    def __init__(self): 
        print self.divline
        print "\tGENERACIÓN DEL PRESUPUESTO"
        print self.divline
        self.set_cliente()
        self.set_datos_basicos()
        self.calcular_iva()
        self.calcular_neto()
        self.armar_presupuesto()

# Instanciar clase 
presupuesto = ModeloDePresupuesto()
'''
#165 twython
'''
from twython import Twython

usuario = "Mister_Negativo"
twitter = Twython()
followers = twitter.getFollowersIDs( screen_name = usuario )

for follower_id in followers :
    print "Usuario %d sigue a %s" % (follower_id,usuario)

tweets = twitter.getPublicTimeline()

for tweet in tweets :
    print tweet['user']['name'].encode('utf-8')
    print tweet['text'].encode('utf-8')

results = twitter.getDailyTrends()

for time, trend_list in results['trends'].iteritems() :
    print time
    for trend in trend_list :
        print trend['query']
'''

#164. twython
'''
from twython import Twython

def on_results(results):
    A callback to handle passed results. Wheeee.
    

    print results

Twython.stream({
    'username': 'your_username',
    'password': 'your_password',
    'track': 'python'
}, on_results)

'''


#163. twython
'''
from twython import Twython

t = Twython()
print t.search(q='python')

'''

#162. twython
'''
from twython import Twython

t = Twython()
print t.getProfileImageUrl('ryanmcgrath', size='bigger')
print t.getProfileImageUrl('mikehelmick')
'''

#161. twython

'''
from twython import Twython


oauth_token and oauth_token_secret are the final tokens produced
from the `Handling the callback` step


t = Twython(app_key=app_key,
            app_secret=app_secret,
            oauth_token=oauth_token,
            oauth_token_secret=oauth_token_secret)

# Returns an dict of the user home timeline
print t.getHomeTimeline()
'''

#160. twython
'''
from twython import Twython

oauth_token and oauth_token_secret come from the previous step
if needed, store those in a session variable or something


t = Twython(app_key=app_key,
            app_secret=app_secret,
            oauth_token=oauth_token,
            oauth_token_secret=oauth_token_secret)

auth_tokens = t.get_authorized_tokens()
print auth_tokens
'''

#159. twython 1er código
'''
from twython import Twython

t = Twython(app_key=app_key,
            app_secret=app_secret,
            callback_url='http://google.com.mx/')

auth_props = t.get_authentication_tokens()

oauth_token = auth_props['oauth_token']
oauth_token_secret = auth_props['oauth_token_secret']

print 'Connect to Twitter via: %s' % auth_props['auth_url']
'''


#158. listas
'''
lista_numeros=[25,32,55,67,81,90,102,120,145,208]
lista_palabras=['casa','sala','recamara','comedor','baño']
print [len(x)  for x in lista_palabras] #longitud de las palabras
print [x for x in lista_numeros if x<100] #ver solo números menores a 100
print lista_numeros[3],'  la lista es de tipo ',type(lista_numeros) #ver cambio y ver el tipo de la lista
print lista_palabras[2]

lista_numeros.append(201) #añadir elemento 201 al final
print lista_numeros
lista_numeros.pop() #eliminar el último elemento añadido
print lista_numeros
lista_numeros.extend([201,234]) #extender lista
print lista_numeros

lista_palabras.remove("comedor") #remover palabra comedor
print lista_palabras
lista_palabras.insert(0,"comedor") #añadir palabra comedor
print lista_palabras

#recorrer lista con for
for i in lista_numeros:
    print i

print ""
#recorrer lista con while
cont=0
while cont<len(lista_palabras):
    print lista_palabras[cont]
    cont=cont+1

print lista_palabras
lista_palabras.reverse() #lista de reversa
print lista_palabras
'''

#157. funciones
'''
def primos():
    n=2
    while True:
        for x in range(2,n):
            if n%x==0:
                break
            else:
                yield n
                n+=1

for p in primos():
    print (p)

'''

#156. comprehensiones
'''
lista=['Fernando','Ariel','Oscar','Javier','Enrique','Jaime']
otra_lista=[e +'!!' for e in lista]
print[x for x in otra_lista]
print [len(x) for x in otra_lista]
'''


#155. paso de argumentos
'''
import sys
from datetime import *
if len(sys.argv) >= 2:
    print "Hola usuario hoy es ",datetime.today()
    for i in range(1,len(sys.argv)):
            print i,"  --> ",sys.argv[i]
else:
        print "Este programa necesita un parámetro";
'''

'''
import sys
if len(sys.argv) >= 2:
        print "La cadena introducida tiene",len(sys.argv[1]),"caracteres";
else:
        print "Este programa necesita un parámetro";
'''
#154. menú
'''
import os
def menu():
    opcion = 0
    while opcion <1 or opcion >7:
        print "Bienvenid@"
        print
        print "1) Calculadora"
        print "2) Paint"
        print "3) Loquequieras"
        opcion = int(raw_input('Digita el numero de la opcion a escoger: '))
        return opcion
opcion = 0
while opcion !=16:
    opcion = menu()
    if opcion == 1:
        import os
        os.system("cls")
        print "1)Sumar"
        print "2)Restar"
        num = int(raw_input('Digita el numero de la opcion a escoger: '))
        if num == 1:
            a = input("Escribe el primer numero a sumar:  ")
            b = input('Escribe el segundo numero a sumar:  ')
            print 'El Resultado de la suma es :  ', a + b
            raw_input()
            os.system("cls")

'''
#153. otro
'''
g=9.81
def altura(t):
    if t==0:
        return 0
    else:
        return (g*t**2)/2

print altura(6.309)
'''

#152. binario
'''
print "Binario a Decimal y Decimal a Binario"
 
print "Menu"
 
print "a)Decimal a Binario"
print "b)Binario a Decimal"
 
opcion = raw_input("¿Que quieres hacer?")
 
if opcion == "a" :
    print "Introduce el numero decimal y se convertira en un numero binario"
    ndcimal = int(raw_input("Introduce el numero: "))
    print "El numero en Binario es: %s " % bin(ndcimal)

 
if opcion == "b" :
    print "Introduce el numero binario y se convertira en un numero decimal"
    print "***NOTA*** Sigue la sintaxis del codigo al reves : 0bxxxxxxx (x = 1 o 0)"
    nbinario = str(raw_input("Introduce el numero : "))
    print "El numero en Decimal es: %s " % int(nbinario,2)
'''
#151. ejemplo
'''
montos=[200,250,300,350,400,450,500,550]
tasas=[3.06,4.3,5.1]
periodos=[5,10,15,20]
for i in montos:
    print "monto:  [",i,"]"
    for j in tasas:
        print "tasa:  [",j,"]"
        for k in periodos:
            print "periodo:  [",k,"]"
            print "resultado:  ",i*pow(1+j/100,k)
'''

#150. PTG
'''
import turtle as t
import time

t.color("blue")
t.up()
t.goto(0,-55)
t.down()
t.circle(45)
t.up()
t.goto(0,0)
t.down()

#color("red")
for deg in range(0,61,7):
    t.right(90+deg)
    t.forward(100)
    t.right(90)
    t.forward(100)
    t.right(90)
    t.forward(100)
    t.right(90)
    t.forward(100)

t.up()
t.goto(-150,-120)
t.color("yellow")
t.write("hecho")
t.time.sleep(5)
''' 


#149. Python Turtle Graphics
'''
import turtle as tortuga

print "Usando la librería [",tortuga,"]"


tortuga.up()
tortuga.goto(0,36)
tortuga.down()
tortuga.color('blue')
tortuga.fill(2)
tortuga.circle(22)
tortuga.fill(1)
tortuga.up()
tortuga.goto(0,-24)
tortuga.down()
tortuga.color('green')
tortuga.fill(2)
tortuga.circle(22)
tortuga.fill(0)
tortuga.up()
tortuga.goto(0,-77)
tortuga.down()
tortuga.color('yellow')
tortuga.fill(2)
tortuga.circle(21)
tortuga.fill(0)
tortuga.up()
tortuga.goto(0,-77)
tortuga.down()
tortuga.color('red')
tortuga.fill(1)
tortuga.circle(22)
tortuga.fill(0)

raw_input('Presiona una tecla para terminar')

'''
#148. Firebird
'''
import kinterbasdb
con = kinterbasdb.connect(dsn='C:\Firebird\Firebird_2_1\examples\empbuild\EMPLOYEE.FDB', user='sysdba', password='mainkey')
# Create a Cursor object that operates in the context of Connection con:
cur = con.cursor()
print "\t[Firebird]"
# Execute the SELECT statement:
cur.execute("select * from country")
# Retrieve all rows as a sequence and print that sequence:
print cur.fetchall(),"\t"
'''

#147. porcentajes
'''
montos=[2500,3600,4500,5600,7500,8210,70454]
porcentaje=0.0
salir="n"
result=0.0

while salir=="n":

    print "\t[Montos]"
    for i in montos:
        print i

    porcentaje=float(raw_input("Introduce porcentaje a obtener: "))
    print "\t[Porcentaje obtenido]"

    for j in montos:
        result=(porcentaje*j)/100
        print result
    

    

    salir=raw_input("¿Desea salir?   Si-> s  No->n: ")

    if salir=="s":
        break

'''

#146.
'''
numeros=[5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,200,300,400,500,1000]
def obtenerMultipos50(valores):
    print "Multipos de 50"
    for n in valores:
        if(n%50==0):
            print n

    print "---------------------------------------------"

def obtenerMultiplos25(valores):
    print "Multiplos de 25"
    for n in valores:
        if(n%25==0):
            print n

    print "--------------------------------------------"

obtenerMultipos50(numeros)
obtenerMultiplos25(numeros)
'''



#145. operadores ternarios
'''
gato="gato"
perro="perro"
print gato if (3==0) else perro
'''

#144. Clases en Python
'''
class Futbol:
    def __init__(self,nombreEquipo,goleador,victorias,derrotas,empates,golesAFavor, golesEnContra, golesGoleador):
        self.nombreEquipo=nombreEquipo
        self.goleador=goleador
        self.victorias=victorias
        self.derrotas=derrotas
        self.empates=empates
        self.golesAFavor=golesAFavor
        self.golesEnContra=golesEnContra
        self.golesGoleador=golesGoleador

    def verDatos(self):
        print "Nombre del equipo: ",self.nombreEquipo
        print "Goleador: ",self.goleador
        print "Victorias: ",self.victorias
        print "Derrotas: ",self.derrotas
        print "Empates: ",self.empates
        print "Goles a favor: ",self.golesAFavor
        print "Goles en contra: ",self.golesEnContra
        print "Goles goleador: ",self.golesGoleador

def main():
    miJugador= Futbol("Real Madrid","Hugo Sánchez",12,0,0,35,6,32)
    miJugador.verDatos()
            

#main
if __name__=='__main__':
    main()

'''

#143.matrices
'''
numero_filas=4
numero_columnas=3
matriz = []
for i in range(numero_filas):
    matriz.append([])
    for j in range(numero_columnas):
        matriz[i].append(None)

print matriz
'''


#142. MySQLDb
'''
import sys
import MySQLdb as my

con=my.connect('localhost','root','root','agenda')

try:
    cursor=con.cursor()
    cursor.execute("insert into tblentcontact(nomb_contact,apellidop_contact,apellidom_contact,direcc_contact,tel_contact,email_contact) values ('Antonio','Huerta','Campos','El campo marte','7221212345','huerta@latinmail.com')")
    print "hecho"

except my.Error, e:
    print "Error:",e
    sys.exit(1)

finally:
    if con:
        con.close()

'''

#141. MySQLDb

'''
import MySQLdb as my
import sys

con=None
try:
    con=my.connect('localhost','root','root','agenda')
    cursor=con.cursor()
    #si todo sale bien debe aparecer la versión de MySQL
    cursor.execute("select version()")
    datos=cursor.fetchone()
    print "Version de MySQL: %s"%datos

except my.Error, e:
    print "Error %d: %s"%(e.argv[0],e.argv[1])
    sys.exit(1)

finally:
    if con:
        con.close()

'''



#140. POO en Python
'''
class Batman(object):
    def __init__(self):
        print "Batman el caballero de la noche"
        super(Batman,self).__init__()

class Robin(object):
    def __init__(self):
        print "Robin el compañero de Batman"
        super(Robin,self).__init__()

class RedHood(Batman,Robin):
    def __init__(self):
        print "Red Hood un antiguo Robin"
        Batman.__init__(self)
        Robin.__init__(self)

print "MRO: ",[x.__name__ for x in RedHood.__mro__]
RedHood()
'''
#139. POO en Python

'''
class Programador:

    def __init__(self,nombre,lenguajes,nivel):
        self.nombre=nombre
        self.lenguajes=lenguajes
        self.nivel=nivel

    def getNombre(self):
        return self.nombre

    def getLenguajes(self):
        return self.lenguajes

    def getNivel(self):
        return self.nivel

def main():
    fernando=Programador("Fernando",['Python','Java','Javascript','C++'],"Mid-Level")
    augusto=Programador("Augusto",['Pascal','Cobol','Visual Basic'],"Junior")
    print "Hola ",fernando.getNombre()
    print "Lenguajes que manejas: "
    for i in fernando.getLenguajes():
        print i
    print "Eres de nivel: ",fernando.getNivel()

    print "Hola ",augusto.getNombre()
    print "Lenguajes que manejas: "
    for j in augusto.getLenguajes():
        print j
    print "Eres de nivel: ",augusto.getNivel()
    

if __name__=='__main__':
    main()
'''

#138. Obtener el biotipo de una persona
'''
import sys as s
import os

#definir el tipo sumario en hombres: peso y estatura
tipoSumPesoHombres={"85.54":3.00,"83.79":2.75,
                       "82.04":2.50,"80.29":2.25,"78.54":2.00,"76.79":1.75,
                    "75.04":1.50,"73.29":1.25,"71.54":1.00,"69.79":0.75,
                    "68.04":0.50,"66.79":0.25,"64.54":0.00,"62.79":-0.25,
                    "61.04":-0.50,"59.29":-0.75,"57.54":-1.00,"55.79":-1.25,
                    "54..04":-1.50,"52.29":-1.75,"50.54":-2.00,"48.79":-2.25,
                    "47.04":-2.50,"45.29":-2.75,"43.54":-3.00}

tipoSumEstaturaHombres={"1.87":3.00,"1.86":2.75,"1.85":2.50,"1.83":2.25,
                        "1.82":2.00,"1.81":1.75,"1.79":1.50,"1.78":1.25,"1.77":1.00,
                        "1.75":0.75,"1.74":0.50,"1.73":0.25,"1.71":0.00,"1.70":-0.25,
                        "1.69":-0.50,"1.67":-0.25,"1.66":-1.00,"1.65":-1.25,"1.63":-1.50,
                        "1.62":-1.75,"1.61":-2.00,"1.59":-2.25,"1.58":-2.50,"1.57":-2.75,"1.55":-3.00}

#desviación=peso(Us)-estatura(Us)
#si peso= 45.29 kg  y estatura= 1.55 Mts entonces se toma su Unidad sigmática (Us)
#45 kg -->  (-2.75)    y   1.55 Mts --> (-3.00) tenemos entonces

# desviación=(-2.75) - (-3.00)= (+0.25)  --> es braquitipo
def desviacion(p,e):
    return p-e

#obtener el biotipo
def biotipo(d):
    if d < 0:
        print "es longitipo"

    elif d > 0:
        print "es braquitipo"

    else:
        print "es normotipo"

peso=45.29
estatura=1.55

desviacion(tipoSumPesoHombres[str(peso)],tipoSumEstaturaHombres[str(estatura)])
biotipo(desviacion)
'''


#137. MySQLDb

'''
import MySQLdb

#conectar a la base de datos
conexion=MySQLdb.connect(host='localhost',user='root',passwd='root',db='agenda')

#obtener cursor
cursor=conexion.cursor()
#sentencia sql
sql='select *from tblentcontact'
#ejecutar sentencia
cursor.execute(sql)
#asignar resultado a la variable res
res=cursor.fetchall()
print "[MySQLDb]"
#imprimir datos
for reg in res:
    #print reg[0],"-->",reg[1]
    print reg
#cerrar conexión
conexion.close()

'''

#136. otro
'''
import string
cubos=[x*2 for x in range(1,22)]
valores=['e','E','c','f','J','M','p','32']
print cubos
print filter(lambda x:x in string.uppercase,valores) #mayusculas
print filter(lambda x:x in string.lowercase,valores)#minusculas
'''


#135. otro
'''
for i in range(1,100):
    if i%3==2:
        print i,"  mod ",3," = 2"

'''

#134.  Python Turtle Graphics
'''
import turtle as t

t.up()
t.goto(0,36)
t.down()
t.color('blue')
t.fill(2)
t.circle(22)
t.fill(1)
t.up()
t.goto(0,-24)
t.down()
t.color('green')
t.fill(2)
t.circle(22)
t.fill(0)
t.up()
t.goto(0,-77)
t.down()
t.color('yellow')
t.fill(2)
t.circle(21)
t.fill(0)
t.up()
t.goto(0,-77)
t.down()
t.color('red')
t.fill(1)
t.circle(22)
t.fill(0)

raw_input('Presiona una tecla para terminar')
'''

#133. sumando
'''
import os
import sys

def main():

    if len(sys.argv)=="":
        print "Debes introducir 2 parametros"

    else:
        #el parametro sys.argv[0] indica el nombre del programa
        num1=float(sys.argv[1])
        num2=float(sys.argv[2])

        print "suma de %f y de %f es %f"%(num1,num2,num1+num2)

#main
main()

'''
#132. paso de parámetros
'''
import sys

if len(sys.argv)<=0:
    print "debes introducir un parametro"

else:
    print "programa [",sys.argv[0],"]"
    print "valor introducido",sys.argv[1],"es de tipo: ",type(sys.argv[1])


'''

#131. Uso de la clase Turtle (Tortuga)
'''
import turtle as t

#dibujando
t.forward(100)
t.right(90)
t.forward(50)
t.right(90)
t.forward(100)
t.right(90)
t.forward(50)

'''

#130. sms en Python,
# A continuación le mostramos un script realizado en python, para enviar SMS a móviles desde la plataforma de Descom SMS
'''
import sys
import getopt
import httplib
import urllib
import xml.dom.minidom
from xml.dom.minidom import parseString
####################
# Funciones
####################
def usage():
    print 'Uso del programa:'
    print '\tArgumentos Obligatorios:'
    print '\t\t -i\t--id\t\tCodigo de Cliente de la cuenta en Descom SMS'
    print '\t\t -u\t--username\tNombre de usuario de la cuenta en Descom SMS'
    print '\t\t -p\t--passwd\tPassword del usuario de la cuenta en Descom SMS'
    print '\tArgumentos Opcionales:'
    print '\t\t -s\t--sendsms\tLista de nuemeros de moviles a los que se le envia el mensaje, separado por ",". Si no se define este argumento, se obtiene el saldo de la cuenta.'
    print '\t\t -m\t--message\tTexto del mensaje a enviar.'
    print '\t\t -r\t--remitente\tRemitente personalizado del mensaje.'
def StrtoHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    return reduce(lambda x,y:x+y, lst)

#######################
# Variables globales
#######################
HOSTNAME = 'www.descomsms.com'
URL='/AP/descomMessage.servlet.Servlet'
VERBOSE=False
USERNAME=''
PASSWD=''
ID=''
REMITENTE=''
MOVILES=''
MENSAJE=''
MENSAJESXML=''
 
#######################
# Entrada de datos
#######################
try:
    opts, args = getopt.getopt(sys.argv[1:], "hu:p:i:vs:m:r:", ["help", "username=", "passwd=", "id=","verbose","sendsms=","message=","remitente="])
except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
for o, a in opts:
    if o == "-v":
        VERBOSE = True
    elif o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-u", "--username"):
         USERNAME = a
    elif o in ("-p", "--passwd"):
        PASSWD = a
    elif o in ("-i", "--id"):
        ID = a
    elif o in ("-s","--sendsms"):
        MOVILES = a
    elif o in ("-m","--message"):    
        MENSAJE = a
    elif o in ("-r","--remitente"):
        REMITENTE = a
    else:
        assert False, "unhandled option"
if USERNAME=='' or PASSWD=='' or ID=='':
    usage()
    sys.exit()
if MOVILES<>'' and MENSAJE=='':
    usage()
    sys.exit()
 
############################
# Crear Trama XML de envio
############################
N=0
if MOVILES<>'':
    for M in MOVILES.split(','):
        N=N+1
        MENSAJESXML+='<Mensaje><Id>'+str(N)+'</Id><Destino>'+M.strip()+'</Destino><Texto>'+StrtoHex(MENSAJE)+'</Texto></Mensaje>'
    if REMITENTE<>'':
        REMITENTE=StrtoHex(REMITENTE)
        REMITENTE='<Remitente>'+REMITENTE+'</Remitente>'

XML='<TXEnvio><Autentificacion><Usuario>'+StrtoHex(USERNAME)+'</Usuario><Passwd>'+StrtoHex(PASSWD)+'</Passwd><Idcli>'+ID+'</Idcli>'+REMITENTE+'</Autentificacion>'
if MENSAJESXML<>'':
    XML+='<Mensajes><Total>'+str(N)+'</Total>'+MENSAJESXML+'</Mensajes>'
XML+='</TXEnvio>'
##################
# Envio de SMS's
##################
params = urllib.urlencode({'xml': XML})
headers = {"Content-type": "application/x-www-form-urlencoded"}
conn = httplib.HTTPSConnection(HOSTNAME)
conn.request('POST', URL, params, headers)
response = conn.getresponse()
if response.status<>200:
    print 'Error: ',response.reason
    sys.exit(2)
RXML=response.read()
conn.close()
dom=parseString(RXML) 
nodos=dom.childNodes
 
#######################
# Analisis de respuesta
#######################
for n in dom.getElementsByTagName("Autentificacion"):
    Auth=n
    break
for n in Auth.getElementsByTagName("Resultado"):
    RAuth=n.firstChild.data
for n in Auth.getElementsByTagName("Comentario"):
    Comentario=n.firstChild.data
for n in Auth.getElementsByTagName("Saldo"):
    SALDO=n.firstChild.data
if RAuth<>"1":    
    print "Error: ", Comentario
    sys.exit(2)
if MOVILES=='':
    print "Saldo actual: ",SALDO,"creditos"
    sys.exit(0)
else:
    for n in dom.getElementsByTagName("Mensajes"):
        MSGS=n
        break
    TOTAL_ERRORES=int(MSGS.attributes["total_error"].value)
    TOTAL_MENSAJES=int(MSGS.attributes["total_mensajes"].value)
    TOTAL_OK=int(MSGS.attributes["total_ok"].value)
    if TOTAL_ERRORES==0:
        print 'Ok, '+str(TOTAL_OK)+' mensajes enviados'
    else:
        if TOTAL_OK==0:
            print 'Error, ningun mensajes ha sido enviado.'
        else:
            print 'Error, '+str(TOTAL_ERRORES)+' mensajes enviados con errores, '+str(TOTAL_OK)+' enviados correctamente:'
        MMOVILES=MOVILES.split(',')
        NN=0
        for M in MSGS.getElementsByTagName("Mensaje"):
            for n in M.getElementsByTagName("Resultado"):
                RMesg=n.firstChild.data
                break
            for n in M.getElementsByTagName("Comentario"):
                                CMesg=n.firstChild.data
                                break
            if RMesg=="0":
                print '\t['+MMOVILES[NN]+'] ERR ['+CMesg+']'
            NN=NN+1
    print "Saldo actual: ",SALDO,"creditos"
'''


#129. bisiesto
'''
def bisiesto(anyo):
    if anyo%400==0 and anyo%100==0:
        print anyo,"  es bisiesto"

    elif anyo%4==0:
        print anyo," es bisisesto"

    else:
        print anyo," no es bisisesto"

print "primer prueba"
bisiesto(1983)
print "segunda prueba"
bisiesto(2000)
print "tercera prueba"
bisiesto(1800)
'''


#128. listar MAC

'''
import sys
import os

def getMacAddress():
    mac_vector=[]
    if sys.platform == 'win32':
        for line in os.popen("ipconfig /all"):
            
            if line.lstrip().startswith('Physical Address'):
                mac = line.split(':')[1].strip().replace('-',':')
                mac_vector.append(mac)

            else:
                for line in os.popen("/sbin/ifconfig"):
                    if line.find('Ether') > -1:
                        mac = line.split()[4]
                        break

    return mac_vector

print "Obteniendo direccion Macc",getMacAddress()
'''


#127.
'''
v=500.0
n=12
i=3.0
f=0.0
cont=0
res=''

while cont<n:
    cont+=1
    f=v*pow(1+i/100,cont)
    res+='\n'+str(f)+'  periodo no. '+str(cont)
#print f
print res    
'''


#126. lista sin llenar, el mayor de 3 números
'''
lista=[] #lista vacia
suma=2
cont=0
maximo=3

#llenar lista
while cont<maximo:
    cont+=1
    suma+=cont
    lista.insert(cont,suma)
#ver tamaño de la lsia
print "longitud:",len(lista)

#si el tamaño (de la lista) es de 3 se ejecuta esta parte
if len(lista)==3:
    print "se cumple, la longitud de la lista es de: ",len(lista)
    for i in lista:
        mayor=lista[0]
        if lista[0]<lista[1]:
            mayor=lista[1]

        elif lista[0]<lista[2]:
            mayor=lista[2]

print "mayor: ",mayor
        
'''


#125. listas, el mayor de tres números

'''
lista=[8.0,7.0,9.0]
mayor=lista[0]
print "valor asignado como mayor: ",mayor
for i in lista:
    if lista[0]<lista[1]:
        mayor=lista[1]
        #print "mayor es: ",mayor
    elif lista[0]<lista[2]:
        mayor=lista[2]
        #print "mayor es: ",mayor

print "mayor es: ",mayor
'''

#124. listas
'''
a=["alma","fernando","yezmin","uriel","camila"]
b=[x for x in a if 'a' in x]
print b
print filter(lambda x: 'a' in x,a)
'''


#123.listas
'''
lista=[]
cont,suma,maximo=0,2,6

while cont<maximo:
    cont+=1
    suma+=cont
    lista.insert(cont,suma)

print lista

'''

#122. listas
'''
lista=[]

for i in range(5):
    print "no. ",i
    lista.insert(5,i)

print "lista llena:",lista

'''

#121. matrices y vectores
'''
#import os
#os.system("pause") para pausar (solo Windows)
vector=[[21,32,33],[7,6,6],[5,44,3],[9,44,21]]
print "original: ",vector,"  longitud: ",len(vector)

for i in vector:
    print i
    vector.remove(i)
    for j in vector:
        print j

print "modificado: ",vector

'''

#120. matrices y vectores
'''
vector=[]

for i in range(3):
    vector.insert(3,i)
    print i

print vector #salida: [0,1,2]  con vector.insert(3,i)
'''



#119. cálculo del M.C.D.
'''
a,b,resto,m,n,temp=0,0,0,0,0,0

while a<=0 or a==0:
    a=float(raw_input('valor de a:'))

while b<=0 or b==0:
    b=float(raw_input('valor de b:'))


print "El máximo común divisor de: ",a,"  y ",b,"  es:"

if a<b:
    temp=a
    a=b
    b=temp

m=a
n=b
resto=m%n

while resto!=0:
    m=n
    n=resto
    resto=m%n

print n
'''

#118. imc en Python
'''
def imc(x,y):
    return x/(y*y)

pesos=[45,48,51,54,57,60,63,66,69,72,75,78,81,84,87,90,93,96,99,102,105]
tallas=[1.51,1.53,1.56,1.59,1.62,1.65,1.68,1.71,1.74,1.77,1.81,1.83,1.86,1.89,1.92,1.95,1.98]
print "\t[Cálculo del IMC]\n"
for i in pesos:
    print "\t[---- peso: ",i,"-----]"
    for j in tallas:
        print "talla: ",j
        print "imc generado: ",imc(i,j)
        print "----------------------------------"
'''
#117. funciones matemáticas
'''
from math import *

valores=[12,34,43,65,65,32,88,0,32,1,87]
print "valores: ",[x for x in valores]
print 
print "seno"
print [sin(x) for x in valores],"\n"
print "coseno"
print [cos(x) for x in valores],"\n"
print "tangente"
print [tan(x) for x in valores],"\n"
'''

#116. no. pulsaciones
'''
def pulsacionesMujer(e):
    return (210-e)/10

datosMujer={"Alma":30,"Camila":1,"Adela":10,"Coco":55,"Carolina":24,"Yezmin":26}
for i in datosMujer:
    print i," tiene ",datosMujer[i]," de edad"
    print "le corresponden  ",pulsacionesMujer(datosMujer[i]),"  pulsaciones\n"

'''

#115. no. de pulsaciones

'''
edades=[5,10,15,20,25,30,35,40,45,50,55,60]

def pulsacionesHombre(e):
    return (220-e)/10

def pulsacionesMujer(e):
    return (210-e)/10

print "Con for"
for i in edades:
    print "\nedad (hombre): ",i,"  le corresponden: ",pulsacionesHombre(i)," pulsaciones"
    print "\nedad (mujer): ",i,"  le corresponden: ",pulsacionesMujer(i)," pulsaciones"

print "con comprehensiones"
print "Mujer:",[(210-x)/10 for x in edades]
print "Hombre:",[(220-x)/10 for x in edades]
'''


#114. lambda
'''
lista=[1,7,65,400,405,900,1024]
print lista
print "Devolver solo mayores a 100 --con lambda"
print filter(lambda x: x>100,lista)
print "Devolver menores a 100 --con lambda"
print filter(lambda x: x<100,lista)
print "Devolver solo mayores a 100 -- con comprehensiones"
print [x for x in lista if x>100]
print "Devolver solo menores a 100 --con comprehensiones"
print [x for x in lista if x<100]
'''
#113. usando loggers y decoradores
'''
import random as aleatorio

def logger(nombre):
    def wrapper(f):
        def f2(*args):
            print "-->Entrando a: ",nombre
            r=f(*args)
            print "<--Saliendo de: ",nombre
            return r
        return f2
    return wrapper

#el decorador
@logger('F1')
def f1():
    print "Haciendo algo"

@logger('F2')
def f2():
    print "Haciendo otras cosas"

@logger('Main')
def f3():
    print "Haciendo más cosas"
    for f in range(1,5):
        aleatorio.choice([f1,f2])()

#main
f3()
'''    

#112. otro ejemplo
'''
import random

def f1():
    print "Soy la función 1"

def f2():
    print "Soy la función 2"

def f3():
    print "Soy la función 3 (hago varias cosas)"
    for f in range(1,5):
        random.choice([f1,f2])()

#main
f3()
'''

#111. ejemplo de decoradores
'''
#creo la función que actuará como "decorador"
def memo(f):
    cache={}
    def memof(arg):
        if not arg in cache:
            cache[arg]=f(arg)
        return cache[arg]
    return memof

#el decorador
@memo
def factorial(n):
    print "calculando, n=",n
    if n>2:
        return n * factorial(n-1)
    else:
        return n

#main
valores=[4,4,5,3]
for i in valores:
    print factorial(i)
    
'''


#110. POO en Python
'''
class Punto(object):

    def __init__(self,x=0,y=0):
        self.x=x
        self.y=y

    #def set_x(self,x):
      #  self.x=x

    #def x(self):
      #  return self.x

    #def set_y(self,y):
      #  self.y=y

    #def y(self):
      #  return self.y
#main
punto=Punto('Punto','x y')
print "x:",punto.x
print "y:",punto.y
propiedad=property(punto.x,punto.y)
print propiedad
'''  

#109 .uso de time
'''
import time

def imprime(titulo):
    print titulo

imprime("Fecha de hoy")
print time.ctime(time.time())
'''

#108. MySQLdb y Tkinter

'''
from Tkinter import *
#panel principal
root=Tk()
#título
root.title("MySQL y Tkinter")

#función para ejecutar archivo
def activa():
    archivo="C:/Users/Uriel/Documents/Programas/Python/prog57.py"
    print "Ejecutando el archivo: [",archivo,"]"
    try:
        execfile(archivo)
    except IOError:
        print "excepcion ocurrida: "

#función para quitar ventana
def quitar():
    exit()
            
#etiqueta activar
btnActiva=Button(root,text='Activar',command=activa,width=20)
btnActiva.grid(row=0,column=1)

#botón quitar
btnQuitar=Button(root,text='Quitar',command=quitar,width=20)
btnQuitar.grid(row=0,column=2)


#inicia aplicación
root.mainloop()
'''
#107. Decimal a binario (Tkinter)
'''
from Tkinter import *

#función para calcular el número binario
def decimalABinario():
    #texto.get()
    numeroBinario=""
    resto=0
    numeroDecimal=int(texto.get())
    while (numeroDecimal>=2):
        resto=numeroDecimal%2
        numeroDecimal=(int)(numeroDecimal/2)
        numeroBinario+=(str)(resto)

    numeroBinario+=(str)(numeroDecimal)
    lista=list(numeroBinario)
    lista.reverse()
    print "\nNúmero decimal leido: ",texto.get(),"\nNúmero binario obtenido: ",lista
'''  

'''
def ver():
    print "tu colocaste: ",texto.get()
'''

'''
def quitar():
    exit()
    
#panel principal   
root=Tk()
root.title('Decimal a binario')

#etiqueta 
lblDecimal=Label(root,text="Número decimal: ")
lblDecimal.grid(row=0,column=0)

#para la caja de texto
texto=StringVar()

#caja de texto
txtMensaje=Entry(root,textvariable=texto)
txtMensaje.grid(row=0,column=1)

#botón calcular
btnCalcular=Button(root,text="Calcular",command=decimalABinario,width=20)
btnCalcular.grid(row=0,column=2)


#botón quitar
btnQuitar=Button(root,text="Quitar",command=quitar,width=20)
btnQuitar.grid(row=0,column=3)

#inicia aplicación
root.mainloop()
'''

#106. Tkinter
'''
from Tkinter import *
#puede ser también asi:
#import Tkinter

#función aviso
def aviso():
    print "Hola usuario"

#función quitar
def quitar():
    exit()

#función verificar
def verificar():
    if var.get():
        print "checkbutton seleccionado"
    else:
        print "checkbutton no seleccionado"

#función obtener
def obtener():
    cont=0
    print "El usuario introdujo: ",texto.get()
    for i in texto.get():
        cont+=1
        print i," -->",cont
    print "%s tiene %d caracteres"%(texto.get(),cont)
    
#panel principal 
root=Tk()

#para el checkbutton
var=IntVar()

#para el textbox
texto=StringVar()



#label
lblMsg=Label(root,text='Programando en Python')
lblMsg.grid(row=0,column=1)

#botón activa
btnActiva=Button(root,text='Activar',command=aviso,width=20)
btnActiva.grid(row=1,column=1)

#botón quita
btnQuita=Button(root,text='Quitar',command=quitar,width=20)
btnQuita.grid(row=3,column=1)

#checkbutton
check=Checkbutton(root,text="Seleccionado/no seleccionado",variable=var)
check.grid(row=4,column=1)

#botón verifica
btnVerifica=Button(root,text='Verifica',command=verificar,width=20)
btnVerifica.grid(row=5,column=1)

#textbox
txtMensaje=Entry(root,textvariable=texto)
txtMensaje.grid(row=6,column=1)

#botón obtener
btnObtener=Button(root,text='Obtener',command=obtener,width=20)
btnObtener.grid(row=7,column=1)


#título ventana
root.title('Ventana')
#inicia app
root.mainloop()

'''

#105. unzip
'''
import sys
import zipfile

if __name__ == '__main__':
    zf = zipfile.PyZipFile('zipfile_pyzipfile.zip', mode='w')
    try:
        zf.debug = 3
        print 'Adding python files'
        zf.writepy('.')
    finally:
        zf.close()
    for name in zf.namelist():
        print name

    print
    sys.path.insert(0, 'zipfile_pyzipfile.zip')
    import zipfile_pyzipfile
    print 'Imported from:', zipfile_pyzipfile.__file__
'''

#104. unzip
'''
from zipfile_infolist import print_info
import zipfile

print 'creating archive'
zf = zipfile.ZipFile('zipfile_append.zip', mode='w')
try:
    zf.write('README.txt')
finally:
    zf.close()

print
print_info('zipfile_append.zip')

print 'appending to the archive'
zf = zipfile.ZipFile('zipfile_append.zip', mode='a')
try:
    zf.write('README.txt', arcname='README2.txt')
finally:
    zf.close()

print
print_info('zipfile_append.zip')

'''

#103. unzip
'''
import time
import zipfile
from zipfile_infolist import print_info

msg = 'This data did not exist in a file before being added to the ZIP file'
zf = zipfile.ZipFile('zipfile_writestr_zipinfo.zip', 
                     mode='w',
                     )
try:
    info = zipfile.ZipInfo('from_string.txt', 
                           date_time=time.localtime(time.time()),
                           )
    info.compress_type=zipfile.ZIP_DEFLATED
    info.comment='Remarks go here'
    info.create_system=0
    zf.writestr(info, msg)
finally:
    zf.close()

print_info('zipfile_writestr_zipinfo.zip')
'''

#102. unzip
'''
from zipfile_infolist import print_info
import zipfile

msg = 'This data did not exist in a file before being added to the ZIP file'
zf = zipfile.ZipFile('zipfile_writestr.zip', 
                     mode='w',
                     compression=zipfile.ZIP_DEFLATED, 
                     )
try:
    zf.writestr('from_string.txt', msg)
finally:
    zf.close()

print_info('zipfile_writestr.zip')

zf = zipfile.ZipFile('zipfile_writestr.zip', 'r')
print zf.read('from_string.txt')
'''

#101. unzip
'''
from zipfile_infolist import print_info
import zipfile

zf = zipfile.ZipFile('zipfile_write_arcname.zip', mode='w')
try:
    zf.write('README.txt', arcname='NOT_README.txt')
finally:
    zf.close()
print_info('zipfile_write_arcname.zip')
'''


#100. unzip
'''
from zipfile_infolist import print_info
import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

modes = { zipfile.ZIP_DEFLATED: 'deflated',
          zipfile.ZIP_STORED:   'stored',
          }

print 'creating archive'
zf = zipfile.ZipFile('zipfile_write_compression.zip', mode='w')
try:
    print 'adding README.txt with compression mode', modes[compression]
    zf.write('README.txt', compress_type=compression)
finally:
    print 'closing'
    zf.close()

print
print_info('zipfile_write_compression.zip')
'''

#99. unzip
'''

from zipfile_infolist import print_info
import zipfile

print 'creating archive'
zf = zipfile.ZipFile('zipfile_write.zip', mode='w')
try:
    print 'adding README.txt'
    zf.write('README.txt')
finally:
    print 'closing'
    zf.close()

print
print_info('zipfile_write.zip')
'''

#98. unzip

'''
import zipfile

zf = zipfile.ZipFile('example.zip')
for filename in [ 'README.txt', 'notthere.txt' ]:
    try:
        data = zf.read(filename)
    except KeyError:
        print 'ERROR: Did not find %s in zip file' % filename
    else:
        print filename, ':'
        print repr(data)
    print
    
'''

#97. unzip
'''
import zipfile

zf = zipfile.ZipFile('example.zip')
for filename in [ 'README.txt', 'notthere.txt' ]:
    try:
        info = zf.getinfo(filename)
    except KeyError:
        print 'ERROR: Did not find %s in zip file' % filename
    else:
        print '%s is %d bytes' % (info.filename, info.file_size)
'''

#96. unzip
'''

import datetime
import zipfile

def print_info(archive_name):
    zf = zipfile.ZipFile(archive_name)
    for info in zf.infolist():
        print info.filename
        print '\tComment:\t', info.comment
        print '\tModified:\t', datetime.datetime(*info.date_time)
        print '\tSystem:\t\t', info.create_system, '(0 = Windows, 3 = Unix)'
        print '\tZIP version:\t', info.create_version
        print '\tCompressed:\t', info.compress_size, 'bytes'
        print '\tUncompressed:\t', info.file_size, 'bytes'
        print

if __name__ == '__main__':
    print_info('example.zip')

'''

#95. unzip
'''
import zipfile

zf = zipfile.ZipFile('example.zip', 'r')
print zf.namelist()

#94. unzip
import zipfile

for filename in [ 'README.txt', 'example.zip', 
                  'bad_example.zip', 'notthere.zip' ]:
    print '%20s  %s' % (filename, zipfile.is_zipfile(filename))

'''

#93. unzip
'''
import zipfile

zip = zipfile.ZipFile(r'c:\my.zip')
zip.extractall(r'c:\output')
'''

#92. otro
'''
import MySQLdb
db=MySQLdb.connect(host='hostname',user='user',passwd='pass',db='mysql')
cursor=db.cursor()
sql='SELECT host,user,password FROM user;'
cursor.execute(sql)
resultado=cursor.fetchall()
for registro in resultado:
    print registro[0] , '|' , registro[1]
    
'''

#91. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
import MySQLdb as mdb
import sys

try:
    conn = mdb.connect('localhost', 'testuser', 
        'test623', 'testdb');

    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM Writers WHERE Id = 5")  
    cursor.execute("DELETE FROM Writers WHERE Id = 4") 
    cursor.execute("DELETE FROM Writer WHERE Id = 3") 
    
    conn.commit()

except mdb.Error, e:
  
    conn.rollback()
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)

cursor.close()
conn.close()
'''

#90. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
import MySQLdb as mdb
import sys

try:
    conn = mdb.connect('localhost', 'testuser', 
        'test623', 'testdb');

    cursor = conn.cursor()
    
    cursor.execute("UPDATE Writers SET Name = %s WHERE Id = %s", 
        ("Leo Tolstoy", "1"))       
    cursor.execute("UPDATE Writers SET Name = %s WHERE Id = %s", 
        ("Boris Pasternak", "2"))
    cursor.execute("UPDATE Writer SET Name = %s WHERE Id = %s", 
        ("Leonid Leonov", "3"))   

    conn.commit()

    cursor.close()
    conn.close()

except mdb.Error, e:
  
    conn.rollback()
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
'''

#89. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
import MySQLdb as mdb 
import sys

try:
    conn = mdb.connect(host='localhost',user='testuser', 
        passwd='test623', db='testdb')

    cursor = conn.cursor()

    cursor.execute("SELECT Data FROM Images LIMIT 1")

    fout = open('image.png','wb')
    fout.write(cursor.fetchone()[0])
    fout.close()

    cursor.close()
    conn.close()

except IOError, e:

    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
'''    

#88. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

import MySQLdb as mdb
import sys

try:
    fin = open("chrome.png")
    img = fin.read()
    fin.close()

except IOError, e:

    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)

 
try:
    conn = mdb.connect(host='localhost',user='testuser',
       passwd='test623', db='testdb')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Images SET Data='%s'" % \
        mdb.escape_string(img))

    conn.commit()

    cursor.close()
    conn.close()

except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
'''

#87. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
import MySQLdb as mdb
import sys


con = mdb.connect('localhost', 'testuser', 
    'test623', 'testdb')
    
with con:    

    cur = con.cursor()
        
    cur.execute("UPDATE Writers SET Name = %s WHERE Id = %s", 
        ("Guy de Maupasant", "4"))        
    
    print "Number of rows updated: %d" % cur.rowcount

'''
#86. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
import MySQLdb as mdb
import sys


con = mdb.connect('localhost', 'testuser', 
    'test623', 'testdb')

with con:

    cur = con.cursor()
    cur.execute("SELECT * FROM Writers")

    rows = cur.fetchall()

    desc = cur.description

    print "%s %3s" % (desc[0][0], desc[1][0])

    for row in rows:    
        print "%2s %3s" % row

'''
#85. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
import MySQLdb as mdb
import sys

con = mdb.connect('localhost', 'testuser', 
    'test623', 'testdb')

with con:

    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute("SELECT * FROM Writers")

    rows = cur.fetchall()

    for row in rows:
        print "%s %s" % (row["Id"], row["Name"])
'''
#84. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
import MySQLdb as mdb
import sys


con = mdb.connect('localhost', 'testuser', 
    'test623', 'testdb');

with con:

    cur = con.cursor()
    cur.execute("SELECT * FROM Writers")

    numrows = int(cur.rowcount)

    for i in range(numrows):
        row = cur.fetchone()
        print row[0], row[1]
'''

#83. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
import MySQLdb as mdb
import sys


con = mdb.connect('localhost', 'testuser', 
        'test623', 'testdb');

with con: 

    cur = con.cursor()
    cur.execute("SELECT * FROM Writers")

    rows = cur.fetchall()

    for row in rows:
        print row
'''

#82. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
import MySQLdb as mdb
import sys

con = mdb.connect('localhost', 'testuser', 'test623', 'testdb');

with con:
    
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS \
        Writers(Id INT PRIMARY KEY AUTO_INCREMENT, Name VARCHAR(25))")
    cur.execute("INSERT INTO Writers(Name) VALUES('Jack London')")
    cur.execute("INSERT INTO Writers(Name) VALUES('Honore de Balzac')")
    cur.execute("INSERT INTO Writers(Name) VALUES('Lion Feuchtwanger')")
    cur.execute("INSERT INTO Writers(Name) VALUES('Emile Zola')")
    cur.execute("INSERT INTO Writers(Name) VALUES('Truman Capote')")
    
'''
#81. otro
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
import MySQLdb as mdb
import sys

con = None

try:

    con = mdb.connect('localhost', 'testuser', 
        'test623', 'testdb');

    cur = con.cursor()
    cur.execute("SELECT VERSION()")

    data = cur.fetchone()
    
    print "Database version : %s " % data
    
except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
        
    if con:    
        con.close()
'''

#80. MysQL y Python
'''
import MySQLdb
db=MySQLdb.connect(host='localhost',user='root',passwd='root',db='usuariospy')
cursor=db.cursor()
sql='SELECT id,nombre FROM usuarios;'
cursor.execute(sql)
resultado=cursor.fetchall()
for registro in resultado:
    print registro[0] , '|' , registro[1]

'''
#79 MySQLdb y Python
'''
import MySQLdb
db=MySQLdb.connect(host='localhost',user='root',passwd='root',db='agenda')
cursor=db.cursor()

sql='select * from tblentcontact'
cursor.execute(sql)
resultado=cursor.fetchall()
print 'Usuarios'
for registro in resultado:
    print registro[0],'->',registro[1]
    
cursor.close()
'''

#78. web service
'''
from SimpleXMLRPCServer import SimpleXMLRPCServer

def hola_mundo():   
    return ("hola mundo")

server = SimpleXMLRPCServer(("localhost", 8087))
print("Escuchando por el puerto 8887...")
server.register_function(busPlaca)
server.serve_forever()
'''

#77.  leer xml
'''
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
#all these imports are standard on most modern python implementations
 
#open the xml file for reading:
file = open('somexmlfile.xml','r')
#convert to string:
data = file.read()
#close file because we dont need it anymore:
file.close()
#parse the xml you got from the file
dom = parseString(data)
#retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
xmlTag = dom.getElementsByTagName('tagName')[0].toxml()
#strip off the tag (<tag>data</tag>  --->   data):
xmlData=xmlTag.replace('<tagName>','').replace('</tagName>','')
#print out the xml tag and data in this format: <tag>data</tag>
print xmlTag
#just print the data
print xmlData
'''

#76.leer xml
'''
#import library to do http requests:
import urllib2
 
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
#all these imports are standard on most modern python implementations
 
#download the file:
file = urllib2.urlopen('http://www.javamexico.org/somexmlfile.xml')
#convert to string:
data = file.read()
#close file because we dont need it anymore:
file.close()
#parse the xml you downloaded
dom = parseString(data)
#retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
xmlTag = dom.getElementsByTagName('tagName')[0].toxml()
#strip off the tag (<tag>data</tag>  --->   data):
xmlData=xmlTag.replace('<tagName>','').replace('</tagName>','')
#print out the xml tag and data in this format: <tag>data</tag>
print xmlTag
#just print the data
print xmlData
'''

#75. leer xml
'''
#Importamos el módulo
from xml.dom import minidom

#Creamos una función que busca un tag dado en un fichero XML
#y nos devuelve una lista con todos los contenidos que había
#dentro de los tags.

def buscaXMLTag(xmlFile,xmlTag):
    resultList = []
    try:
        dom = minidom.parse(xmlFile)
        elements = dom.getElementsByTagName(xmlTag)
        if len(elements) != 0:
            for i in range(0,len(elements)):
                resultList.extend([elements[i].childNodes[0].nodeValue])

            else:
                print 'xxx No hay elementos en el fichero XML con la etiqueta ' + xmlTag
    except:
        print 'xxx El fichero no existe o está mal formado.'
        print 'xxx Path del fichero: ' + xmlFile
        print 'xxx Etiqueta sobre la que se realizó la búsqueda: ' + xmlTag

    return resultList

#Ejecutamos la función y sacamos por pantalla todo el contenido encontrado
datos = buscaXMLTag('/home/jose/test.xml','titulo')
for elemento in datos:
    print elemento
'''

#74. CSV
'''
import csv
campo1 = "BBBBBB"
campo2 = 'AAA'
contador = 0
lineterminator='\n'
f = open('C:\\Users\\Uriel\\Documents\\Programas\\Python\\prueba_grabar.csv', 'a')
#obj = csv.writer(f, delimiter=';')
obj = csv.writer(f, delimiter=';', lineterminator='\n')
while contador < 10:
    contador = contador + 1
    obj.writerow([campo1,campo2, contador])
f.close()
print "fin..."
'''




#73. otro ejemplo de clases
'''
class Futbol:

    def __init__(self,nombreEquipo,victorias,derrotas,empates,golesAFavor,golesEnContra,golesGoleador,goleador):
        self.nombreEquipo=nombreEquipo
        self.victorias=victorias
        self.derrotas=derrotas
        self.empates=empates
        self.golesAFavor=golesAFavor
        self.golesEnContra=golesEnContra
        self.golesGoleador=golesGoleador
        self.goleador=goleador

    def verDatos(self):
        print "\nEquipo: %s  \nNo. victorias: %d  \nNo. derrotas: %d  \nNo. empates: %d  \nGoles a favor: %d  \nGoles en contra: %d  \nGoles goleador: %d  \nGoleador: %s " %(self.nombreEquipo,self.victorias,self.derrotas,self.empates,self.golesAFavor,self.golesEnContra,self.golesGoleador,self.goleador)

def main():
    futbol=Futbol("RedalycSoccer",3,0,0,15,7,6,"Jonhatan")
    futbol.verDatos()
    if (futbol is Futbol):
        print "futbol pertenece a la clase Futbol"
    else:
        print "futbol  NO pertenece a la clase Futbol, solo es una ", type(futbol)

    
if __name__ == '__main__':
    main()
'''


#72. otro
'''
class Animal:
    def __init__(self):
       print "Animal creado"
    def quiensoy(self):
       print "Animal"
    def comer(self):
       print "Estoy comiendo"
 
class Perro(Animal):
    def __init__(self):
       Animal.__init__(self)
       print "Perro Creado"
    def quiensoy(self):
       print "Perro"
    def ladrar(self):
       print "Woof Woof!"
def main():
     d = Perro()
     d.quiensoy()
     d.comer()
     d.ladrar()
 
if __name__ == '__main__':
    main()
'''

#71. otro
'''
import math
class Complejo:
      def __init__(self, real, imaginario):
          self.real = real
          self.img = imaginario
      def abs(self):
          print math.sqrt((self.real * self.real) + (self.img * self.img))
      def __add__(self, otro):
          print Complejo(self.real + otro.real, self.img + otro.img)
      def __sub__(self, otro):
          print Complejo(self.real + otro.real, self.img + otro.img)
          
      def mostrar(self):
          print self.real
          print self.img
 
def main():
      complejo1 = Complejo(3,4)
      complejo2 = Complejo(3,4)
      complejo3 = complejo1 + complejo2
      complejo4 = complejo1 - complejo2
      complejo3.mostrar()
      complejo4.mostrar()
 
if __name__ == '__main__':
     main()
'''

#71. otro
'''
import math
class Complejo:
      def __init__(self, real, imaginario):
          self.real = real
          self.img = imaginario
      def abs(self):
          print math.sqrt((self.real * self.real) + (self.img * self.img))
 
def main():
      numero = Complejo(3,4) 
      numero.abs()
 
if __name__ == '__main__':
     main()
'''

#70. y otro más
'''
import math
class Complejo:
      def __init__(self, real, imaginario):
          self.real = real
          self.img = imaginario
      def abs(self):
          print math.sqrt((self.real * self.real) + (self.img * self.img))

complejo=Complejo(56,99)
complejo.abs()
'''

#69. otro más de clases
'''
class Coche:
    """Abstraccion de los objetos coche."""
    def __init__(self, gasolina):
        self.gasolina = gasolina
        print "Tenemos", gasolina, "litros"

    def arrancar(self):
        if self.gasolina > 0:
            print "Arranca"
        else:
            print "No arranca..."

    def conducir(self):
        if self.gasolina > 0:
            self.gasolina -= 1
            print "Quedan", self.gasolina, "litros"
        else:
            print "No se mueve..."

miCoche=Coche(30)
miCoche.arrancar()
miCoche.conducir()
'''
#68. otro ejemplo de clases
'''
class Fecha:
    "Ejemplo de clase para representar fechas"
    dia = 14
    mes = "Noviembre"
    anho = 2006
    def dime_fecha(self):
        return "%i de %s de %i" % (Fecha.dia, Fecha.mes, Fecha.anho)

mi_fecha = Fecha()
print mi_fecha.dia, mi_fecha.mes, mi_fecha.anho
print mi_fecha.dime_fecha()
'''

#67. urllib
'''
import urllib2

try:
    f = urllib2.urlopen("http://www.python.org")
    print f.read()
    f.close()
except HTTPError, e:
    print "Ocurrió un error"
    print e.code
except URLError, e:
    print "Ocurrió un error"
    print e.reason

'''

#66. Ejemplo de clases en Python
'''
class Heroe:
    def __init__(self,nombre,pais,poderes):
        self.nombre=nombre
        self.pais=pais
        self.poderes=poderes

    def getNombre(self):
        return self.nombre

    def getPais(self):
        return self.pais

    def getPoderes(self):
        return self.poderes


#main
spiderman= Heroe("spiderman","USA",['sentido aracnido','fuerza de araña','super agilidad','trepar muros'])

#spiderman

print type(spiderman)
print "\nHeroe: ",spiderman.getNombre()
print "\nPais: ",spiderman.getPais()
print "\nPoderes: " ## puede ser print "\nPoderes: ",spiderman.getPoderes  pero lo muestra como lista

for i in spiderman.getPoderes():
    print i

'''

#65. otro ejemplo de exec
#uso de un archivo *.py externo
'''
archivo="C:/Users/Uriel/Documents/Programas/Python/prog1.py"
print "Ejecutando el archivo: [",archivo,"]"

try:
    execfile(archivo)
except IOError:
    print "excepcion ocurrida: "
'''
#64. eval("cadena")
#print eval("3+21")

#63. uso de archivos y execfile()
'''
temp=open("pruebaExecFile.py","w")
temp.write("print x+45")
temp.close()
x=32
execfile("pruebaExecFile.py")
'''

#62. diccionarios
'''
dicc={'Fernando':30,'Alma':26,'Camila':1,'Andrea':32,'Horacio':15}
edadTotal=0
for i in dicc:
    edadTotal+=dicc[i]
    print i,'  edad: ',dicc[i]

print "Total de edad: ",edadTotal

'''


#61.  while
'''
suma,dato=0, 0
dato=int(raw_input('Introduce numero:'))
while dato >=0:
    suma=suma+dato
    dato=int(raw_input('Introduce numero:'))
    if dato==0:
        break

print "suma: ",suma
'''


#60.  ejercicios de electrónica
'''
global vbe
vbe=0.7

def rth(r1,r2):
    return (r1*r2)/(r1+r2)

def eth(vcc,r1,r2):
    return (vcc*r2)/(r1+r2)

def ib(eth,rth,beta,re):
    return (eth-vbe)/(rth+(beta+1)*re)

def ic(beta,ib):
    return beta*ib

def vce(vcc,ic,rc,re):
    return vcc-ic*(rc+re)

def isat(vcc,rc,re):
    return vcc/(rc+re)

r1,r2,re,rc=0,0,0,0
beta,vcc,ib,ic=0,0,0,0
eth,rth=0,0

print "\t************************************"
print "\t*****  [Electrónica básica] ******"
print "\t************************************"

while r1<=0:
    r1=float(raw_input('Valor de r1:'))

while r2<=0:
    r2=float(raw_input('Valor de r2:'))

while rc<=0:
    rc=float(raw_input('Valor de rc:'))

while re<=0:
    re=float(raw_input('Valor de r3:'))

while vcc<=0:
    vcc=float(raw_input('Valor de vcc:'))

while  beta<=0:
    beta=float(raw_input('Valor de beta:'))
    

print "\n\tValores:"
print "r1: ",r1,"   r2:",r2
print "rc: ",rc,"   rc:",re
print "vcc:",vcc,"  beta:",beta
rth=rth(r1,r2)
eth=eth(vcc,r1,r2)

print"\nResultados"
print "Rth:  ",rth
print "Eth: ",eth
ib=ib(eth,rth,beta,re)
print "Ib:  ",ib
ic=ic(beta,ib)
print "Ic:  ",ic
print "Vce:  ",vce(vcc,ic,rc,re)
print "Isat:  ",isat(vcc,rc,re)

'''

#59. arreglos
'''
global g
g=9.8

def velocidadFinal(t):
    if t==0:
        return 0
    else:
        return g*t

    
vector=[0,0,0,0,0,0]
tam=len(vector)

#while tam<=0:
#    tam=int(raw_input('no. elementos:'))

print "arreglo de tamaño: ",tam

for i in range(tam):
    print i+1
    vector[i]=int(raw_input('valor:'))

for i in vector:
    print "tiempo: ",i,"   velocidad final: ",velocidadFinal(i)
    
    
'''
    


#58. fórmulas del movimiento

'''
#caída libre
global g
g=9.8
def velocidadFinal(t):
    if t==0:
        return 0
    else:
        return g*t

tiempo=[0,10,15,20,25,30,35,40,45,50]    
for i in tiempo:
    print "tiempo: ",i,"   velocidad final: ",velocidadFinal(i)
'''

'''
#tiro parabólico
from math import sin
global g
g=9.8

def alcance(vi,a):
    return vi ** 2 * sin(2*a) /g

valores=[200,250,300,350,400,450,500]
for i in valores:
    print "alcance de: ",i,"   es: ",alcance(i,45)
'''





#57. horoscopo chino
'''
animales={0:"mono",1:"gallo",2:"perro",3:"cerdo",4:"rata",5:"buey",6:"tigre",7:"conejo",8:"dragon",9:"serpiente",10:"caballo",11:"cabra"}
anyos=[1981,1990,1994,1998,2002,2006,2009,2012]
resto=0
print "\t[Horoscopo chino en Pyhton]"
for i in anyos:
    resto=i%12
    print "si naciste en: ",i,"  te correscpone el signo del: ",animales[resto]
'''

#56. otro
'''
valores=[5,7,42,12,0,2,72,9]
s=0
doble=lambda x:x*2
print "sumatoria con sum(): ",sum(x*2 for x in valores)
for i in valores:
    s+=doble(i)
print "suma con lambda: ",s
print ""
print "suma solo pares :",sum(x for x in valores if x%2==0)
print "suma solo impares :",sum(x for x in valores if x%2!=0)
print "maximo: ",max(x for x in valores)
print "minimo: ",min(x for x in valores)
    
'''

#55. timeit
'''
import timeit
t=timeit.Timer()
valores=[6,7,6,5,4]
try:
    print "tiempo transcurrido: ",t.timeit()," segundos"
    print "prueba 1: ",t.timeit(10000)
    print "prueba 2: ",t.timeit(sum(valores))
except:
    print t.print_exc()
    
'''

#54. vectores y tiempo
'''
import timeit
t=timeit.Timer()
numeros=[9,8,7,6,5,4]
s=0
for i in numeros:
    print "i: ",i
    for j in numeros:
        s+=i*j
        print "primer suma: ",s
    for k in numeros:
        print "k: ",k
        for l in numeros:
            s+=i-l
            print "segunda suma: ",s

print "suma final: ",s,"   -->tiempo: ",t.timeit()
'''


#53. otro
'''
class Nodo:
    def __init__(self,valor,sig=None):
        self.valor=valor
        self.sig=sig

#main
lista=Nodo("a",Nodo("b",Nodo("c",Nodo("d"))))
print lista.valor
print lista.sig.valor
print lista.sig.sig.valor
print lista.sig.sig.sig.valor
'''

#51. otros
'''
cont=4**2
numeros=[]
for i in range(cont):
    numeros.insert(0,i)
    print "se introduce el numero: ",i
print "vector original: ",numeros
#invertir orden
lista=list(reversed(numeros))
print "vector resultante: ",lista,"  con reversed(vector)"
'''

#50. random
'''
from random import *

aleatorio=(int) (random()*100)
#print aleatorio
print "No. aleatorio sin funcion"
num=[]
cont=3**2
for i in range(1,cont):
    print i,"  x ",aleatorio, "= ",i*aleatorio

aleatorios=lambda x: (int)(random()*x)

print ""
print "No. aleatorio con funcion"
print aleatorios(12)
'''


#49. otros
'''
cont=5**2
numeros=[]
for i in range(cont):
    numeros.append(i)
    print i

print numeros
lista=list(reversed(numeros))
print lista
'''

#48.  estadística básica en Python
'''
valores=[6.5,4.32,2.11,6.7,9.8,3.2,5.7,8.9,8.8,7.3,6.6]
print "longitud: ",len(valores)
print "Mostrar valores:"
for i in valores:
    print i
print ""
#ordenar valores
print "Valores ordenados:"
valores.sort()
for i in valores:
    print i

#algunas operaciones
print "Suma: ",sum(valores)
print "maximo: ",max(valores)
print "minimo: ",min(valores)
print  "Promedio: ",sum(valores)/len(valores)

#ocurrencia
print valores.count(6.6)
'''


#47. clases
'''
class Persona:
    def __init__(self,nombre,edad):
        self.nombre=nombre
        self.edad=edad
    def setNombre(self,nombre):
        self.nombre=nombre
    def setEdad(self,edad):
        self.edad=edad
    def getEdad(self):
        return self.edad
    def getNombre(self):
        return self.nombre

#main
persona= Persona("Fernando",30)
print persona.getNombre()
print persona.getEdad()
'''


#46. comparar
'''
def pertenece(e):
    if type(e) is list:
        print e,"  es una  lista"
    elif type(e) is file:
        print e," es un archivo"
    elif type(e) is tuple:
        print e," es una tupla"
    elif type(e) is float:
        print e," es de tipo real"
    elif type(e) is int:
        print e," es de tipo entero"
    elif type(e) is long:
        print e," es de tipo entero largo"
    elif type(e) is str:
        print e,"  es de tipo cadena"
    elif type(e) is types.NoneType:
        print e, "no pertenece a ningun tipo"
    else:
        print e,"  no pertenece a ningun tipo definido en la funcion"


lista=[1,"fernando",[2,3,4],0.9]
tupla=("camila",0,21.2,(5,4,3))

pertenece(lista)
pertenece(tupla)
pertenece(32)
pertenece(3.3)
pertenece(8l)
pertenece("Soy una cadena")
'''





#45. diccionarios
'''
dic={"usuario":"fernando","passw":5432,"direccion":"zaragoza"}
print dic
print dic.keys()
print dic.values()
'''

#44. otros
'''
valores=[3,5,43,21,0]
print cmp(5,3)
valores.sort()
print valores
valores.reverse()
print valores
print tuple(valores)
print list(valores)
'''

#43. listas
'''
print list('fernando')

for i in list('fernando'):
    print i

print "numero de ocurrencias de la palabra gato: ",['ser','gato','gato','perro'].count('gato')

'''



#42. longitud, maximo y minimo
'''
numeros=[34,566,0]
print "Numeros: "
for i in numeros:
    print i

print ""
print "longitud: ",len(numeros)
print "maximo: ",max(numeros)
print "minimo: ",min(numeros)
'''


#41  código PIN
'''
base=[['fernando','5432'],['alma','4321'],['famila','3215']]
usuario=raw_input("Usuario: ")
pin=raw_input("Pin: ")


if [usuario,pin] in base:
    print "acceso garantizado"
else:
    print "no existe usuario o pin"

'''
#40.  otros ejemplos

'''
largo=long(232222)
print largo, "tipo: ",type(largo)
etiqueta='<a href=http://www.elgato.org>Un lugar singular</a>'
print etiqueta
print etiqueta[32:-3]
numeros=[1,2,3,4,5,6,7,8,9,10]
print numeros[3:7]
url=raw_input('Introduce url:')
dominio=url[11:-4]
print "Nombre del dominio: "+dominio
cadena="hola"
print cadena*3
'''




#39. función sum()
'''
print "Uso de función sum()"
print sum(1.0 for i in range(1,12))
print sum(1.0 for i in range(10))
vector=[3,4,5,6,7,8]
print sum(2*i for i in vector)
'''

#38. diccionarios
'''
dic={"Hola": 1,"Mundo":2,"Python":3,"Programador":4}
# dic={"llave":valor}
print dic["Hola"]
print dic["Python"]
print "------------------------------"
for i in dic:
    print "Llave:  ",i, " --> valor:  ",dic[i]

print "tamaño del diccionario: ",len(dic)
print "----------------------------------"

for j in dic:
    if j=="Python":
        print "llave: ",j,"  --> valor:",dic[j]

'''


#37. listas
'''
lista=[1,2,3]
tupla=(2,32.0,"ernesto")
lista2=["Hola",7.43,3,lista,tupla]
for i in lista2:
    #print i,"  tipo: ",type(i)
    if type(i)==float:
        print "real: ",i
    if type(i)==int:
        print "entero: ",i
    if type(i)==str:
        print "cadena: ",i
    if type(i)==tuple:
        print "tupla: ",i
    if type(i)==list:
        print "lista: ",i
    
'''


#36. combinatorio y permutación
'''
def factorial(x):
    if (x==0):
        return 1
    else:
        return x * factorial(x-1)

def permutacion(n,r):
    menor=0
    mayor=0
    if(n<r):
        menor=n
        mayor=r
    else:
        menor=r
        mayor=n

    return factorial(mayor)/factorial(mayor-menor)


def combinatorio(n,r):
    menor=0
    mayor=0
    if(n<r):
        menor=n
        mayor=r
    else:
        menor=r
        mayor=n

    return (factorial(mayor)/(factorial(mayor) * factorial(mayor-menor)))


print permutacion(10,9)
print combinatorio(10,9)
'''

#35.  algunas operaciones con cadenas
'''
def iguales(c1,c2):
    if(c1==c2):
        print "son iguales"

    else:
        print "no son iguales"

#main
cad=""
cad2=[]
cad3="Hola programadores de Python"
cad4="En un verano muy singular"
numero=2211
print type(cad) 
print type(cad2)
print "numero a cadena: ",str(numero)
print "longitud: ",len(cad3)

for i in range(1,len(cad3)+1):
    print i

iguales(cad3,cad4)
'''



#34. pares e impares
'''
def pares(n):
    if (n%2==0):
        return n

def impares(n):
    if not(n%2==0):
        return n
    
numeros=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]

print "pares: ",[x for x in numeros if pares(x)]
print "impares: ",[x for x in numeros if impares(x)]
'''


#33. sumatoria 2+4+6+...+1000
'''
cont=0
suma=0
maximo=1000
print "sumatoria del 2+4+6+8+...+1000"
while (cont<maximo):
    cont=cont+2
    suma=suma+cont

print "suma total: ",suma

'''

#32. otro ejemplo de comprehensiones
'''
numeros=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
print [x for x in numeros if 200%x==0]
print [x for x in numeros if not(200%x==0)]
'''


#31. uso de file
'''
global salir

def menu():
    print "===================="
    print "             M   E   N  Ú               "
    print "1. Llenar vector"
    print "2. Ver datos"
    print "3. Ciclo for"
    print "===================="
    opcion=int(raw_input("Tu opcion: "))
    return opcion



#main
salir="n"
vector=[]
while salir == "n":
    opc=menu()

    if opc==1:
        #abrir archivo y escribir
        f2=open("archivo.txt","w")
        numeros=raw_input('Introduce elementos separados por comas:')
        f2.write(numeros)
        f2.close()

    if opc==2:
        #abrir  archivo y leer
        f=open("archivo.txt","r")
        completo=f.read(450)
        #print f
        print "Elementos del arreglo: "
        print completo
        f.close()

    if opc==3:
        f3=open("archivo.txt","r")
        completo2=f3.read(450)
        #print f
        print "Elementos del arreglo: "
        #print completo2
        vector=[completo2]
        print "vector: ",type(vector)
        for i in vector:
            print "vector: ",i
        f3.close()
        

    else:
        print ""

    salir=raw_input("¿Desea salir?  Si->s No->n: ")

    if (salir =="s"):
        break
    
'''

'''
f=open("archivo.txt","r")
completo=f.read(450)
print f
print completo
f.close()

f2=open("archivo.txt","w")
nombre=raw_input('Tu nombre:')
f2.write(nombre)
f2.close()

'''








#30. ejercicio con progresiones
'''
global a,L
suma=0 #suma del arreglo s=(n/2)*(a+L)
numeros=[3,6,9,12,15,18] ## el resultado debe ser 63
n=len(numeros) #tamaño del arreglo, número de elementos
a=numeros[0] #primer elemento del arreglo
print "primer elemento: ",a
for i in numeros:
    print i

L=i #último elemento del arreglo
print "ultimo elemento: ",L
suma=(n/2)*(a+L)
print "suma: ",suma

'''



#29. suma de matrices
'''
mat1=[[21,43,3],[6,5,4],[9,6,2]]
mat2=[[7,3,21],[6,7,10],[8,4,11]]
suma=[[0,0,0],[0,0,0],[0,0,0]]
print "tamaño de la matriz 1: ",len(mat1)
print "tamaño de la matriz 2: ",len(mat2)
tamanyo=len(mat1)
for i in range(tamanyo):
    for j in range(tamanyo):
        suma[i][j]=mat1[i][j] + mat2[i][j]
        print suma[i][j],"  posicion[",i,",",j,"]"
        #print mat1[i][j] + mat2[i][j]

#mostrar resultado
        
for i2 in range(tamanyo):
    for j2 in range(tamanyo):
        print suma[i2][j2],"  posicion[",i,",",j,"]"
        
'''



#28. matrices, en este ejemplo es de 3x3
'''
matriz=[[4,5,3],[0,7,21],[8,21,6]]
print "tamaño de la matriz: ",len(matriz)
#una forma, se imprimen los valores y los indices
print "ver valores e indices"
for i in range(len(matriz)):
    for j in range(len(matriz)):
        print matriz[i][j],"   posicion[ ",i,",",j,"]"

#multiplicar la matriz con valor
numero=2
print "multiplicación por el número: ",numero
for i2 in range(len(matriz)):
    for j2 in range(len(matriz)):
        print matriz[i2][j2]*numero,"  posicion[",i2,",",j2,"]"
'''


#27. vectores
'''
vector=[3,6,9,12,15,18]
print "tamaño del arreglo: ",len(vector)
#una forma, asi se muestran los valores 3,6,9,12,15,18
print "valores del arreglo"
for i in vector:
    print i  


#otra forma, asi se muestran los indices
print "indices del arreglo"
for j in range(len(vector)):
    print j

#otra más
print "valores del arreglo - 1"
for k in range(len(vector)-1):
    print vector[k]


#otra
print "valores del arreglo con  while
"'
cont=0
while cont<len(vector):
    print vector[cont]
    cont=cont+1

'''


#26. ficheros
'''
Archivos

Los ficheros en Python son objetos de tipo file creados mediante la función open (abrir).
Esta función toma como parámetros una cadena con la ruta al fichero a abrir, que puede ser relativa o absoluta; una cadena opcional indicando el modo de acceso (si no se especifica se accede en modo lectura) y, por último, un entero opcional para especificar un tamaño de buffer distinto del utilizado por defecto.


El modo de acceso puede ser cualquier combinación lógica de los siguientes modos:

‘r’: read, lectura. Abre el archivo en modo lectura.
El archivo tiene que existir previamente, en caso contrario se lanzará una excepción de tipo IOError.
‘w’: write, escritura. Abre el archivo en modo escritura.
Si el archivo no existe se crea. Si existe, sobreescribe el contenido.
‘a’: append, añadir. Abre el archivo en modo escritura.
Se diferencia del modo ‘w’ en que en este caso no se sobreescribe el contenido del archivo, sino que se comienza a escribir al final del archivo.
‘b’: binary, binario.
‘+’: permite lectura y escritura simultáneas.
‘U’: universal newline, saltos de línea universales.
Permite trabajar con archivos que tengan un formato para los saltos de línea que no coincide con el de la plataforma actual (en Windows se utiliza el caracter CR LF, en Unix LF y en Mac OS CR).

'''
#lectura: r
'''
f=open("archivo.txt","r")
completo=f.read(450)
print f
print completo
f.close()
'''
#escritura: w
'''
f=open("archivo.txt","w")
nombre=raw_input('Tu nombre:')
f.write(nombre)
f.close()

'''

# 1. Uso de map(funcion,secuencia[,secuencia,...])
'''
def cuadrado(n):
    return n ** 2

l=[1,2,3,4,5]
l2=map(cuadrado,l)
print 'Lista original: ',l
print ''
print 'Lista resultante: ',l2
'''
# 2. Uso de type()
'''
cadena="Hola usuario"
entero=9
caracter='b'
real=9.7
print type(cadena)
print type(entero)
print type(caracter)
print type(real)
'''

#3. Números complejos
'''
complejo=2.11+6.00j
complejo2=4.322+8.43j
print "1. ",complejo
print "2.",complejo2
suma=complejo+complejo2
print "suma: ",suma
'''

#4. uso de float(), int(), str()
'''
numero="1212"
cadena=23
real="2.1"
print "numero: ",int(numero)
print "cadena: ",str(cadena)
print "real: ",float(real)
'''

#5.  uso de or, not ,and
'''
a=9
b=32
print "a= %d   y b= %d"%(a,b)
expr1= (a>=b) and (b<a)
print " la expresion: (a>=b) and (b<a) es: ",expr1
expr2=(a<b) and (b>a)
print " la expresion: (a<b) and (b>a)  es: ",expr2
expr3= (a<=b) or (b>a)
print " la expresion: (a>=b) or (b<a) es: ",expr3
expr4=(a<b) or (b>a)
print " la expresion: (a<b) or (b>a)  es: ",expr4
expr5=not (a>b)
print " la expresion: not (a >b) es: ",expr5
expr6=not (a<b)
print " la expresion: not (a <b) es: ",expr6
'''

#6. uso de listas--> vectores o matrices
'''
l=[2,3,4]
l2=["a","e","i"]
lista=[3,"Fernando",0.322,True,l,l2]
print lista
print "es de tipo: ",type(lista)
'''

#7. uso de tuplas, se parecen a las listas
'''
t=(1,3,5)
t2=("uriel","aes","Python")
tupla=(1,"Ariel",34.32,False,t,t2)
print tupla
print "es de tipo: ",type(tupla)
'''

#8. uso del operador []
'''
numero="123"
t=(1,2,3,4,5,6)
numero2=t[2]
cadena="En este verano caluroso"
print numero[1] #debe mostrar 2
print numero2 #debe mostrar 3
print cadena[4]
print cadena[4:]
print cadena[::2]
'''

#9. matrices asociativas:  diccionarios  --> dic={"Clave": valor}
'''
dic={"Creador de Java":"James Gosling","Edad de Camilin":1,"Mi sueldo":8000.0}
print dic
print dic["Creador de Java"]
print dic["Edad de Camilin"]
print dic["Mi sueldo"]
'''

# 10. uso de if  ... else
'''
cadena="migatocomebananas.net"
cadena2="migatocomeperas.net"
numero=1

if cadena==cadena2:
    print "Son idénticas"

else:
    print "son distintas"



if numero>0:
    print "mayor a cero"

elif numero<0:
    print "menor a cero"

else:
    print "ninguno de los dos casos anteriores"

'''

# 11. uso del operador ternario
'''
valor=9
numero= "par" if (valor % 2 == 0) else "impar"
print " resultado: ",numero
'''

#12.  uso de for .. in
'''
vector=[1,2,3,4,5]
for v in vector:
    print v

print ""

vector2=["fer","alma","uriel","camilin"]
for v2 in vector2:
    print v2

'''

#13. uso de funciones con parámetros "variables"
'''
def suma(param1,param2, *otros):
    for val in otros:
        print val

#invocar función suma
print suma(1,2) # con 2 parámetros
print suma(1,2,3) # con 3 parámetros
print suma(1,2,3,4) # con 4 parámetros
'''

#14. determinar el número mayor de un arreglo
'''
numeros=[1,2,3,4,5,6,7,8]
mayor=0
for i in range(len(numeros)-1):
    if (numeros[i+1]<numeros[i]):
        mayor=numeros[i]

    else:
        mayor=numeros[i+1]

print "mayor:  ",mayor
'''

#15.  uso de filter(function,sequence)
''' La funcion filter verifica que los elementos de una secuencia cum-
plan una determinada condición, devolviendo una secuencia con los
elementos que cumplen esa condición. Es decir, para cada elemento de
sequence se aplica la función function; si el resultado es True se añade
a la lista y en caso contrario se descarta
'''

'''
def par(n):
    return (n%2.0==0)

lista=[1,2,3,4,5,6,7,8,9,10,11]
lista2=filter(par,lista)
print lista
print "numeros pares de la lista: ",lista2
'''

#16. uso de reduce(function,sequence[,initial])
'''
La función reduce aplica una función a pares de elementos de una
secuencia hasta dejarla en un solo valor
'''
'''
def restar(x1,x2):
    return x1-x2

def sumar(x1,x2):
    return x1+x2

lista=[1,2,3,4,5]
lista2=reduce(restar,lista)
print "lista original: ",lista
lista2=reduce(restar,lista)
lista3=reduce(sumar,lista)
print "resultado resta: ",lista2
print "resultado suma: ",lista3
'''

# 17. uso de lambda
'''son funciones anónimas que no pueden ser referenciadas
más adelante'''
'''
lista=[1,2,3,4,5,6,7,8,9,10,11,12]
lista2=filter(lambda n: n%2.0==0,lista)
print "lista original: ",lista
print "resultado: ",lista2

numero=lambda x,y: x+y
print numero(2,3) #imprime 5

'''
#18.  uso de try   ... except ... finally
'''
try:
    num=int("21d")

except Exception:
    print "no es numerico"

finally:
    print "limpiando"

'''

#19. números complejos
'''
print "[Números complejos]"
print ""
print (8+9j),"+",(7+12j)," = "
expr=(8+9j) + (7+12j)
print expr
print (8+5j),"-",(6+12j)," = "
expr2=(8+5j) - (6+12j)
print expr2
print (8-9j),"-",(7+2j)," = "
expr3=(8-9j) - (7+12j)
print expr3
print (-8-3j),"+",(-4-12j)," = "
expr4=(-8-3j) + (-4+12j)
print expr4
print (5+3j),"",(8+5j)," = "
expr5=(8+3j) * (8+5j)
print expr5
print ""
print (5-2j)," elevado a 2 = "
expr6=(5-2j)
print pow(expr6,2)
print (-2-7j)," elevado a 3 = "
expr7=(-2-7j)
print pow(expr7,3)
print (-5-21j),"",(-45-5j)," = "
expr8=(-5-21j) * (-45-5j)
print expr8
print (-5-21j),"/",(-45-5j)," = "
expr9=(-5-21j) / (-45-5j)
print expr9
print (3+5j),"/",(3+5j)," = "
expr10=(3+5j) / (3+5j)
print expr10
'''
#20. sistema de ecuaciones lineales
'''
global salir

salir="n"
a11, a12, a21, a22, b1, b2=0, 0, 0, 0, 0, 0
x, y=0, 0

def determinanteX(a11,a12,a21,a22,b1,b2):
    return ((b1*a22)-(b2*a12))/((a11*a22)-(a21*a12))


def determinanteY(a11,a12,a21,a22,b1,b2):
    return ((a11*b2)-(a21*b2))/((a11*a22)-(a21*a12))



def inicio():
    print "\t[Sistema de ecuaciones lineales en Python]"
    print "\ta11X  +  a12Y=b1"
    print "\ta21X  +  a22Y=b2"
    print""
    print "Introduce valores"
    

while salir=="n":
    inicio()

    a11=float(raw_input('a11:'))
    a12=float(raw_input('a12:'))
    a21=float(raw_input('a21:'))
    a22=float(raw_input('a22:'))
    b1=float(raw_input('b1:'))
    b2=float(raw_input('b2:'))
    print""
    print "sistema resultante:"
    print a11,"X +",a12,"Y =",b1
    print a21,"X +",a22,"Y =",b2
    print ""
    print "X=",determinanteX(a11,a12,a21,a22,b1,b2)
    print "Y=",determinanteY(a11,a12,a21,a22,b1,b2)
    

    
    salir=raw_input('¿Desea salir? Si->s  No->n :')

    if (salir=="s"):
        break

'''

# 21 . uso de clases
'''
class Persona:
    def __init__(self,nombre,edad,estatura,direccion,telefono,email):
        self.nombre=nombre
        self.edad=edad
        self.estatura=estatura
        self.direccion=direccion
        self.telefono=telefono
        self.email=email


    def getNombre(self):
        return self.nombre

    def getEdad(self):
        return self.edad
    
    def getEstatura(self):
        return self.estatura
    
    def getDireccion(self):
        return self.direccion

    def getTelefono(self):
        return self.telefono

    def getEmail(self):
        return self.email

#main
objeto= Persona("Andrea",25,1.65,"La Villita", "7221212786", "andrea.calamaro@latin.com")
print "[Datos]\n"
print "nombre: ",objeto.getNombre()
print "edad: ",objeto.getEdad()
print "estatura: ",objeto.getEstatura()
print "direccion: ",objeto.getDireccion()
print "telefono: ",objeto.getTelefono()
print "email: ",objeto.getEmail()

'''

#22. comprehensiones en Python
#lista=[1,2,3,4,5,6,7,8,9]
#print [x*2 for x in range(len(lista))]
#print [x*2 for x in lista]

#for x in lista:
#    print x**2

#[x ** 3 for x in range(5)]
#[x ** 2 for x in range(1,12)]
#[x*2 for x in lista]

#list(map((lambda x: x**2),range(5)))

## imprimen [0,2,4,6,8]
'''
print [x for x in range(10) if x % 2 == 0]

print list(filter((lambda x: x % 2 == 0), range(10)))

result=[]
for x in range(10):
    if x%2==0:
        result.append(x)
print result

'''

#23. map vs comprehensiones
##normal con for y append
'''
print "primer prueba"
resultado=[]
for x in "FERNANDO":
    resultado.append(ord(x))

print resultado

## ahora con map
print ""
print "segunda  prueba"
resultado1=list(map(ord,"FERNANDO"))
print resultado1

##ahora con comprehension
resultado2=[ord(x) for x in "FERNANDO"]
print ""
print "tercer prueba"
print resultado2

'''


#24. más comprehensiones
'''
print [x + y for x in 'ball' for y in 'boy']
print [(x,y) for x in range(5) if x % 2 == 0 for y in range(5) if y % 2 == 1]
print ""
print "otra prueba"
result = []
for x in range(5):
    if x%2==0:
        for y in range(5):
            if y%2==0:
                result.append((x,y))
print result
'''

#25. comprehensiones con matrices
'''
matrix1=[[1,3,4],[0,43,2],[5,3,21]]
matrix2=[[4,7,10],[7,7,2],[12,43,21]]
print"Matrices"
print "m1: ",matrix1
print "m2: ",matrix2
print ""
print [r[2] for r in matrix1]
print "matrix2 ---> posicion (2,1)= ",matrix2[2][1]
'''










