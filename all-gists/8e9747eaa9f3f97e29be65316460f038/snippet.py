# -*- coding: utf-8 -*-
import pypyodbc

#Example: Automatically populate library with real P/Ns from Digi-Key

#Open database file (NB: This worked with older .MDB file, haven't updated)
dbconn = pypyodbc.win_connect_mdb(r'newae_dblib\NewAElib_db.MDB')

cur = dbconn.cursor()


#(u'RCHIP-51R-0603', u'RES-EU', u'Libraries\\NewAE_AltiumLib.SchLib', u'=Value', u'Standard', u'Standard', u'51R, 0603', u'0603', None, None, u'2', None, None, u'51R', u'Libraries\\NewAE_AltiumLib.PcbLib', u'RESC1608X55N', u'0603', u'1608', None, None, None, None, None, None, None, None, None, u'Surface Mount', None, None, None, None)

db_tables = {
    "Part Number":"Part Number when placing in AD",
    "Value":"Value for resistors, capacitors, etc",
    "Comment":"Displayed on schematic (P/N, or =Value)",
    "Description":"Human-readable description of part",
    "Library Path":"Symbol Library Path",
    "Library Ref":"Symbol Library Ref",
    "Component Kind":"",
    "Component Type":"",
    "Footprint":"Human-Readable footprint info",
    "Footprint Path":"PCB Library Path",
    "Footprint Ref":"PCB Library Ref",
    "Manufacture 1":"Option #1 Manufacture",
    "Manufacture Part Number 1":"Option #1 MPN",
    "Pin Count":"0",
    "Supplier 1":"Digi-Key (normally)",
    "Supplier Part Number 1":"",
    "Case-EIA":"EIA Case size (0603 etc)",
    "Case-Metric":"Metric Case Size",
    "Rated Voltage":"",
    "Mounting Technology":"",
    "Tolerance":"",
    "Temperature Range":"",
}


#Make blank table
db_newpart = db_tables.copy()
for k in db_tables.keys():
    db_newpart[k] = ""
    
db_newpart["Comment"] = "=Value"
db_newpart["Library Path"] = "Libraries\NewAE_AltiumLib.SchLib"
db_newpart["Library Ref"] = "RES-EU"
db_newpart["Component Kind"] = "Standard"
db_newpart["Component Type"] = "Standard"
db_newpart["Footprint"] = "0603"
db_newpart["Footprint Path"] = "Libraries\NewAE_AltiumLib.PcbLib"
db_newpart["Footprint Ref"] = "RESC1608X55N"
db_newpart["Pin Count"] = "2"
db_newpart["Case-EIA"] = "0603"
db_newpart["Case-Metric"] = "1608"
db_newpart["Mounting Technology"] = "SMT"

from urllib import urlopen
from sgmllib import SGMLParser

headers = ['Digi-Key Part Number',
           'Manufacturer',
           'Manufacturer Part Number',
           'Description',
           'Lead Free Status / RoHS Status',
           'Operating Temperature',
           'Standard Package',
           'Price Break',
           'Unit Price',
           'Extended Price']

class DK_Parser(SGMLParser):
    def reset(self):

        SGMLParser.reset(self)

        self.last_td = ''
        self.inside_th = False
        self.inside_td = False
        self.grab_data = False
        self.part_info = {}
        self.hdr_index = 0
        self.row_hdrs = []

    def start_tr(self, attrs): # row
        self.first_header_in_row = True

    def start_th(self, attrs): # header cell
        if self.first_header_in_row:
            self.first_header_in_row = False
            self.row_hdrs = []
            self.hdr_index = 0
        self.inside_th = True

    def end_th(self):
        self.inside_th = False

    def start_td(self, attrs): # data cell
        self.inside_td = True

    def end_td(self): 
        self.inside_td = False
        self.hdr_index = self.hdr_index+1

    def handle_data(self,text):
        text = text.strip()
        if self.inside_th:
            if text in headers:
                self.row_hdrs.append(text)
                self.last_td = ''
                self.grab_data = True
            else:
                self.grab_data = False
        elif self.inside_td and self.grab_data:
            if self.hdr_index:
                self.last_td = ''
            if self.hdr_index < len(self.row_hdrs):
                self.last_td = self.last_td + text
                self.part_info[self.row_hdrs[self.hdr_index]] = self.last_td
                
                
