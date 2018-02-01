#!/usr/bin/env python
import zipfile

tempdirlin='/home/user/sattemp'
tempdirwine='D:\\'
converterbin="/windows/Programme/Program Files (x86)/DesignSpark/DesignSpark Mechanical 1.0/sabSatConverter.exe"
# add freecad libdir to path
import sys
sys.path.insert(0,'/usr/local/freecad/lib')

def transform2placement(str1):
    import FreeCAD
    mat1=FreeCAD.Matrix(*tuple(float(s) for s in str1.split()))
    if not mat1.submatrix(3).isOrthogonal():
        raise ValueError('Deformation Matrix')
    else:
        return FreeCAD.Placement(mat1)

class scfile:
    xmlfilenames={'SpaceClaim/Graphics/renderlist.xml':'render', \
        'SpaceClaim/_rels/document.xml.rels':'rels', \
        'SpaceClaim/document.xml':'doc' }
    def __init__(self,rsdoc,rsdocfn='u',extractgeometry=False):
        import os
        import subprocess
        self.xmlcontent={}
        self.refs={}
        self.caption={}
        self.missing=set()
        #rsdocfn=os.path.split(fname)[-1].rsplit('.',1)[0]
        #rsdoc=zipfile.ZipFile(fname,'r')
        for zipinfo in rsdoc.infolist():
            fn=zipinfo.filename
            if fn in self.xmlfilenames.keys():
                infile=rsdoc.open(zipinfo,'r')
                import xml.etree.ElementTree as ET
                xmltree = ET.fromstring(infile.read())
                infile.close()
                self.xmlcontent[self.xmlfilenames[fn]]=xmltree
            elif extractgeometry and fn.startswith('SpaceClaim/Geometry/') and \
                    fn.endswith('.sab'):
                fnshort=fn[:-4].rsplit('/',1)[-1]
                try:
                    fnshort='%03d' % int(fnshort.split('x',2)[0][1:])
                except ValueError:
                    pass

                #print fnshort
                sabfilename='tempsab.sab'
                satfilename='tempsat.sat'
                sabpath=os.path.join(tempdirlin,sabfilename)
                satpath=os.path.join(tempdirlin,satfilename)
                outfile=open(sabpath,'wb')
                infile=rsdoc.open(zipinfo,'r')
                outfile.write(infile.read())
                outfile.close()
                infile.close()
                if subprocess.call(["wine", converterbin, "-i", \
                        tempdirwine+sabfilename,"-o",\
                        '%s%s-%s.sat' % (tempdirwine,rsdocfn,fnshort)]) == 0:
                    os.unlink(sabpath)
                else:
                    print 'failed %s' % (rsdocfn+ fnshort)
        self._buildrels()
        self._buildcaption()
        self._buildshortdicts()
        self._buildpartdict()

    def _buildrels(self):
        #store rels in dict
        self.rdoc={}
        for ref in self.xmlcontent['rels']:
            refid= ref.attrib['Type'].split('#',1)[-1]#.rsplit(':',1)[-1]
            if ref.attrib['Target'].startswith('/SpaceClaim/Geometry/'):
                if refid in self.refs:
                    raise ValueError(refid)
                self.refs[refid] = (ref.attrib['Id'],ref.attrib['Target'])
            self.rdoc[ref.attrib['Id']]=(refid,ref.attrib['Target'])
