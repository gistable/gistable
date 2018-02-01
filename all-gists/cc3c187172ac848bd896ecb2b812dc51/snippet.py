#!/usr/bin/python
# -*- coding: utf-8  -*-

import os, shutil, urlparse, urllib
import zipfile
import argparse

from PIL import Image
from internetarchive import download

# How to use it

# Dependencies:
#* PIL (Pillow version: http://pillow.readthedocs.io/en/3.1.x/installation.html) built with OpenJPEG support (for JPEG2000)
#* internetarchive: https://pypi.python.org/pypi/internetarchive
#* djvuLibre: http://djvu.sourceforge.net/

#1. create a working folder on your pc and copy the code as jp2todjvu.py.py
#2. go into folder and verify djvuLibre, PIL and internetarchive are reachable
#3. run the script: python jp2todjvu.py ID_ARCHIVE


# Technical details:

# input: IA_identifier
# files: IA_identifier.pdf
#        IA_identifier_djvu.xml
# routines esterne: cjb2, djvm, djvuxmlparser, pdfimages
# nome pagine: IA_identifier_0000.djvu, IA_identifier_0001.djvu....

# cartella jp2: jp2
# cartella jpg: jpg
# cartella djvu individuali: djvu
# cartella input: input
# cartella output: output

# as-it-is copy of https://it.wikisource.org/w/index.php?title=Progetto:Bot/Programmi_in_Python_per_i_bot/jp2todjvu.py&oldid=1809134
# contributors: Alex brollo, Laurentius, Aubrey


def path2url(path):
        return urlparse.urljoin('file:', urllib.pathname2url(path))

def cleanfolder(dirpath):
        if not os.path.isdir(dirpath):
                os.mkdir(dirpath)

        for filename in os.listdir(dirpath):
                filepath = os.path.join(dirpath, filename)
                try:
                        shutil.rmtree(filepath)
                except OSError:
                        os.remove(filepath)

def dezip(zipf):
        cleanfolder("jp2")
        z = zipfile.ZipFile(os.path.join("input", zipf))
        for f in z.namelist():
                jp2 = f.split("/").pop()
                if jp2.endswith(".jp2"):
                        data = z.read(f)
                        open(os.path.join("jp2", jp2), "wb").write(data)
                print jp2, " saved"

def downloadItem(IAid):
        cleanfolder("input")
        download(IAid,glob_pattern="*_djvu.xml",destdir="input", verbose=True,no_directory=True)
        download(IAid,glob_pattern="*_jp2.zip",destdir="input", verbose=True,no_directory=True)

def jp2tojpg(fileformat="jpg"):
    if fileformat not in ("jpg", "pbm"):
        raise ValueError("Formato file intermedio non supportato")
    cleanfolder("jpg")
    cleanfolder("pbm")
    listaJp2 = os.listdir("jp2")
    listaJp2.sort()
    for f in range(len(listaJp2)):
        if listaJp2[f].endswith(".jp2"):
            fout = "%s.%s" % (listaJp2[f][0:-4], fileformat)
            image = Image.open(os.path.join("jp2", listaJp2[f]))
            if f == 0 and image.size[0] < 1000:
                    fattore=1024.0/image.size[0]
                    image=image.resize((int(image.size[0]*fattore),int(image.size[1]*fattore)))
            image.save(os.path.join(fileformat, fout))
            #comando="convert jp2/%s jpg/%s" % (listaJp2[f], fout)
            #res = os.system(comando)
            print fout, " salvata"

def jpgtodjvu(fileformat="jpg"):
    if fileformat not in ("jpg", "pbm"):
        raise ValueError("Formato file intermedio non supportato")
    cleanfolder("djvu")
    listaImmagini = os.listdir(fileformat)
    for f in listaImmagini:
        if f.endswith("." + fileformat):
            comando = "c44 %s %s" % (os.path.join(fileformat, f),
                os.path.join("djvu", f[0:-4] + ".djvu"))
            res = os.system(comando)
            print res,comando

def merge(pathdjvu="djvu"):
        cleanfolder("output")
        listaDjvu=os.listdir(pathdjvu)
        listaDjvu.sort()
        lista=""
        for n in range(len(listaDjvu)):
                if listaDjvu[n].endswith(".djvu"):
                        lista+=os.path.join("djvu",listaDjvu[n])+" "
                if len(lista)>7500:
                        break

        djvuBundled=os.path.join("output",listaDjvu[0].replace("_0000.djvu",".djvu"))
        comando="djvm -c %s %s" % (djvuBundled,lista)
        res=os.system(comando)
        print res,comando
        if n<len(listaDjvu):
                np=n+1
                for n in range(np,len(listaDjvu)):
                        comando="djvm -i %s %s" % (djvuBundled,os.path.join("djvu",listaDjvu[n]))
                        res=os.system(comando)
                        print res,comando
        return lista



