# auto_o.py by Kenny @octosavvi
# IDA Pro should treat immediate operands as offsets whenever possible.
#
# To use, create a system alias which adds -S"auto_o.py" to your ida
# commandline.  Place this file anywhere your idapythonrc.py path allows.

Message("Loading auto_o\n")

def auto_o():
  Wait()
  try:
    dataSeg # is only defined when a database is created
  except NameError:
    # Don't muck with an existing database
    return
  
  ds = dataSeg()
  re_im = re.compile('^(#\d|0x)')
  Message("Running auto_o\n")
  # For each of the segments
  for seg_ea in Segments():
    # For each of the defined elements
    for head in Heads(seg_ea, SegEnd(seg_ea)):
      # If it's an instruction and has Immediate Operand
      if isCode(GetFlags(head)) and GetOpType(head, 1) == 5:
        # Try setting it to an Offset
        OpOff(head, 1, ds)
        # If it still looks like an Immediate value
        if re_im.match(GetOpnd(head, 1)):
          # Set it back to a Number
          OpNumber(head, 1)

auto_o()