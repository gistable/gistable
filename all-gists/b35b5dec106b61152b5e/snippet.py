print "--"
print "Renaming Hooks for Current Procedure..."
print "Message from rpetrich: Please use this for good and not evil"
print "--"

doc = Document.getCurrentDocument()

def procedure_end(seg, proc):
	addr = proc.getEntryPoint()
	currentIndex = seg.getProcedureIndexAtAddress(addr)
	nextIndex = currentIndex
	while nextIndex == currentIndex:
		addr = addr + 2
		if seg.getTypeAtAddress(addr) == Segment.TYPE_PROCEDURE:
			currentIndex = seg.getProcedureIndexAtAddress(addr)
	#print Segment.stringForType(seg.getTypeAtAddress(addr))
	#print hex(addr)
	return addr

def read_string(seg, addr):
	result = ""
	byte = seg.readByte(addr)
	while (byte != 0):
		result = result + chr(byte & 0xff)
		addr = addr + 1
		byte = seg.readByte(addr)
	return result

pending_string = None
pending_class = None
pending_int = None
pending_selector = None
pending_proc = None
pending_getinstance_method = False

seg = doc.getCurrentSegment()
proc = seg.getProcedureAtAddress(doc.getCurrentAddress())
start = proc.getEntryPoint()
end = procedure_end(seg, proc)
for addr in range(start, end):
	for ref in seg.getReferencesFromAddress(addr):
		ref_seg = doc.getSegmentAtAddress(ref)
		ref_name = ref_seg.getNameAtAddress(ref)
		if (ref_name is None):
			ref_type = ref_seg.getTypeAtAddress(ref)
			if ref_type == Segment.TYPE_ASCII:
				pending_string = read_string(ref_seg, ref)
				#print hex(addr) + "->" + hex(ref)
				#print "\"" + pending_string + "\""
			elif ref_type == Segment.TYPE_INT:
				pending_int = ref_seg.readUInt32LE(ref)
				#print hex(addr) + "->" + hex(ref) + " = " + hex(pending_int)
				sel_seg = doc.getSegmentAtAddress(pending_int)
				if not sel_seg is None:
					pending_selector = read_string(sel_seg, pending_int)
					#print "@selector(" + pending_selector + ")"
				else:
					print pending_int
			elif ref_type == Segment.TYPE_NEXT:
				if ref_seg.getTypeAtAddress(ref - 1) == Segment.TYPE_PROCEDURE:
					pending_proc = ref - 1
					#print "sub_" + hex(pending_proc)
			#else:
				#print hex(addr) + "->" + hex(ref) + " is " + Segment.stringForType(ref_type)
		else:
			#print hex(addr) + "->" + hex(ref) + " as " + str(ref_name)
			ref_name = str(ref_name)
			if (ref_name == "imp___symbolstub1__objc_getClass") or (ref_name == "imp___picsymbolstub4__objc_getClass"):
				if not pending_string is None:
					pending_class = pending_string
					print "objc_getClass(\"" + str(pending_string) + "\")"
					pending_getinstancemethod = False
			elif (ref_name == "imp___symbolstub1__MSHookMessageEx") or (ref_name == "imp___picsymbolstub4__MSHookMessageEx"):
				if (not pending_class is None) and (not pending_proc is None) and (not pending_selector is None):
					doc.getSegmentAtAddress(pending_proc).setNameAtAddress(pending_proc, "hook: -[" + pending_class + " " + pending_selector + "]")
					print "MSHookMessageEx(" + pending_class + ", " + pending_selector + ", " + hex(pending_proc) + ")"
					pending_getinstancemethod = False
			elif (ref_name == "imp___symbolstub1__class_addMethod") or (ref_name == "imp___picsymbolstub4__class_addMethod"):
				if (not pending_class is None) and (not pending_proc is None) and (not pending_selector is None):
					if pending_getinstancemethod:
						prefix = "hook"
					else:
						prefix = "new"
					doc.getSegmentAtAddress(pending_proc).setNameAtAddress(pending_proc, prefix + ": -[" + pending_class + " " + pending_selector + "]")
					print "class_addMethod(" + pending_class + ", " + pending_selector + ", " + hex(pending_proc) + ")"
					pending_getinstancemethod = False
			elif (ref_name == "imp___picsymbolstub4__method_setImplementation"):
				if (not pending_class is None) and (not pending_proc is None) and (not pending_selector is None):
					prefix = "hook"
				doc.getSegmentAtAddress(pending_proc).setNameAtAddress(pending_proc, prefix + ": -[" + pending_class + " " + pending_selector + "]")
				print "method_setImplementation(class_getInstanceMethod(" + pending_class + ", " + pending_selector + "), " + hex(pending_proc) + ")"
				pending_getinstancemethod = False
			elif (ref_name == "imp___symbolstub1__class_getInstanceMethod") or (ref_name == "imp___picsymbolstub4__class_getInstanceMethod"):
				pending_getinstancemethod = True
			else:
				pending_proc = ref
