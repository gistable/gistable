if 64 - 64: i11iIiiIii
if 65 - 65: O0 / iIii1I11I1II1 % OoooooooOO - i1IIi
if 73 - 73: II111iiii
if 22 - 22: I1IiiI * Oo0Ooo / OoO0O00 . OoOoOO00 . o0oOOo0O0Ooo / I1ii11iIi11i
import os
if 48 - 48: oO0o / OOooOOo / I11i / Ii1I
if 48 - 48: iII111i % IiII + I1Ii111 / ooOoO0o * Ii1I
if 46 - 46: ooOoO0o * I11i - OoooooooOO
if 30 - 30: o0oOOo0O0Ooo - O0 % o0oOOo0O0Ooo - OoooooooOO * O0 * OoooooooOO
if 60 - 60: iIii1I11I1II1 / i1IIi * oO0o - I1ii11iIi11i + o0oOOo0O0Ooo
if 94 - 94: i1IIi % Oo0Ooo
import sys
import re
import hashlib
import csv
import time
import locale
import getopt
if 68 - 68: Ii1I / O0
def Iiii111Ii11I1 ( ) :
 os . popen ( 'adb root' ) . close ( )
 if 66 - 66: iII111i
 if 30 - 30: iIii1I11I1II1 * iIii1I11I1II1 . II111iiii - oO0o
 if 72 - 72: II111iiii - OoOoOO00
 if 91 - 91: OoO0O00 . i11iIiiIii / oO0o % I11i / OoO0O00 - i11iIiiIii
 II1Iiii1111i = os . popen ( 'adb shell ls /data/data/com.tencent.mm/MicroMsg/*/EnMicroMsg.db' ) . read ( )
 return II1Iiii1111i . splitlines ( ) [ - 1 ] if II1Iiii1111i else ''
 if 25 - 25: Ii1I
def oo00000o0 ( ) :
 os . popen ( 'adb root' ) . close ( )
 if 34 - 34: IiII % II111iiii % iIii1I11I1II1 % IiII * iII111i / OoOoOO00
 if 31 - 31: i11iIiiIii / I1IiiI / ooOoO0o * oO0o / Oo0Ooo
 II1Iiii1111i = os . popen ( 'adb shell cat /data/data/com.tencent.mm/shared_prefs/system_config_prefs.xml' ) . read ( )
 Oo0o0ooO0oOOO = re . findall ( 'name="default_uin" value="([0-9]+)"' , II1Iiii1111i )
 return Oo0o0ooO0oOOO [ 0 ] if Oo0o0ooO0oOOO else 0
 if 58 - 58: i11iIiiIii % I1Ii111
def O0OoOoo00o ( ) :
 II1Iiii1111i = os . popen ( 'adb shell dumpsys iphonesubinfo' ) . read ( )
 if 31 - 31: II111iiii + OoO0O00 . I1Ii111
 if 68 - 68: I1IiiI - i11iIiiIii - OoO0O00 / OOooOOo - OoO0O00 + i1IIi
 IiiIII111ii = re . findall ( 'Device ID = ([0-9]+)' , II1Iiii1111i )
 return IiiIII111ii [ 0 ] if IiiIII111ii else 0
 if 3 - 3: iII111i + O0
def I1Ii ( ) :
 Oo0o0ooO0oOOO = oo00000o0 ( )
 if 66 - 66: Ii1I
 if 78 - 78: OoO0O00
 IiiIII111ii = O0OoOoo00o ( )
 if Oo0o0ooO0oOOO and IiiIII111ii :
  return hashlib . md5 ( IiiIII111ii + Oo0o0ooO0oOOO ) . hexdigest ( ) [ 0 : 7 ]
 return ''
 if 18 - 18: O0 - iII111i / iII111i + ooOoO0o % ooOoO0o - IiII
 if 62 - 62: iII111i - IiII - OoOoOO00 % i1IIi / oO0o
