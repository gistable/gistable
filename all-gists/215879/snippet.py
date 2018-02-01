#! /usr/bin/python                                                              
# -*- coding: utf-8 -*-                                                         
#                                                                               
# Simple XML validator done while learning the use of lxml library.             
#   -- Juhamatti Niemelä <iiska AT iki DOT fi>                                  
                                                                                
import lxml                                                                     
from lxml import etree                                                          
                                                                                
if __name__ == "__main__":                                                      
    import sys, os                                                              
                                                                                
    if len(sys.argv) != 3:                                                      
        print "Usage: %s document.xml schema.xsd" % (sys.argv[0])               
        exit(0)                                                                 
                                                                                
    with open(sys.argv[2]) as f:                                                
        doc = etree.parse(f)                                                    
                                                                                
    print "Validating schema ... "                                              
    try:                                                                        
        schema = etree.XMLSchema(doc)                                           
    except lxml.etree.XMLSchemaParseError as e:                                 
        print e                                                                 
        exit(1)                                                                 
                                                                                
    print "Schema OK"                                                           
                                                                                
    with open(sys.argv[1]) as f:                                                
        doc = etree.parse(f)                                                    
                                                                                
    print "Validating document ..."                                             
    try:                                                                        
        schema.assertValid(doc)                                                 
    except lxml.etree.DocumentInvalid as e:                                     
        print e                                                                 
        exit(1)                                                                 
                                                                                
    print "Document OK" 