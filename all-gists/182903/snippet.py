#!/usr/bin/python
# -*- encoding:utf-8 -*-
# Implementa Modulo 11 de geração e verificação de dígito.
# veja http://pt.wikipedia.org/wiki/D%C3%ADgito_verificador para detalhes

import random
random.seed()

def pin_dv_gen(digs):
  l = len(digs)
  d=0
  for i in range(1,l+1):
    d = d + int(digs[-i])*(i+1)
  dv=d*10 % 11
  if 10==dv: return '0'
  return str( dv )

def pin_dv_verify(digs):
  dig = pin_dv_gen(digs[0:-1])
  return dig==digs[-1]

def generate_pin_with_dv():
  pin="".join(random.sample('0123456789',6))
  return pin+pin_dv_gen(pin)  