def OoooooOoo ( msgcsv ) :
 locale . setlocale ( locale . LC_ALL , '' )
 if 70 - 70: OoO0O00 . OoO0O00 - OoO0O00 / I1ii11iIi11i * OOooOOo
 if 86 - 86: i11iIiiIii + Ii1I + ooOoO0o * I11i + o0oOOo0O0Ooo
 if 61 - 61: OoO0O00 / i11iIiiIii
 if 34 - 34: OoooooooOO + iIii1I11I1II1 + i11iIiiIii - I1ii11iIi11i + i11iIiiIii
 if hasattr ( msgcsv , 'title' ) :
  msgcsv = [ ooOoo0O + '\n' for ooOoo0O in msgcsv . splitlines ( ) ]
  pass
 OooO0 = csv . reader ( msgcsv )
 OooO0 . next ( )
 for ooOoo0O in OooO0 :
  try :
   II11iiii1Ii , OO0o , Ooo , O0o0Oo , Oo00OOOOO , O0O , O00o0OO , I11i1 , iIi1ii1I1 , o0 , I11II1i , IIIII = ooOoo0O [ : 12 ]
   pass
  except :
   continue
  ooooooO0oo = 'me' if ( Oo00OOOOO == '1' ) else I11i1
  IIiiiiiiIi1I1 = time . localtime ( int ( O00o0OO ) / 1000 )
  I1IIIii = time . strftime ( "%Y-%m-%d %a %H:%M:%S" , IIiiiiiiIi1I1 )
  yield [ I11i1 , I1IIIii , ooooooO0oo , iIi1ii1I1 , o0 ]
  pass
 pass
 if 95 - 95: OoO0O00 % oO0o . O0
def I1i1I ( chat ) :
 oOO00oOO = { }
 if 75 - 75: i1IIi / OoooooooOO - O0 / OoOoOO00 . II111iiii - i1IIi
 if 71 - 71: OOooOOo + Ii1I * OOooOOo - OoO0O00 * o0oOOo0O0Ooo
 for I11i1 , I1IIIii , ooooooO0oo , iIi1ii1I1 , o0 in chat :
  oOO00oOO [ I11i1 ] = 1
  pass
 return oOO00oOO . keys ( )
 if 65 - 65: O0 % I1IiiI . I1ii11iIi11i % iIii1I11I1II1 / OOooOOo % I1Ii111
def oo ( chat , name = '' ) :
 II1Iiii1111i = [ ]
 if 44 - 44: O0 / ooOoO0o
 if 84 - 84: ooOoO0o * II111iiii % Ii1I . OoOoOO00
 name = name . lower ( )
 for I11i1 , I1IIIii , ooooooO0oo , iIi1ii1I1 , o0 in chat :
  iIi1ii1I1 = iIi1ii1I1 . replace ( '\n' , '\n  ' )
  o0 = ( '\t' + o0 ) if o0 else ''
  if not name :
   II1Iiii1111i . append ( '%s: %s %s: %s %s' % ( I11i1 , I1IIIii , ooooooO0oo , iIi1ii1I1 , o0 ) )
   pass
  elif I11i1 . lower ( ) == name :
   II1Iiii1111i . append ( '%s %s: %s %s' % ( I1IIIii , ooooooO0oo , iIi1ii1I1 , o0 ) )
   pass
  pass
 return '\n' . join ( II1Iiii1111i ) + '\n'
 if 66 - 66: I1ii11iIi11i / OoOoOO00 - I1IiiI . OOooOOo / I1IiiI * OOooOOo
