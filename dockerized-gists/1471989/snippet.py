# -*- coding: utf-8 -*-

clippings = 'My Clippings.txt'
ankiFile = 'AnkiImport.txt'

def kindle_to_anki():
	try:
		clippingsFile = open(clippings, 'r')
	except IOError, e:
		print '*** file open error: ', e

	anki_import = open(ankiFile, 'w')

	kindle_notes = clippingsFile.readlines()

	anki_import.writelines(['"%s"\t"%s"\n\n' % (kindle_notes[i].strip(), kindle_notes[i+3].strip()) 
		for i in range(0, len(kindle_notes), 5)])

	anki_import.close()
	clippingsFile.close()

if __name__ == '__main__':
	kindle_to_anki()