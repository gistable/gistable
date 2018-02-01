#!/usr/bin/python                                                                        
# -*- coding: utf-8 -*-

# http://docs.python.org/tutorial/datastructures.html
                                                                  
l = [ 1, 10, 4, 2, 4, 3, 3, 1, 1, 3]                                                     
                                                                                         
print l                                                                                  
                                                                                         
promedio = sum(l)/len(l)                                                                 
print "largo ",len(l), ", promedio:",promedio                                            
                                                                                         
# moda                                                                                   
repeticiones = 0                                                                         
for i in l:                                                                              
    apariciones = l.count(i)                                                             
    if apariciones > repeticiones:                                                       
        repeticiones = apariciones                                                       
                                                                                         
modas = []                                                                               
for i in l:                                                                              
    apariciones = l.count(i)                                                             
    if apariciones == repeticiones and i not in modas:                                   
        modas.append(i)                                                                  
                                                                                         
print "moda:", modas                                                                     
                                                                                         
# mediana                                                                                
l.sort()                                                                                 
print l                                                                                  
                                                                                         
if len(l) % 2 == 0:                                                                      
    n = len(l)                                                                           
    mediana = (l[n/2-1]+ l[n/2] )/2                                                      
else:                                                                                    
    mediana =l[len(l)/2]                                                                 
                                                                                         
print 'mediana:',mediana 