#!/usr/bin/env python
import sys
import datetime
frankierart={
	0x01:'Stampit 2003',
	0x02:'0x02???',
	0x03:'Frankit',
	0x05:'Filiale',
	0x07:'Frankierservice Infopost/Infobrief',
	0x08:'Premiumadress',
	0x09:'Pressepost Randbeschriftung 52x52 Module, Version 1',
	0x0c:'Frankit PremA???',
	0x12:'DV-Freimachung',
	0x18:'Elektroreturn',
	0x19:'Pressepost Etikett, Version1',
	0x1a:'Pressepost Randbeschriftung 16x28 Module, Version 1',
	0x1c:'Premiumadress Label',
	0x30:'Plusbrief',
	0x33:'Stampit',
	0x30:'Plusbrief individuell',
	0x42:'Plusbrief/Marke individuell',
	0x4d:'Handyporto?',
	0x52:'Elektroreturn',
	0x66:'Handyporto?',
	#0x33:'Marke individuell',
	0x85:'Internetmarke'
	
}
productid={
	1:'Standardbrief',
	2:'Standardbrief Einschreiben Einwurf',
	7:'Standardbrief Einschreiben',
	8:u'Standardbrief Einschreiben + R\xfcckschein',
	9:u'Standardbrief Einschreiben + Eigenh\xe4ndig',
	10:u'Standardbrief Einschreiben + Eigenh\xe4ndig + R\xfcckschein',
	11:'Kompaktbrief',
	21:u'Gro\xdfbrief',
	32:'Maxibrief',
	51:'Postkarte',
	76:u'B\xfcchersendung Standard',
	77:u'B\xfcchersendung Kompakt',
	78:u'B\xfcchersendung Gro\xdf',
	79:u'B\xfcchersendung Maxi',
	80:u'Warensendung Standard',
	81:u'Warensendung Kompatk',
	82:u'Warensendung Maxi',
	83:u'Warensendung Standard',
	80:u'Warensendung Standard',
	
	86:'Infobrief/Katalog Standard',
	87:'Infobrief/Katalog Kompakt',
	88:u'Infobrief/Katalog Gro\xdf',
	89:'Infobrief/Katalog Maxi',
	90:'Infopost/Katalog',
	450:'Pressesendung E+0',
	451:'Pressesendung E+1',
	452:'Pressesendung E+2',
	453:'Postvertriebsstk. E+0',
	454:'Postvertriebsstk. E+1',
	455:'Postvertriebsstk. E+2',
	3106:'Infopost/Katalog Kompakt',
	3101:'Infopost/Katalog Kompakt >20g',
	3107:u'Infopost/Katalog Gro\xdf',
	3108:u'Infopost/Katalog Maxi',
	3104:u'Infopost/Katalog Maxi >20g',
	3105:u'Infopost/Katalog Maxi >100g',
	9001:'Standardbrief PremA',
	9279:'Pressesendung E+0 PremA',
	9280:'Pressesendung E+1 PremA',
	9287:'Pressesendung E+2 PremA'
}
frankmaschmanuf={
	0x1d:'Neopost',
	0x2d:'Frama',
	0x3d:'Francotyp-Postalia',
	0x4d:'Pitney Bowes',
	0x6d:'Telefrank'}
# Write a Data Matrix barcode
#dm_write = DataMatrix()
#dm_write.encode("Hello, world!")
#dm_write.save("hello.png", "png")

def decodedm(str1):
	print len(str1)
	print str1.encode('hex')
	if str1.startswith('DEA'):
		frankierartnum=ord(str1[3])
		frankierartname=frankierart.get(frankierartnum)
		print 'Frankierart %d %s'%(frankierartnum,frankierartname)
		if frankierartnum == 0x07:
			print 'Briefzentrum %d' % ord(str1[4])
		if frankierartnum != 0x1c:
			proid=ord(str1[14])*2**8+ord(str1[15]) 
			print 'Produkt-ID %d %s'%(proid,productid.get(proid))
		if frankierartnum == 0x03 or frankierartnum ==5:
			print 'Frankierwert %d Eurocent'%(
			ord(str1[10])*2**8+ord(str1[11]) )
		if frankierartnum == 0x85:
			print 'Kundennummer %s'%str1[9:14].encode('hex')
			num=ord(str1[4])*2**32+ord(str1[5])*2**24+\
				ord(str1[6])*2**16+ord(str1[7])*2**8+\
				ord(str1[8])
			print'Fortlaufende Nummer (dez) %d' %num
		if frankierartnum == 0x03 or frankierartnum == 0x19 or\
		frankierartnum == 0x1a or frankierartnum == 0x09  or\
		frankierartnum == 0x0c or frankierartnum == 0x05:
			datein=ord(str1[12])*2**8+ord(str1[13]) 
			year=datein%100+2000
			day=datein/100
			date=datetime.date.fromordinal(datetime.date(year,1,1).toordinal()-1+day)
			print 'Einlieferungsdatum: %s'% date.strftime('%a %d.%m.%Y')			
		if frankierartnum == 0x03 or frankierartnum == 0x33:
			
			print 'Preisliste %d' % ord(str1[4])
			frankmasch=str1[5:10].encode('hex')
			print 'Frankiermaschine %s Hersteller %s'%(frankmasch,\
			frankmaschmanuf.get(int(frankmasch[0:2],16)))
			
		if str1[3]=='\x19' or str1[3]=='\x1A' or str1[3]=='\x09':
			print 'Zeitungskennziffer %d'%(
			(ord(str1[5])*2**16+ord(str1[6])*2**8 +ord(str1[7])) )
			#print str1[5:8].encode('hex')
			#print 'Zeitungskennziffer %d'% int(str1[5:8],256)
			print 'Heftnummer %d'%(
			ord(str1[8])*2**8+ord(str1[9]) )
			print 'Premiumaddress-ID %d'%(
			ord(str1[16])*2**8+ord(str1[17]) )
			print 'Abonentennummer %s' % str1[18:42]
			if str1[3]=='\x19' or str1[3]=='\x09':
				print 'PLZ Ort %d %s'%((ord(str1[42])*2**16+\
				ord(str1[43])*2**8 +ord(str1[44])),\
				str1[45:69].strip())
				print  u'Stra\xdfe %s' % str1[69:91]
				print 'Hausnummer %s' % str1[91:101]
				print 'Name1 %s' % str1[101:131]
				print 'Name2 %s' % str1[131:161]
				print 'Name3 %s' % str1[161:191]
				print 'Kd-Inv Info %s' % str1[191:202].strip()
			elif str1[3]=='\x1A':
				print 'Kd-Inv Info %s' % str1[42:47]
			#print 'Referenz %s' % str1[0x12:]
		
	else:
		print str1;

# Read a Data Matrix barcode
def handleargc():
	for filename in sys.argv[1:]:
		if filename.endswith('.bin'):
			decodedm(str1=open(filename,'rb').read())
		else:
        		from pydmtx import DataMatrix
		        from PIL import Image
			dm_read = DataMatrix()
			img = Image.open(sys.argv[1])

			dm_read.decode(img.size[0], img.size[1], buffer(img.tostring()))
			#print dm_read.count()
			#print dm_read.stats(1)
			decodedm(dm_read.message(1))

try:
	import android
	droid = android.Android()
	code = droid.scanBarcode()
	str2=code.result['extras']['SCAN_RESULT']
	if True: #procedute to identify hex encoding
		decodedm(str2.replace(' ','').decode('hex'))
except ImportError:
	if len(sys.argv) == 1:
		decodedm(raw_input())
	else:
		handleargc()