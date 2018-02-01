import idc

def decrypt_n_comment(func, func_name):
	"""
	Decrypt and comment Shamoon2's strings
	"""
	data = {}

	for xref in XrefsTo(LocByName(func_name)):
		# init
		string_ea = search_inst(xref.frm, "push")
		string_op = GetOperandValue(string_ea,0)
		key_ea = PrevHead(string_ea)
		key_op = GetOperandValue(key_ea,0)

		# Call shamoon2's func
		res = func(string_op, key_op)

		# Refresh the memory for GetString function
		idc.RefreshDebuggerMemory()
		
		try:
		    # Add comments
		    MakeComm(string_ea, "key[0x{:X}] : '{:s}'".format(key_op, GetString(res,-1,ASCSTR_UNICODE))) 
		except:
			continue

def search_inst(ea, inst):
	"""
	Find first instruction before the given ea
	"""
	while True:
		if GetMnem(ea) == inst:
			return ea
		ea = PrevHead(ea)

# Initialization ------------------------------------------
FUNC_NAME = "getStringW"

# Execution -----------------------------------------------
decrypt_function = Appcall[FUNC_NAME]

decrypt_n_comment(decrypt_function, FUNC_NAME)