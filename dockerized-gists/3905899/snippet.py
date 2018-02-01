#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Neste problema, você deverá exibir uma lista de 1 a 100, um em cada linha, com as seguintes exceções:

    Números divisíveis por 3 deve aparecer como 'Fizz' ao invés do número;
    Números divisíveis por 5 devem aparecer como 'Buzz' ao invés do número;
    Números divisíveis por 3 e 5 devem aparecer como 'FizzBuzz' ao invés do número'.
"""

import unittest

def fizzbuzz():
    lista = range(1,101)
    for index in range(0, len(lista)):
        if lista[index] % 15 == 0:
            lista[index] = 'FizzBuzz'
        elif lista[index] % 3 == 0:
            lista[index] = "Fizz"
        elif lista[index] % 5 == 0:
            lista[index] = "Buzz" 
    return lista

print fizzbuzz()

class FizzBuzzTest(unittest.TestCase):
    
    def test_imprime1(self):
        self.assertEqual(1, fizzbuzz()[0])
        
    def test_imprime2(self):
        self.assertEqual(2, fizzbuzz()[1])

    def test_imprime3(self):
        self.assertEqual("Fizz", fizzbuzz()[2])
    
    def test_imprime4(self):
        self.assertEqual(4, fizzbuzz()[3])

    def test_imprime5(self):
        self.assertEqual('Buzz', fizzbuzz()[4])
    
    def test_imprime15(self):
        self.assertEquals('FizzBuzz', fizzbuzz()[14])
 
    def test_imprime30(self):
        self.assertEquals('FizzBuzz', fizzbuzz()[29])
    
if __name__== '__main__':
    unittest.main()