def IIIii1II1II ( dbn , key = '' ) :
 i1I1iI , oo0OooOOo0 = os . popen2 ( [ 'sqlcipher' , dbn ] )
 if 92 - 92: iII111i . I11i + o0oOOo0O0Ooo
 if 28 - 28: i1IIi * Oo0Ooo - o0oOOo0O0Ooo * IiII * Ii1I / OoO0O00
 if key :
  i1I1iI . write ( 'PRAGMA key=%s;\n' % ` key ` )
  i1I1iI . write ( 'pragma cipher_use_hmac=off;\n' )
  pass
 i1I1iI . write ( '.tables\n' )
 i1I1iI . close ( )
 return oo0OooOOo0 . read ( ) . split ( )
 if 94 - 94: II111iiii % I1ii11iIi11i / OoOoOO00 * iIii1I11I1II1
def oOOoo0Oo ( dbn , key = '' , table = 'message' ) :
 table = table or 'message'
 if 78 - 78: I11i
 if 71 - 71: OOooOOo + ooOoO0o % i11iIiiIii + I1ii11iIi11i - IiII
 i1I1iI , oo0OooOOo0 = os . popen2 ( [ 'sqlcipher' , dbn ] )
 i1I1iI . write ( '.header on\n' )
 i1I1iI . write ( '.mode csv\n' )
 if key :
  i1I1iI . write ( 'PRAGMA key=%s;\n' % ` key ` )
  i1I1iI . write ( 'pragma cipher_use_hmac=off;\n' )
  pass
 i1I1iI . write ( 'select * from %s;\n' % ` table ` )
 i1I1iI . close ( )
 return oo0OooOOo0 . read ( )
 if 88 - 88: OoOoOO00 - OoO0O00 % OOooOOo
 if 16 - 16: I1IiiI * oO0o % IiII
def Oo000o ( names = [ ] ) :
 I11IiI1I11i1i = 'EnMicroMsg.db'
 iI1ii1Ii = 'message.csv'
 oooo000 = Iiii111Ii11I1 ( )
 iIIIi1 = I1Ii ( )
 os . popen ( 'adb wait-for-device' )
 os . popen ( 'adb pull %s %s' % ( ` oooo000 ` , ` I11IiI1I11i1i ` ) ) . close ( )
 iiII1i1 = oOOoo0Oo ( I11IiI1I11i1i , iIIIi1 )
 if iiII1i1 . find ( '\n' ) < 0 :
  return 1
 file ( iI1ii1Ii , 'w' ) . write ( iiII1i1 )
 o00oOO0o = list ( OoooooOoo ( iiII1i1 ) )
 if not o00oOO0o :
  return 1
 if not names :
  names = I1i1I ( o00oOO0o )
  pass
 for OOO00O in names :
  OOoOO0oo0ooO = 'message.%s.txt' % OOO00O
  II1Iiii1111i = oo ( o00oOO0o , OOO00O )
  if len ( II1Iiii1111i ) > 4 :
   file ( OOoOO0oo0ooO , 'w' ) . write ( II1Iiii1111i )
   pass
  pass
 pass
 if 98 - 98: iII111i * iII111i / iII111i + I11i
ii111111I1iII = '''Usage: wechat2txt.py [OPTIONS] [NAME]...

OPTIONS:
    -h        display this help and exit
'''
if 68 - 68: iII111i - iIii1I11I1II1 * i11iIiiIii / I1ii11iIi11i * I1Ii111
def i1iIi1iIi1i ( ) :
 try :
  I1I1iIiII1 , i11i1I1 = getopt . getopt ( sys . argv [ 1 : ] , 'h' )
 except getopt . error , ii1I :
  print ii111111I1iII
  return 1
 for Oo0ooOo0o , Ii1i1 in I1I1iIiII1 :
  if Oo0ooOo0o == '-h' :
   print ii111111I1iII
   return 1
  pass
 oOO00oOO = i11i1I1
 II1Iiii1111i = Oo000o ( oOO00oOO )
 return not II1Iiii1111i
 if 15 - 15: II111iiii
if __name__ == "__main__" :
 sys . exit ( i1iIi1iIi1i ( ) )
 if 18 - 18: i11iIiiIii . i1IIi % OoooooooOO / O0