#                self.uid2short[refid.split(':',1)[0]]=ir

    def _buildcaption(self):
        for captiondef in self.xmlcontent['doc'].find('{urn:presentation}PresentationDef').findall(\
                '{urn:presentation}CaptionDef'):
            #print tuple(captiondef)
            key=captiondef.find('{urn:presentation}subjectId').text
            self.caption[key]=(captiondef.find('{urn:presentation}name').text,\
                    captiondef.find('{urn:presentation}type').text,\
                    captiondef.find('{urn:presentation}description').text)
            shortkey=key.rsplit(':',1)[-1]

    def _buildpartdict(self):
        self.partdict={}
        for part in self.xmlcontent['doc'].find('{urn:nom}Design')\
                .findall('{urn:nom}PartDef'):
            key=part.get('Id')
            self.partdict[key]=part

    def _buildshortdicts(self):
        uid2objects={}
        objects2uid={}
        prefix2objects={}
        objects2prefix={}
        #rodo cache the disct
        for rkey in self.refs.iterkeys():
            ruid,robj = rkey.split(':',1)
            ruidlst = uid2objects.get(ruid,[])
            robjlst = objects2uid.get(robj,[])
            ruidlst.append(robj)
            robjlst.append(ruid)
            uid2objects[ruid]=ruidlst
            objects2uid[robj]=robjlst
        for pkey in self.caption.iterkeys():
            puid,pobj = pkey.split(':',1)
            puidlst = prefix2objects.get(puid,[])
            puidlst.append(pobj)
            prefix2objects[puid]=puidlst
            ouidlst = objects2prefix.get(pobj,[])
            ouidlst.append(puid)
            objects2prefix[pobj]=ouidlst
        self.uid2objects=uid2objects
        self.objects2uid=objects2uid
        self.prefix2objects=prefix2objects
        self.objects2prefix=objects2prefix

    def shortref2uidref(self,str1):
        shortref,index=str1.split(':',1)
        lst1=self.prefix2objects.get(shortref,[])
        #lst1=self.objects2uid.get(shortref,[])
        set1=set()
        for elm1 in lst1:
            set1.update(set(self.objects2uid.get(elm1,[])))
        if len(set1)==1:
            return '%s:%s'%(tuple(set1)[0],index)

    def uidref2shortref(self,str1):
        uid,index=str1.split(':',1)
        lst1=self.uid2objects.get(uid,[])
        set1=set()
        for elm1 in lst1:
            set1.update(set(self.objects2prefix.get(elm1,[])))
        if len(set1)==1:
            return '%s:%s'%(tuple(set1)[0],index)
        if uid in self.uid2short:
            return '%d:%s' % (self.uid2short[uid],index)
        else:
            candidates = []
            for key,value in self.caption.iteritems():
                if key.rsplit(':',1)[-1] == index:
                    candidates.append(key)
            if len(candidates) == 1:
                return candidates[0]
            elif len(candidates) == 0:
                return str1

    def subtree2freecad(self,fcdoc=None,rootpart=None):
        import FreeCAD
        import Part
        if fcdoc is None:
            returndoc = True
            fcdoc = FreeCAD.newDocument()
        else:
            returndoc = False
        if rootpart is None:
            rootpart = self.xmlcontent['doc'].find(\
                    '{urn:nom}Design').find('{urn:nom}PartDef')
        partdef=rootpart #testing
        pdid=partdef.get('Id')
        pname=self.caption.get(pdid,('Noname',)) 
        fcpd=fcdoc.addObject('Part::Compound',\
                'partdef_%s' % pdid.replace(':','_'))
        fcpd.Label=pname[0]
        #add Nominal body defs
        for nbd in partdef.findall('{urn:nom}NominalBodyDef'):
            nbdid = nbd.get('Id')
            #print ndbid, ndbid in self.refs, self.caption.get(ndbid)
            #ndb.find('{urn:nom}type').text, ndbid,\
            uidref=self.shortref2uidref(nbdid)
            nbdref = self.refs.get(uidref)
            if nbdref is not None:
                pass
                fcnbd=fcdoc.addObject('Part::Feature',\
                'nbdef_%s' % nbdid.replace(':','_'))
                fcnbd.Label=self.caption.get(nbdid,('Noname',))[0]
                fcpd.Links = fcpd.Links + [fcnbd]
            pass

        #add component defs
        for cd in partdef.findall('{urn:nom}ComponentDef'):
            cdid=cd.get('Id')
            placement=transform2placement(cd.find('{urn:nom}trans').text)
            source=cd.find('{urn:nom}source')
            refid=source.get('refId')
            partref=self.uidref2shortref(refid)
            subpart = self.partdict.get(partref)
            if subpart is not None:
                fcsubpart=self.subtree2freecad(fcdoc,subpart)
                fcsubpart.Placement=placement
                fcpd.Links = fcpd.Links + [fcsubpart]
            else:
                print 'missing part',refid
                self.missing.add(refid)
                #print partref,refid
                #print source.attrib
                #print source.get('targetDoc'),source[:]
                #print self.rdoc.get(source.get('targetDoc'))
                #for ref in self.xmlcontent['rels']:
                #    print ref
