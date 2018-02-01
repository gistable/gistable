#!/usr/bin/env python

def MultiploDeTres(numero):
	return not numero % 3

def MultiploDeCinco(numero):
	return not numero % 5

def FizzBuzz(numero):	
	if MultiploDeTres(numero) and MultiploDeCinco(numero):
		return "fizzbuzz"
	
	if MultiploDeTres(numero):
		return "fizz"

	if MultiploDeCinco(numero):
		return "buzz"

	return numero