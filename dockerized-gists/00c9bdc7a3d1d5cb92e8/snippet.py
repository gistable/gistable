#!/usr/bin/python 
# -*- coding: utf-8 -*-

class cuenta_bancaria():

    def __init__(self):
        self.titular = "Fulano"
        self.num_cuenta = "123456789"
        self.saldo = 0

    def getTitular(self):
        return self.titular

    def getSaldo(self):
        return self.saldo

miCuenta = cuenta_bancaria()

print "El saldo de la cuenta es",miCuenta.getSaldo()
print "El titular de la cuenta es",miCuenta.getTitular()