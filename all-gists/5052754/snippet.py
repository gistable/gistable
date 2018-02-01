#!/usr/bin/python
# -*- coding: utf-8 -*-
import cmath
continuar = "Y"

def ecua():

    a = float(input("A:"))
    b = float(input("B:"))
    c = float(input("C:"))
    formulapos = (-b + cmath.sqrt(b**2 - 4*a*c))/(2*a)
    formulaneg = (-b - cmath.sqrt(b**2 - 4*a*c))/(2*a)
    print("El resultado es {0} y {1}".format(formulapos,formulaneg))
    continuo()

def bicuadrada():
    print("Metemela Negrón")

def opciones():
    todo = input("Bienvenido que desea hacer? \n 1.-Eq.segundo grado \n2.-Eq. bicuadrada\n3.-Salir\n")
    if todo == 1:
        ecua()
    elif todo == 2:
        bicuadrada()
    elif todo ==3:
        quit()

def continuo():
    continuar = raw_input("Desea continuar?")
    if continuar == "N":        
        quit()
    else:
        opciones()

opciones()
