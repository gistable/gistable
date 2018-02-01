# -*- coding: utf-8 *-*
from django.db import models


class Propietario(models.Model):

    propietario = models.CharField(max_length=255)


class Vehiculo(models.Model):

    clase = models.CharField(max_length=255)
    marca = models.CharField(max_length=25)
    combustible = models.CharField(max_length=15)
    carroseria = models.CharField(max_length=25)
    


class DetallePropitario(models.Model):

    vehiculo = models.ForeignKey(Vehiculo)
    propietario = models.ForeignKey(Propietario)
    estado = models.BooleanField()


class Placa(models.Model):

    numero = models.CharField(max_length=15)
    estado = models.BooleanField()
    vehiculo = models.ForeignKey(Vehiculo)