def lookup_mpn(mpn, suffix="CT-ND"):
    dk_url = 'http://search.digikey.com/scripts/DkSearch/dksus.dll'
    dk_params = '?Detail&keywords='
    sock = urlopen(dk_url + dk_params + mpn)
    data = sock.read()
    data = data.split(" ")
    
    #Select cut-tape if that is an option
    dkpn = None
    for d in data:
        if suffix in d:
            dkpn = d
            break
    
    if dkpn is not None:
        dkpn = dkpn.replace("value=", "").replace('"', '')
    
    return dkpn


def lookup_dpn(dkpn):
    dk_url = 'http://search.digikey.com/scripts/DkSearch/dksus.dll'
    dk_params = '?Detail&name='
    sock = urlopen(dk_url + dk_params + dkpn)
    parser = DK_Parser()
    data = sock.read()
    parser.feed(data)
    sock.close()
    parser.close()
    
    return parser.part_info


e24 = [100, 110, 120, 130, 140, 150, 160, 180, 200, 220, 240, 270, 300, 330, 360, 390, 430, 470, 510, 560, 620, 680, 750, 820, 910]
mult = [0.01, 0.1, 1, 10, 100, 1000]


for m in mult:
    for r in e24:
        rval = m * float(r)
        
        rsval = "String Value for Database"
        mpnval = "RC0603FR-07"
        
        if m < 0.1:
            rsval = "%.1f"%rval
            rsval = rsval.replace(".", "R")
            
            mpnval += rsval.replace("R0", "R")
            mpnval += "L"            
            
        elif m > 1:
            rsval = "%.1f"%(rval / 1000)
            rsval = rsval.replace(".", "k").replace("k0", "k")
            
            mpnval += rsval.replace("k", "K")
            mpnval += "L"            
            
        else:
            rsval = "%d"%rval
            rsval += "R"
            
            mpnval += rsval.replace("k", "K")
            mpnval += "L"   
        
        dpn = "???"
        dpn = lookup_mpn(mpnval)
        
        print "%s = %s (%s)" % (rsval, mpnval, dpn)
        
        if dpn is not None:
            #data = lookup_dpn(dpn)
            #print data        
            #Add relevant things
            db_newpart["Description"] = "%s res, 0603, 1%%, 1/10W"%rsval
            db_newpart["Part Number"] = "RCHIP-%s-0603"%(rsval.upper())
            db_newpart["Value"] = rsval
            db_newpart["Manufacture 1"] = "Yageo"
            db_newpart["Manufacture Part Number 1"] = mpnval
            db_newpart["Supplier 1"] = "Digi-Key"
            db_newpart["Supplier Part Number 1"] = dpn
            db_newpart["Tolerance"] = "1%"
            db_newpart["Temperature Range"] = "-55C to 155C"
            db_newpart["Rated Voltage"] = "75VDC"
            db_newpart["Rated Power"] = "0.1W"
            
            

            #Generate our massive string
            cmd = ""
            keylist = db_newpart.keys()
            
            keystr = ", ".join(["[%s]"%k for k in keylist])
            valstr = ", ".join(["'%s'"%db_newpart[k] for k in keylist])
            
            #Check for weird shit
            
            cmd = "INSERT INTO NewAE_IntLib_Test (%s) values (%s)"%(keystr, valstr)
            print cmd
            cur.execute(cmd)

#cur.execute("INSERT INTO NewAE_IntLib_Test ([Part Number], [Value]) values ('pyodbc', '50')")

dbconn.commit()

cur.close()
dbconn.close()
