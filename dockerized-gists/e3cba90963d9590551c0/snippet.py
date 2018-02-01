#!/usr/bin/python2
#coding: utf-8
 
#这个函数是从网上摘的
def is_zh (c):
	try:
		x = ord (c)
	except:
		return False
	# Punct & Radicals
	if x >= 0x2e80 and x <= 0x33ff:
		return True
 
	# Fullwidth Latin Characters
	elif x >= 0xff00 and x <= 0xffef:
		return True
 
	# CJK Unified Ideographs &
	# CJK Unified Ideographs Extension A
	elif x >= 0x4e00 and x <= 0x9fbb:
		return True
 
	# CJK Compatibility Ideographs
	elif x >= 0xf900 and x <= 0xfad9:
		return True
 
	# CJK Unified Ideographs Extension B
	elif x >= 0x20000 and x <= 0x2a6d6:
		return True
 
	# CJK Compatibility Supplement
	elif x >= 0x2f800 and x <= 0x2fa1d:
		return True
 
	else:
		return False
 
def mdcode( str, encoding='utf-8' ):
	if isinstance(str, unicode):
		return str.encode(encoding)
 
	for c in ('utf-8', 'gb18030', 'gbk', 'gb2312','utf-16'):
		try:
			if encoding == 'unicode':
				return str.decode(c)
			else:
				return str.decode(c).encode( encoding )
		except:
			pass
	raise 'Unknown charset'
 
def mdcode_char( str, encoding='utf-8' ):
	str_list = list( str )
	#print str_list
	str_result = []
	pos = 0
	while pos < len(str_list):
		#print pos
		#小于127的属于字母、数字等
		if ord( str_list[pos] ) <= 127 :
			str_result.append(str_list[pos])
			pos += 1
			continue
 
		#test utf8 3个字符
		#utf8 占3个字节，先取三个字节看是不是utf8
		c = ''.join( str_list[pos:pos+3] )
		try:
			zh = c.decode('utf-8')
			flag = True
		except:
			flag = False
			zh = ''
 
		#如果可以用decode对3个字节用utf8解码，则确定可能是utf8的汉字
		#再用 is_zh 函数 判断是否符合汉字的编码范围
		#print flag,zh,is_zh(zh)
		if flag and is_zh( zh ):
			pos += 3
			str_result.append(zh)
			continue
 
		#test gb18030 2个字符
		#gb18030 占2个字节，先取两个字节看是不是gb18030
		c = ''.join( str_list[pos:pos+2] )
		try:
			zh = c.decode('gb18030')
			flag = True
		except:
			flag = False
 
		#如果可以用decode对2个字节用gb18030解码，则确定可能是gb18030的汉字
		#再用 is_zh 函数 判断是否符合汉字的编码范围
		#print flag,zh,is_zh(zh)
		if flag and is_zh( zh ):
			pos += 2
			str_result.append(zh)
			continue
		else:
			#raise 'Unknown charset_char'
			pos += 1

	return ''.join( [ i.encode( encoding ) for i in str_result ] )
 
if __name__ == '__main__':
	#测试字符串
	#转换成utf8
	sutf8 = '''123测试中文abc测试'''
	sgbk = mdcode( sutf8, 'gbk')
	
	#这个字符串包含了gbk和utf8的汉字
	sall = "%s%s%s" % (sgbk, sutf8, sgbk)
	print sall
	#转换编码
	sresult = mdcode_char( sall, 'utf-8' )
	#sresult = mdcode( sall, 'gbk' )
	print mdcode(sresult,'utf-8')
