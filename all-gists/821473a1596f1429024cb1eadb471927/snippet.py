#!/usr/bin/env python

import logging
from optparse import OptionParser
import os
from osgeo import ogr

def log_file_fields(filename):
    print("File: " + filename)
    source = ogr.Open(filename)

    for i in range(source.GetLayerCount()):
        layer = source.GetLayerByIndex(i)
        layerName = layer.GetName()
        print("Layer: " + layerName)
        stringFields = []
        layerDefinition = layer.GetLayerDefn()
        for n in range(layerDefinition.GetFieldCount()):
            fieldDefinition = layerDefinition.GetFieldDefn(n)
            fieldName =  fieldDefinition.GetName()
            fieldTypeCode = fieldDefinition.GetType()
            fieldType = fieldDefinition.GetFieldTypeName(fieldTypeCode)
            if fieldType == "String":
                stringFields.append(fieldName)
    
        print("String Fields:")
        for field in stringFields:
            sql = 'SELECT %s FROM %s' % (field, layerName)
            fieldLayer = source.ExecuteSQL(sql)
            values = {}
            for i, feature in enumerate(fieldLayer):
                values[feature.GetField(0)] = values.get(feature.GetField(0), 0) + 1
        
            print("Field: " + field)
            for key in sorted(values.keys()):
                print("'%s': %d" % (key, values[key]))
            print("\n")

def _main():
    usage = "usage: %prog"
    parser = OptionParser(usage=usage,
                          description="")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      help="Turn on debug logging")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
                      help="turn off all logging")

    (options, args) = parser.parse_args()
 
    logging.basicConfig(level=logging.DEBUG if options.debug else
    (logging.ERROR if options.quiet else logging.INFO))

    for arg in args:
        log_file_fields(arg)

if __name__ == "__main__":
    _main()