import idaapi
import idautils
import sys
import itertools

def rename_functions_ida():
  #Get number of segments
  seg=idaapi.getnseg(0)
  if seg:
  #Get list of functions in that segment
    funcs=idautils.Functions(seg.startEA, seg.endEA)
    for funcaddress in funcs:
      f_name= GetFunctionName(funcaddress)
      if f_name == 'giant_keyloggercase_structure':
        for address in Heads(funcaddress, FindFuncEnd(funcaddress)):
          if GetMnem(address) == 'call':
            t1= GetOpnd(address, 0)
            if t1.startswith('sub_'):
              t2= t1.split('_')
              MakeNameEx(int(t2[1], 16),"keylog_charbychar_"+t2[1],SN_NOWARN)
 
#Wait for analysis to complete
idaapi.autoWait()

#Get existing functions from IDA
rename_functions_ida()

#Exit IDA
idc.Exit(0)