# IDA .fds Loader

# usage:
# 1. Place into $IDA/loader/
# 2. Open .fds file by IDA (select "Python FDS Loader")
# 3. "import fds; fds.add()" and select additional file
# Enjoy!

# reference:
# http://park19.wakwak.com/~fantasy/fds/

import idaapi
import struct

class Struc:
	def __init__(self, pairs):
		"""
		struc = Struc([["8s","name"],["B","id"],...])
		"""
		self.fmt = "".join(map(lambda e:e[0],pairs))
		self.keys = map(lambda e:e[1],pairs)
	def read(self, li):
		"""
		dict = struc.read(li)
		"""
		#print "reading fmt " + self.fmt
		values = struct.unpack(self.fmt, li.read(struct.calcsize(self.fmt)))
		self.dict = {}
		for i in xrange(len(self.keys)):
			self.dict[self.keys[i]] = values[i]
		return self.dict

class QuickDisk:
	def __init__(self, li):
		# IMPORTANT! seek to head!
		li.seek(0)
		# load files
		signat = li.read(4)
		if signat != "FDS\x1a":
			print "WARNING: FDS without ident? (%s)" % signat
		total_sides = struct.unpack("B", li.read(1))
		li.read(0x10 - 4 - 1)

		self.files = []
		self.bootno = []

		vlabel = None
		filecnt = None
		pblkcode = None
		nowfilecnt = 0

		# support both IDA-linput and Python-File
		filesize = 0
		try:
			filesize = li.size()
		except:
			ptell = li.tell()
			li.seek(0, 2) # TODO 2!? no SEEK_END!?
			filesize = li.tell()
			li.seek(ptell)

		while True:
			if filesize <= li.tell():
				break
			if filecnt != None and filecnt <= nowfilecnt:
				# next side
				li.seek(((li.tell() - 0x10 + (65500-1)) / 65500) * 65500 + 0x10)
				nowfilecnt = 0
				if filesize <= li.tell():
					break
			side = (li.tell() - 0x10) / 65500
			if total_sides < side:
				print "WARNING: unexpected tail data"
				total_sides = side
			blkcode = struct.unpack("B", li.read(1))[0]
			if blkcode == 0:
				# tail or gap??
				pass
			elif blkcode == 1:
				# volume label
				vlabel = Struc([
					["14s", "chkcode"],
					["B",   "maker"],
					["4s",  "gamename"],
					["B",   "gamever"],
					["B",   "diskside"],
					["B",   "diskno"],
					["B",   "disktype"],
					["B",   "unk1"],
					["B",   "bootno"],
					["5s",  "unk2"],
					["3s",  "date"],
					["B",   "unk3"],
					["B",   "unk4"],
					["H",   "writerid"], # TODO something goes wrong?
					["B",   "unk5"],
					["B",   "rewritecnt"],
					["B",   "real_diskside"],
					["B",   "unk6"],
					["B",   "crc"],
					["12s", "no_doced"],
					]).read(li)
				#print "vlabel>>>",vlabel
				filecnt = None
				self.bootno.append(vlabel["bootno"])
			elif blkcode == 2:
				# file count
				filecnt = struct.unpack("B", li.read(1))[0]
				#print "fcount>>>",filecnt
			elif blkcode == 3:
				# file header
				header = Struc([
					["B",  "seqno"],
					["B",  "ldno"],
					["8s", "name"],
					["H",  "addr"],
					["H",  "size"],
					["B",  "target"],
					]).read(li)
				header["side"] = side
				header["side_str"] = chr(ord("A") + side)
				header["boot"] = (header["ldno"] <= vlabel["bootno"])
				#print header
				self.files.append(header)
				# TODO check seqno sequence, check seqno < filecnt
			elif blkcode == 4:
				if pblkcode != 3:
					print "WARNING: blkcode %X -> 4" % (pblkcode,)
				# file data
				file = self.files[-1]
				file["offset"] = li.tell()
				file["data"] = li.read(file["size"])
				nowfilecnt += 1
			else:
				# tell-1 = &blkcode
				print "offset %X blkcode %X?" % (li.tell() - 1, blkcode)
			pblkcode = blkcode

	#def files():
	#	return self.files

