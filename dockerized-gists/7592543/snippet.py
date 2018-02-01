#funcion para calcular un porcentaje de avance
# meta, avance
def es_igual(descripcion, dado, esperado):
  print("%s: %s" % (dado==esperado, descripcion))

def calcular_porcentaje(meta, avance):
  if meta == 0:
    return 0.0

  if avance > meta:
    return 100.0

  return (float(avance)/float(meta))*100.0

es_igual("el porcentaje deberia ser 0 cuando la meta es 0", calcular_porcentaje(0, 3), 0.0)

es_igual("el porcentaje deberia ser 100 si el avance es mayor a la meta", calcular_porcentaje(10, 11), 100.0)

es_igual("el porcentaje deberia ser 50 si la meta es 30 y el avance es 15", calcular_porcentaje(30, 15), 50.0)
