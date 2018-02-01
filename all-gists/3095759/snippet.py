#!/usr/bin/env python

def cozimento( tempo_cozimento=0, a=0, b=0 ):
    output = False
    
    if tempo_cozimento and a and b:
        if a > tempo_cozimento < b:
            # Other stuff
            tempo_minimo = min( a, b ) 
            tempo_maximo = max( a, b ) 
            tempo_processo = tempo_minimo - ( tempo_maximo - tempo_minimo )

            output = ( tempo_processo == tempo_cozimento )
        if tempo_cozimento == a and tempo_cozimento == b:
            output = True
    
    return output