#            refid= ref.attrib['Type'].split('#',1)[-1]#.rsplit(':',1)[-1]
                    
        if returndoc:
            return fcdoc
        else: # return the compound created for a Component
            return fcpd




    def printpart(self, partdef,intdentation=1):
        pdid=partdef.get('Id')
        pname=self.caption.get(pdid)
        print ' ' * intdentation, partdef.find('{urn:nom}type').text, \
                pdid,pname
        for el in partdef:
            if el.tag == '{urn:nom}NominalBodyDef':
                ndbid = el.get('Id')
                print ' '*intdentation, 'NBD', \
                        el.find('{urn:nom}type').text, ndbid,\
                        self.caption.get(ndbid)
                        #, ndbid.split(':',1)[-1] in \
                        #tuple(key.rsplit(':',1)[-1] for key in refs.keys())
            elif el.tag == '{urn:nom}ComponentDef':
                cdid=el.get('Id')
                transform = el.find('{urn:nom}trans').text
                source=el.find('{urn:nom}source')
                refid=source.get('refId')
                partref=self.uidref2shortref(refid)
                        #\
                        #refid.split(':',1)[0]),\
                        #refid.rsplit(':',1)[-1])
                #partref=self.uidref2shortref(refid)
                #partref=refid
                cdname=self.caption.get(partref) 
                #or  self.caption.get(self.uidref2shortref(partref))
                        
                        #searchpartwithshortid(partref,caption)
                print ' ' * intdentation, 'CD', cdid, refid, cdname
                if transform != '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1':
                    t = transform.split(' ')
                    if t[0:3]==['1','0','0'] and \
                            t[4:7]   == ['0','1','0'] and \
                            t[8:11]  == ['0','0','1'] and \
                            t[12:16] == ['0','0','0','1']:
                        print 'translate %s,%s,%s' % (t[3],t[7],t[11])
                    else:
                        print 'transform %s' % transform
                print transform2placement(transform)
                
                subpart = self.partdict.get(partref)
                if subpart is not None:
                    self.printpart(subpart,intdentation+1)
                else:
                    print source.attrib
                    print self.rdoc.get(source.get('targetDoc'))
#
#                for subpart in self.xmlcontent['doc'].find('{urn:nom}Design'):
#                    if partref  == subpart.get('Id'):
#                        self.printpart(subpart,intdentation+1)

                pass
            elif False and el.tag == '{urn:nom}ComponentDef':
                cdid=el.get('Id')
                refid=el.find('{urn:nom}source').get('refId')

                print 'CD', cdid, el.find('{urn:nom}source').get('refId')
                if transform != '1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1':
                    print transform
                print refid.rsplit(':',1)[-1] in \
                        tuple(key.rsplit(':',1)[-1] for key in refs.keys())
                for el2 in partdef.findall('{urn:nom}NominalBodyDef'):
                    print 'not match' ,el2.get('Id').rsplit(':',1)[-1] , \
                            refid.rsplit(':',1)[-1]
                    if el2.get('Id').rsplit(':',1)[-1] == \
                            refid.rsplit(':',1)[-1]:
                        print el2.attrib
            else:
                pass
                #print ' ' * intdentation,  el.tag,el.attrib,el.text#,tuple(el)
    def printrootpart(self):
        self.printpart(self.xmlcontent['doc'].find('{urn:nom}Design')\
                .find('{urn:nom}PartDef'),1)

    def searchpartwithshortid(self,str1):
        candidates = []
        uid,shortstr = str1.split(':',1)
        for key,value in self.caption.iteritems():
            if key.rsplit(':',1)[-1] == shortstr:
                candidates.append(value)
        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) == 0:
            return None


def processrsdoc(rsdoc,rsdocfn='u',extractgeometry=False):
    scfileobj=scfile(rsdoc,rsdocfn,extractgeometry)
#    scfileobj.printrootpart()
    xmlcontent=scfileobj.xmlcontent
    fcdoc=scfileobj.subtree2freecad()
#    #fcdoc.saveAs('')
    return xmlcontent
        
def processrsdocfile(fname):
    import os
    rsdocfn=os.path.split(fname)[-1].rsplit('.',1)[0]
    return processrsdoc(zipfile.ZipFile(fname,'r'),rsdocfn)

def processrsdocstring(str1,rsdocfn='u'):
    import StringIO
    return processrsdoc(zipfile.ZipFile(StringIO.StringIO(str1),'r'),rsdocfn)

if __name__ == '__main__':
    import sys
    if len(sys.argv)>1:
        for fname in sys.argv[1:]:
            if zipfile.is_zipfile(fname):
                processrsdocfile(fname)
  