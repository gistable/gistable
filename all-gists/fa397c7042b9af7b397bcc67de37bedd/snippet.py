for seg_ea in Segments():
    for ea in Heads(seg_ea, SegEnd(seg_ea)):
        if isCode(GetFlags(ea)):
        
            n = 0
            while n < 6:
                t = GetOpType(ea, n)
                
                if (t == -1):
                    break

                if (t == o_displ) and (GetOpnd(ea, n).find('(a6)') != -1):
                    OpOff(ea, n | OPND_OUTER, 0xFF0000)
                
                n += 1
                
print "Done!"