import os
import os.path

class Message(object):
    def __init__(self, myfile):
        self.vcard = ''
        self.vbody = ''
        content = myfile.readlines()
        for k in content:        
            splitted = k.splitlines()
            for y in splitted:
                prova = y.split(':')
                self.vbody = prova
        print len(self.vbody)
            

#la parte che legge il contenuto di una directory e lo usa per
#creare una lista di oggetti File.
#Prima di aprire un file viene verificata la condizione che l'utente abbia
#i permessi di accesso al file in lettura. Vedi EAFP.
 
path = "D:\\docs\\toprocess"
listing = os.listdir(path)
messages = []

for infile in listing:
    print "current file is: " + infile
    with open(os.path.join(path, infile)) as myfile:
        tempMsg = Message(myfile)
        messages.append(tempMsg)