def editXml(IAid):
        xmlFile=os.path.join("input",IAid)+"_djvu.xml"
        xml=open(xmlFile).read()
        url=find_stringa(xml,'OBJECT data="','"',0)
        urlNew=path2url(os.getcwd())+"/output/"+IAid+".djvu"
        xml=xml.replace(url,urlNew)
        open(xmlFile,"w").write(xml)
        print "File "+IAid+"_djvu.xml modificato"

def caricaTesto(IAid):
        editXml(IAid)
        # splits xml into header, list of obiects, footer
        # to build smaller temp xml files (50 pages blocks)
        # and to run them avoiding out of memory errors
        h,b,f=splitObject(IAid)
        for i in range(0,len(b),50):
                open("testo.xml","w").write(h+"\n".join(b[i:i+50])+f)
                print "scritto xml per pagine ",i," - ",i+50
                comando="djvuxmlparser testo.xml"# %s" % (os.path.join("input",IAid+"_djvu.xml"))
                print comando
                res=os.system(comando)
                print "risultato: ",res

# utilities 

def find_stringa(stringa,idi,idf,dc=0,x=None,side="left"):
    if side=="right":
        idip=stringa.rfind(idi)
    else:
        idip=stringa.find(idi)
    idfp=stringa.find(idf,idip+len(idi))+len(idf)
    if idip>-1 and idfp>0:
        if x!=None:
            while stringa[idip:idfp].count(x)>stringa[idip:idfp].count(idf):
                if stringa[idip:idfp].count(x)>stringa[idip:idfp].count(idf):
                    idfp=stringa.find(idf,idfp)+len(idf)

        if dc==0:
            vvalore=stringa[idip+len(idi):idfp-len(idf)]
        else:
            vvalore=stringa[idip:idfp]
    else:
        vvalore=""
    return vvalore

def produci_lista(testo,idi,idf,dc=1,inizio=None):
    t=testo[:]
    lista=[]
    while not find_stringa(t,idi,idf,1,inizio)=="":
        el=find_stringa(t,idi,idf,1,inizio)
        t=t.replace(el,"",1)
        if dc==0:
            el=find_stringa(el,idi,idf,0,inizio)
        lista.append(el)
    return lista

def carica_pcl(nome_file, folder="dati/"):
    nome_file=folder+nome_file+".pcl"
    f=open(nome_file)
    contenuto=pickle.load(f)
    f.close()
    return contenuto

def salva_pcl(variabile,nome_file="dato",folder="dati/"):
    nome_file=folder+nome_file+".pcl"
    f=open(nome_file,"w")
    pickle.dump(variabile, f)
    f.close()
    print "Variabile salvata nel file "+nome_file

def main(IAid, down=True, fileformat="jpg"):
        if down:
                downloadItem(IAid)
        dezip(IAid + "_jp2.zip")
        jp2tojpg(fileformat=fileformat)
        jpgtodjvu(fileformat=fileformat)
        merge()
        caricaTesto(IAid)


def splitObject(IAid):
    """
    Splitta djvu.xml in header, lista di object, footer.
    """
    xmlFile=os.path.join("input",IAid)+"_djvu.xml"
    xml=open(xmlFile).read()
    fs=xml.split("<OBJECT")
    for i in range(1,len(fs)):
        fs[i]="<OBJECT "+fs[i].strip()
    fs[len(fs)-1]=fs[len(fs)-1].replace("\n</BODY>\n</DjVuXML>","")
    footer="\n</BODY>\n</DjVuXML>"
    header=fs.pop(0)+"\n"
    return (header,fs,footer)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crea un file DjVu a partire dall'Internet Archive.")

    parser.add_argument('id', help="identificatore dell'Internet Archive")

    parser.add_argument('--no-download', dest='download',
                        action='store_false', help='non scaricare il file')
    parser.add_argument('--pbm', dest='pbm',
                        action='store_true', help='usa PBM come formato intermedio (non compresso)')

    args = parser.parse_args()

    main(args.id, down=args.download, fileformat=("pbm" if args.pbm else "jpg"))


