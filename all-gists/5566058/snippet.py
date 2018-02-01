#Ejemplo Clase Basica:

>>> class c:
...     def __init__(self, value=None):
...         self.name = value
...
>>> obj = c()
>>> obj.name = "Andre"


#Ejemplo atributo

>>> obj.name
"Andre"

#Ejemplo Variable de clase
>>> class Student:
...    default_age = 20                  # variable de la clase
...    def __init__ (self):
...        self.age = Student.default_age    # Variable de la instancia


#Ejemplo llamado de funcion del mismo nombre heredada
class Newstudent(Student):
    "New student class"
    def __init__(self):

        Student.__init__(self, Student.default_age)


# Ejemplo de creacion dinamica de atributos
>>> class DummyClass:
... pass
...
>>> colors = DummyClass()
>>> color.alarm = "red"


#Ejemplo Clase

class Coche:
  """Abstraccion de los objetos coche."""
  def __init__(self, gasolina):
    self.gasolina = gasolina
    print "Tenemos", gasolina, "litros"

  def arrancar(self):
    if self.gasolina > 0:
      print "Arranca"
    else:
      print "No arranca"
    
  def conducir(self):
    if self.gasolina > 0:
      self.gasolina -= 1
      print "Quedan", self.gasolina, "litros"
    else:
      print "No se mueve"


#Herencia simple
class Instrumento:
  def __init__(self, precio):
    self.precio = precio
  def tocar(self):
    print "Estamos tocando musica"
  def romper(self):
    print "Eso lo pagas tu"
    print "Son", self.precio, "$$$"

class Bateria(Instrumento):
  pass

class Guitarra(Instrumento):
  pass

#Herencia Multiple
class Terrestre:
  def desplazar(self):
    print "El animal anda"

  def caminar(self):
    print "El animal anda"

class Acuatico:
  def desplazar(self):
    print "El animal nada"

  def nadar(self):
    print "El animal nada"

class Cocodrilo(Terrestre, Acuatico):
  pass

c = Cocodrilo()
c.desplazar()
c.caminar()
c.nadar()


#Ejemplo Encapsulacion
class Ejemplo:
  
  def publico(self):
    print "Publico"
  
  def __privado(self):
    print "Privado"

ej = Ejemplo()
ej.publico()
ej.__privado()
ej._Ejemplo__privado()


#Ejemplo Atributos, getters y setters (antes de 2.2)
class Fecha():
  
  def __init__(self):
    self.__dia = 1
  
  def getDia(self):
    return self.__dia
  
  def setDia(self, dia):
    if dia > 0 and dia < 31:
      self.__dia = dia
    else:
      print "Error"

mi_fecha = Fecha()
mi_fecha.setDia(33)

#Ejemplo Atributos, getters y setters (version 2.2)

class Fecha(object):
  
  def __init__(self):
    self.__dia = 1
  
  def getDia(self):
    return self.__dia
  
  def setDia(self, dia):
    if dia > 0 and dia < 31:
      self.__dia = dia
    else:
      print "Error"
  
  dia = property(getDia, setDia)

mi_fecha = Fecha()
mi_fecha.dia = 33
