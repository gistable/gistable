from java.io import File
from java.io import FileInputStream
from java.util import Properties


#Load properties file in java.util.Properties
def loadPropsFil(propsFil):
	properties={}
	propFil = Properties()
	propFil.load(FileInputStream(propsFil))
	properties.update(propFil)
	return properties

propertyfile='/opt/data/myfile.properties'
properties = loadPropsFil(propertyfile)
for key, value in properties.iteritems():
    print "%s=%s" % (key, value)

dictName="MyDictDev2"
dictId='Environments/%s'%dictName
if repository.exists(dictId):
	print "update dictionary '%s'" %  dictId
	dict=repository.read(dictId)
	dict.values['entries'].putAll(properties)
	repository.update(dict)
else:
	print "new dictionary created '%s'" %  dictId
	dict=repository.create(factory.configurationItem(dictId, 'udm.Dictionary', {'entries':properties}))





