#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unicodedata

def elimina_tildes(cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    return s.decode()

string_acentos = 'café'.decode('utf-8')

sin_tildes = elimina_tildes(string_acentos)

print sin_tildes