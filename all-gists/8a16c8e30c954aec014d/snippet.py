import idaapi
import idc
#import idautils
import sys

#NOTE: may have to run this a few times to get to the end of the IDB, haven't bothered fixing this

def add_struct_to_idb(name):
	idc.Til2Idb(-1, name)


def find_or_create_struct(name):
	sid = idc.GetStrucIdByName(name)
	if sid == idc.BADADDR:
		sid = idc.AddStrucEx(-1, name, 0)
		print "added struct \"{0}\", id: {1}".format(name, sid)
	else:
		print "struct \"{0}\" already exists, id: ".format(name, sid)
	
	add_struct_to_idb(name)
	
	return sid


def create_CFLString_struct():
	sid = find_or_create_struct("CFLString")
	print idc.AddStrucMember(sid, "magic", -1, idc.FF_DWRD, -1, 4)
	print idc.AddStrucMember(sid, "unk4", -1, idc.FF_DWRD, -1, 4)
	print idc.AddStrucMember(sid, "cstr", -1, idc.FF_BYTE, -1, 0)
	
	return sid


def apply_struct(ea, sid, size):
	if size == -1:
		size = idc.GetStrucSize(sid)
	
	idc.MakeUnknown(ea, size, idc.DOUNK_DELNAMES)
	
	idaapi.doStruct(ea, size, sid)
	
	return size


def main():
	CFLString_sid = create_CFLString_struct()
	
	# limit search to .rodata
	seg_sel = idc.SegByName(".rodata")
	ea = idc.SegByBase(seg_sel)
	end_ea = idc.SegEnd(ea)
	
	while ea < end_ea:
		#find all instances of magic==0x756 and unk4==0x7FFFFFFF
		if (idc.Dword(ea), idc.Dword(ea + 4)) == (0x756, 0x7FFFFFFF):
			# read bytes until NULL is found
			index = 0
			cstr  = ""
			while True:
				char = chr(idc.Byte(ea + 8 + index))
				if char == "\x00":
					break
				index += 1
				cstr  += char
			
			name_str = cstr
			for bad_char in ["-", ":", ";", "=", "(", ")", " ", "/", "\\", "<", ">"]:
				name_str = name_str.replace(bad_char, "_")
			
			#XXX: lazy/unreliable way to deal with name collisions
			suffix = 0
			while not idc.MakeNameEx(ea, "cflstr_{0}__{1}".format(name_str, suffix), idc.SN_CHECK | idc.SN_NOWARN):
				suffix += 1
				# something probably went horribly wrong
				if suffix > 100:
					print "error creating name at address {0}".format(hex(ea))
					sys.exit(1)
			
			# size = magic + unk4 + string_length + NULL_byte
			print "applying at {0}".format(hex(ea))
			struct_size = apply_struct(ea, CFLString_sid, 8 + len(cstr) + 1)
			
			# preserve alignment
			ea += (struct_size & ~3)
		else:
			ea += 4


if __name__ == "__main__":
	main()
