# -*- coding: utf-8 -*-
#
#  luciano_silva_simulator.py
#  
#  Copyright 2015 Ericson Willians (Rederick Deathwill) <EricsonWRP@ERICSONWRP-PC>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from random import randint, seed

class LucianoSilvaSimulator:
    
    def __init__(self, input_seed=7):
        seed(input_seed)
        self.start_keywords = [
            "Uso python para ", 
            "Até agora não vi ninguém falar sobre ", 
            "Tem programado que vive na "
        ]
        self.end_keywords = [
            "redes.", 
            "python.", 
            "bugs.", 
            "o escape...", 
            "educação.", 
            "código fonte.", 
            "todo e qualquer código.",
            "deep web.",
            "surface.",
            "alienação.",
            "os códigos fontes criados ou melhor reaproveitados.",
            "object.",
            "nubi.",
            "brasilzao.",
            "sombra de outro"
        ]
        self.resolution_keywords = [
            " Cadê as soluções?", 
            " O problema tá no código fonte...", 
            " Bugs", 
            " Mais aonde estão os programadores \" \" para corrigir."
        ]

    def write(self, path, number_of_sentences=5000):
        out = open(path, 'w')
        for n in range(number_of_sentences):
            out.write(self.generate_sentence() + '\n')

    def generate_sentence(self):
        x = self.start_keywords[randint(0, len(self.start_keywords)-1)]
        y = self.end_keywords[randint(0, len(self.end_keywords)-1)]
        z = self.resolution_keywords[randint(0, len(self.resolution_keywords)-1)]
        return x + y + z

if __name__ == '__main__':
    
    l = LucianoSilvaSimulator()
    l.write("random_luciano_sentences.txt")