class FileSelector(idaapi.Choose2):
	def __init__(self, li):
		title = "Choose a file from FDS FileList"
		cols = [
			["Offset",    5 | idaapi.Choose2.CHCOL_HEX],
			["Side",      2 | idaapi.Choose2.CHCOL_PLAIN],
			["SeqNo",     2 | idaapi.Choose2.CHCOL_HEX],
			["LoadNo",    2 | idaapi.Choose2.CHCOL_HEX],
			["Filename", 10 | idaapi.Choose2.CHCOL_PLAIN],
			["Addr",      4 | idaapi.Choose2.CHCOL_HEX],
			["Size",      4 | idaapi.Choose2.CHCOL_HEX],
			["Target",    2 | idaapi.Choose2.CHCOL_HEX],
			]
		idaapi.Choose2.__init__(self, title, cols)

		files = QuickDisk(li).files
		#files = filter(lambda x:x["target"] == 0, files)	# TODO filter: only texts?
		self.files = files

	def OnGetSize(self):
		return len(self.files)
	def OnGetLine(self, n):
		file = self.files[n]
		return [
			hex(file["offset"]),
			file["side_str"] + ("*" if file["boot"] else ""),
			hex(file["seqno"]),
			hex(file["ldno"]),
			file["name"],
			hex(file["addr"]),
			hex(file["size"]),
			hex(file["target"]),
			]
	def OnClose(self):
		pass
	def show(self):
		i = self.Show(True)
		if i == -1:
			return None
		else:
			return self.files[i]

def accept_file(li, n):
	if n > 0:
		return 0

	if li.read(4) != "FDS\x1a":
		return 0

	return "Python FDS Loader"

def make_io():
	# TODO make name to io-port... and DISK-BIOS functions?
	idaapi.add_segm(0, 0x0000, 0x0800, "RAM", "DATA")
	idaapi.add_segm(0, 0x2000, 0x2008, "PPU", "DATA")
	idaapi.add_segm(0, 0x4000, 0x4018, "CPU", "DATA")
	idaapi.add_segm(0, 0x4022, 0x408B, "DISKIO", "DATA")
	#idaapi.add_segm(0, 0x4100, 0x6000, "EXT", "DATA") # non-need?
	#idaapi.add_segm(0, 0xE000, 0x10000, "BIOS", "UNK") # add BIOS image by yourself...

def load_file(li, neflags, format):
	if format != "Python FDS Loader":
		return 0

	# 6502 (2A03 is best)
	idaapi.set_processor_type("M6502", SETPROC_ALL|SETPROC_FATAL)

	# try to user to be choose?
	#return add_li(li)

	# or autoload boot-files?
	# only see side-A.
	qd = QuickDisk(li)
	for file in filter(lambda f:f["target"] == 0 and f["ldno"] <= qd.bootno[0], qd.files):
		load_li(li, file)

	make_io()

	return 1

def make_offs_name(ea, name):
	idaapi.set_name(ea, name)
	idaapi.doWord(ea, 2)
	idaapi.set_offset(ea, 0, 0)

def load_li(li, file):
	# file2base(li,pos,ea1,ea2,patchable) FILEREG_NOTPATCHABLE
	# mem2base(mem,ea,fpos)
	#idaapi.file2base(li, file["offset"], file["addr"], file["addr"]+file["size"], idaapi.FILEREG_NOTPATCHABLE)
	#idaapi.mem2base(file["data"], file["addr"], file["addr"]+file["size"], file["offset"])

	# TODO I want to make segment type "CODE" but IDA tries to analysis...
	idaapi.add_segm(0, file["addr"], file["addr"]+file["size"], "%s%X" % (file["side_str"], file["seqno"]), "UNK")
	idaapi.mem2base(file["data"], file["addr"], file["offset"])

	# special-handling: vectors
	if file["addr"] <= 0xDFFA and 0xDFFF <= file["addr"]+file["size"]:
		make_offs_name(0xDFFA, "NMIVEC")
		make_offs_name(0xDFFC, "RSTVEC")
		make_offs_name(0xDFFE, "IRQVEC")

def add_li(li):
	"""
	@hide
	"""
	file = FileSelector(li).show()
	if file == None:
		return 0

	load_li(li, file)

	return 1

def add():
	"""
	user accessible API.
	fds.add()
	"""

	f = None
	try:
		f = open(idaapi.get_input_file_path(), "rb")
	except IOError:
		print "fds: Can't open input file."
		return 0
	r = add_li(f)
	f.close()

	return r
