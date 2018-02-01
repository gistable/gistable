'''

HeapWalker - Walking Windows 7 process heaps using pydbg
Author : Debasish Mandal
Blog :http://www.debasish.in/
Twitter : https://twitter.com/debasishm89

Description : This python script is simplest implementation of Windows HeapWalk() API. 
It uses pydbg and allows user to Walk Through debugee process's heaps on the fly.

In this example

The output of this script will be similar to windbg command "!heap -a 0xMyHeapHandle" command.
           
0:002> !heap -a 00220000
	...
	...
    Heap entries for Segment00 in Heap 00220000
         address: psize . size  flags   state (requested size)
        00220000: 00000 . 00588 [101] - busy (587)
        00220588: 00588 . 00240 [101] - busy (23f)
        002207c8: 00240 . 00020 [101] - busy (18)
        002207e8: 00020 . 00ce0 [101] - busy (cd6)
		..
		And so on.

'''
from pydbg import *
from pydbg.defines import *
from struct import unpack
from struct import pack


def getHeapBlockDetails(dbg,heap_handle, chunk_addr):
	'''
	Return heap block details: state and size
	'''
	xor_res =  unpack('<L',dbg.read_process_memory( heap_handle+0x50, 4 ))[0] ^ unpack('<L',dbg.read_process_memory( chunk_addr, 4 ))[0]
	h = pack('>L',xor_res).encode('hex')
	size = int(h[4:],16)*8
	state_code = int(h[2:4],16)
	if state_code == 1:
		state = "Busy"
	elif state_code == 0:
		state = "Free"
	elif state_code == 9:
		state = "Busy - Internal"
	else:
		state = "Unknown"
	return size,state
def ReadListEntry(dbg,addr):
	'''
	Read and return two dword from any pointer(Mostly Blink of _LIST_ENTRY Linked List). 
	'''
	flink = dbg.read_process_memory( addr, 4 )	# +0x010 SegmentListEntry : _LIST_ENTRY 
	blink = dbg.read_process_memory( addr+4, 4 )
	return flink,blink
def getSegmentsIfAny(dbg,heap_hnd):
	'''
	A bit "hacky" way to find out if the heap has more than one segment in it.
	If it has more than one segment, this function is going to return a list with all segment base address.
	Other wise it will return a list with only item (the same heap handle)
	
	Example : If heap handle is 04c10000,
	
	0:027> dt _LIST_ENTRY 04c10000+0x010
	ntdll!_LIST_ENTRY
	 [ 0x4010010 - 0x4c100a8 ]
	   +0x000 Flink            : 0x04010010 _LIST_ENTRY [ 0x5420010 - 0x4c10010 ]
	   +0x004 Blink            : 0x04c100a8 _LIST_ENTRY [ 0x4c10010 - 0xa100010 ]

	0:027> dt _LIST_ENTRY 0x04c100a8
	ntdll!_LIST_ENTRY
	 [ 0x4c10010 - 0xa100010 ]
	   +0x000 Flink            : 0x04c10010 _LIST_ENTRY [ 0x4010010 - 0x4c100a8 ]
	   +0x004 Blink            : 0x0a100010 _LIST_ENTRY [ 0x4c100a8 - 0x5420010 ]

	And so on...
	'''
	seg_list = []
	first_flink,first_blink = ReadListEntry(dbg,heap_hnd+0x010)#   0xheaphandle+0x010 SegmentListEntry : _LIST_ENTRY 
	if first_flink == first_blink:
		seg_list.append(heap_hnd)
	else:
		# try to find out all available heap segments by iterating through the linked list.
		next_blink = first_blink
		while 1:
			flink , blink = ReadListEntry(dbg,unpack('<L',next_blink)[0])
			# Get the exact segment base
			if flink.encode('hex')[:2] == "10":
				seg_list.append (unpack('<L',flink)[0] - 16)
			'''
			Otherwise this can also be done.
			if unpack('<L',flink)[0] % 16 == 0:	# A nasty hack.
				seg_list.append (unpack('<L',flink)[0] - 16)
			'''
			#print hex(unpack('<L',flink)[0]),hex(unpack('<L',blink)[0])
			if blink == first_blink:
				# Break the loop - End of Linked List (_LIST_ENTRY ) Reached
				break
			next_blink = blink
	return set(seg_list)	# Remove any duplicate value if any
def HeapWalk(dbg):
	print '[+] Address of PEB : ', hex(dbg.peb)
	total_heaps = unpack('<L',dbg.read_process_memory( dbg.peb+0x088, 4 ))[0]	# Total number of process heaps
	print '[+] Total Number of Process Heaps : ', total_heaps
	h_poi = unpack('<L',dbg.read_process_memory( dbg.peb+0x090, 4 ))[0]			# Pointer where all the heap handles are present in memory
	heaps = []
	offset = 0
	# Now we read all the heap handles from memory
	for i in range(1,total_heaps+1):
		heaps.append(  int (hex(unpack('<L',dbg.read_process_memory( h_poi+offset, 4 ))[0]),16)   )
		offset += 4
	# Start iterating through all the heaps
	for heap in heaps:
		print '[+] Walking ',hex(heap)
		# Small check to determine if the heap is LFH
		heap_type = unpack('<L',dbg.read_process_memory( heap+0x0d4, 4 ))[0]
		if heap_type != 0:
			print '[+] Heap type : Low Fragmentation Heap'
		else:
			print '[+] Heap type : Other'
		seg_list = getSegmentsIfAny(dbg,heap)
		if len(seg_list) > 1:
			print '[+] Heap has total',len(seg_list),'segments'
		else:
			print '[+] Heap has only 1 segment'
		for seg in seg_list:
			# Try to iterate through all heaps or heap segments.
			print '[+] Parsing Segment ',hex(seg),'of Heap :',hex(heap)
			next_addr = seg
			# Try to iterate through all the available heap blocks.
			while 1:
				try:
					size,state = getHeapBlockDetails(dbg,heap,next_addr)
					print '\t Heap',hex(heap),'Segment :',hex(seg),'Block :',hex(next_addr),'Size : ', hex(size), 'User Pointer : ',hex(next_addr + 8) ,'(',state,')'
					block_data = dbg.read_process_memory( next_addr+8, size )
					'''
					# Do this when you need to search for string / Unicode string "DEBASISH" in all heap blocks
					if "D\x00E\x00B\x00A\x00S\x00I\x00S\x00H" in block_data:
						print '\t Heap Block : ',hex(next_addr), 'Size : ', hex(size), 'User Pointer : ',hex(next_addr + 8) ,'(',state,')'
					'''
					next_addr = next_addr + size
				except Exception,e:
					print '\t [+] Uncommited Bytes Reached'
					break
	return DBG_CONTINUE

def main():
	dbg = pydbg()
	pid = raw_input ('Enter PID : ')
	dbg.attach(int(pid))
	print '[+] Attached'
	#HeapWalk(dbg)
	try:
		mb = dbg.func_resolve_debuggee('user32.dll','MessageBoxA')
		dbg.bp_set(mb,handler=HeapWalk)
	except Exception,e:
		print '[+] Failed'
	dbg.run()
if __name__ == '__main__':
	main()