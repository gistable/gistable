import glob

# declare types of commands
C_ARITMETIC = object()
C_PUSH = object()
C_POP = object()
C_LABEL = object()
C_GOTO = object()
C_IF = object()
C_FUNCTION = object()
C_RETURN = object()
C_CALL = object()
C_ERROR = object()

class CodeWriter:
	file = None	# file to be writing to
	fileName = None
	compare = 1 # the number of equalities
	curFunction = None # stores the name of the current function
	
	def __init__(self, name):
		self.file = open(name, 'w')
		self.fileName = name.strip()
		
	def __del__(self):
		self.file.close()
		
	def WriteAritmetic(self, arg1):
		# plus or minus
		if arg1 in ['add', 'sub', 'and', 'or']:	
			if arg1 == 'add': line = 'D=D+M'
			elif arg1 == 'sub': line = 'D=M-D'
			elif arg1 == 'and': line = 'D=D&M'
			elif arg1 == 'or': line = 'D=D|M'
			self.file.write("@SP\n")		#A=0, M[0]=258
			self.file.write("M=M-1\n")	#M[0]=258-1
			self.file.write("A=M\n")		#A=257
			self.file.write("D=M\n")		#D=M[257] (8)
			self.file.write("A=A-1\n")	#A=256
			self.file.write("%s\n" % (line, ))
			self.file.write("M=D\n")		#M[256]=D
			self.file.write("D=A+1\n")	#A=257
			self.file.write("@SP\n")
			self.file.write("M=D\n")
			return True
		# unary operations
		elif arg1 in ['neg', 'not']:
			line = 'M=-M' if arg1 == 'neg' else 'M=!M'
			self.file.write("@SP\n")
			self.file.write("M=M-1\n")
			self.file.write("A=M\n")
			self.file.write("%s\n" % (line, ))
			self.file.write("D=A+1\n")
			self.file.write("@SP\n")
			self.file.write("M=D\n")
		# in case they are equal
		elif arg1 in ['eq', 'lt', 'gt']:
			if arg1 == "eq":
				line = "D;JEQ"
			elif arg1 == "lt":
				line = "D;JLT"
			elif arg1 == "gt":
				line = "D;JGT"
			self.file.write("@SP\n")
			self.file.write("M=M-1\n")
			self.file.write("A=M\n")
			self.file.write("D=M\n")
			self.file.write("A=A-1\n")
			self.file.write("D=M-D\n")
			self.file.write("@EQ%d\n" % (self.compare, ))
			self.file.write("%s\n" % (line, ))
			self.file.write("@0\n")
			self.file.write("D=-A\n")
			self.file.write("@SP\n")
			self.file.write("A=M\n")
			self.file.write("M=D\n")
			self.file.write("@SP\n")
			self.file.write("M=M+1\n")
			self.file.write("@doneEQ%d\n" % (self.compare, ))
			self.file.write("0;JMP\n")
			self.file.write("(EQ%d)\n" % (self.compare, ))
			self.file.write("@1\n")
			self.file.write("D=A\n")
			self.file.write("@SP\n")
			self.file.write("A=M\n")
			self.file.write("M=D\n")
			self.file.write("@SP\n")
			self.file.write("M=M+1\n")
			self.file.write("(doneEQ%d)\n" % (self.compare, ))
			
			self.compare += 1			
		return False
		
	def WritePushPop(self, type, segment, index):
		# deal with the value
		value = 0
		if segment == "constant":
			self.file.write("@%s\n" % (str(index), ))
			self.file.write("D=A\n")
		elif segment in ['local', 'argument', 'this', 'that']:
			if segment == 'local': key = "LCL"
			elif segment == 'argument': key = "ARG"
			elif segment == 'this': key = 'THIS'
			elif segment == 'that': key = 'THAT'
			self.file.write("@%s\n" % (str(key), ))
			self.file.write("D=A\n")
			self.file.write("@%s\n" % (str(index), ))
			self.file.write("D=D+M\n")
		elif segment in ['pointer', 'temp']:
			if segment == 'pointer': base = 3
			elif segment == 'temp': base = 5
			self.file.write("@%s\n" % (base, ))
			self.file.write("D=A\n")
			self.file.write("@%s\n" % (index, ))
			self.file.write("D=D+A\n")
		elif segment in ['static']:
			self.file.write("@%s.%s\n" % (self.fileName[:-4], index))
			self.file.write("D=M\n")
		
		if type is C_PUSH:
			self.file.write("@SP\n")
			self.file.write("A=M\n")
			self.file.write("M=D\n")
			self.file.write("D=A+1\n")
			self.file.write("@SP\n")
			self.file.write("M=D\n")
			return True
		elif type is C_POP:
			self.file.write("@R13\n")
			self.file.write("M=D\n")
			self.file.write("@SP\n")
			self.file.write("A=M-1\n")
			self.file.write("D=M\n")
			self.file.write("@R13\n")
			self.file.write("A=M\n")
			self.file.write("M=D\n")
			return True
			
		return False
		
	def WriteLabel(self, b):
		self.file.write("(%s$%s)\n" % (self.curFunction, b))
		return True
		
	def WriteGOTO(self, b):
		self.file.write("@%s$%s\n" % (self.curFunction, b))
		self.file.write("0;JMP\n")
		return True
		
	def WriteIf(self, b):
		self.file.write("@SP\nA=M\nD=M\n")
		self.file.write("@SP\nM=M-1\n")
		self.file.write("0;JMP\n")
		self.file.write("@%s\n" % (b, ))
		self.file.write("D;JMP\n")
		return True
		
	def WriteSPup(self):
		self.file.write("D=A\n")
		self.file.write("@SP\n")
		self.file.write("M=A\n")
		self.file.write("M=D\n")
		self.file.write("@SP\n")
		self.file.write("M=M+1")
		return True
		
	def WriteCall(self, f, n):
		self.file.write("@return-%s\n" % (f, ))
		self.WriteSPup()
		self.file.write("@LCL\n")
		self.WriteSPup()
		self.file.write("@ARG\n")
		self.WriteSPup()
		self.file.write("@THIS\n")
		self.WriteSPup()
		self.file.write("@THAT\n")
		self.WriteSPup()
		self.file.write("@SP\n")
		self.file.write("D=M\n")
		self.file.write("@ARG\n")
		self.file.write("D=D-n\n")
		self.file.write("M=D-5\n")
		self.file.write("@LCL\n")
		self.file.write("M=D\n")
		self.WriteGOTO(f)
		self.file.write("(return-%s)\n" % (f, ))
		return True
		
	def WriteFunction(self, f, k):
		self.file.write ("(%s)\s" % (f, ))
		curFunction = f
		for i in range(0, k):
			self.file.write("@0\n")
			self.WriteSPup()
		return True
		
	def WriteReturn(self):
		self.file.write("@LCL\n")
		self.file.write("D=M\n")
		self.file.write("@R13\n")
		self.file.write("M=D\n")	# R13 is now FRAME
		self.file.write("D=M-5\n")
		self.file.write("@R14\n")
		self.file.write("M=D\n")	# R14 stores RET
		self.file.write("@SP\n")
		self.file.write("M=A\n")
		self.file.write("D=M\n")
		self.file.write("@ARG\n")
		self.file.write("A=M\n")
		self.file.write("M=D\n")		# *ARG = pop()
		self.file.write("@ARG\n")
		self.file.write("D=M\n")
		self.file.write("@SP\n")
		self.file.write("M=A\n")
		self.file.write("M=D+1\n")		# SP = ARG + 1
		self.file.write("@R13\n")
		self.file.write("D=M\n")
		self.file.write("@THAT\n")	# THAT = FRAME-1
		self.file.write("M=D-1\n")
		self.file.write("@THIS\n")
		self.file.write("M=D-2\n")	# FRAME - 2
		self.file.write("@ARG\n")
		self.file.write("M=D-3\n")	# FRAME-3
		self.file.write("@LCL\n")
		self.file.write("M=D-4\n")	# FRAME - 4
		self.file.write("@R14\n")
		self.file.write("D=M\n")
		self.file.write("@D\n")	# GOTO RET
		self.file.write("0;JMP\n")
		return True
		
	def WriteBootstrap(self):
		self.file.write("@SP\n")
		self.file.write("M=256\n")
		self.WriteCall("Sys.init", 0)
		return True

class VM:
	file = None	# stores the file(s) to open
	fileWriter = None	# the new file to write to
	dir = None # name of the directory
	
	# get the file
	def __getFile(self):
		var = raw_input("What is the file name/directory: ")
		
		# if ends in .vm just one file, otherwise directory
		if var[len(var)-3:len(var)] == '.vm':
			self.file = [var]
			self.dir = var[:-3]
		else:
			# directory, check if ends in /, otherwise add
			if var[-1] <> "/":
				self.dir = var
				var = "%s/" % var
			else:
				self.dir = var[:-1]
			# glob through them all for .vm files
			self.file = glob.glob(var + "*.vm")
			
		return True
		
	# check if the line is actually code
	def __isCode(self, line):
		output = line.lstrip(" ")
		if output.startswith("//"): 	# check if it is a comment
			return False
		elif output.startswith('\n'):	# check if it just a new line
			return False
		else:
			return True
	
	# parse the line
	def __parseLine(self, line):
		line = line.strip(" ")
		line = line.rstrip("\n")
		line = line[:line.find("//")]
		return line.lower()
		
	# define the command type
	def __commandType(self, line):
		if line.find(" ") > -1:
			seg1 = line[:line.find(" ")].lower()
		else:
			seg1 = line.lower()
		
		if seg1 == "push":
			return C_PUSH
		elif seg1 == "pop":
			return C_POP
		elif seg1 in ['add', 'sub', 'neg', 'eq', 'lt', 'gt', 'and', 'or', 'not']:
			return C_ARITMETIC
		elif seg1 == "label":
			return C_LABEL;
		elif seg1 == "goto":
			return C_GOTO
		elif seg1 == "if-goto":
			return C_IF
		elif seg1 == "call":
			return C_CALL
		elif seg1 == "function":
			return C_FUNCTION
		elif seg1 == "return":
			return C_RETURN
		else:
			return C_ERROR
			
	# get the first arguement		
	def __arg1(self, input):
		if input.find(" ") < 0:
			return input
		else: 
			input = input[input.find(" ")+1:]
			return input[:input.find(" ")]
		
	# def get the second arguement
	def __arg2(self, input): 
		input = input[input.find(" ")+1:]
		return input[input.find(" ")+1:]
		
	# go through the file and do the cool shit	
	def __outFile(self, inFile):
		# open new file
		input = open(inFile, 'r')
		# loop through
		for f in input:
			# check if it is a comment or a newline
			if not self.__isCode(f):
				continue
			
			# parse the line
			f = self.__parseLine(f)
			
			# what type of line it is
			type = self.__commandType(f)
			
			# error?  return
			if type is C_ERROR:
				import sys
				print "Error on line: %s" % (f, )
				sys.exit()
			
			# write a line
			if type is C_ARITMETIC:
				self.fileWriter.WriteAritmetic(self.__arg1(f))
			elif type in [C_PUSH, C_POP]:
				self.fileWriter.WritePushPop(type, self.__arg1(f), self.__arg2(f))
			elif type is C_LABEL:
				self.fileWriter.WriteLabel(self.__arg1(f))
			elif type is C_ERROR:
				self.fileWriter.WriteGOTO(self.arg1(f))
			elif type is C_IF:
				self.fileWriter.WriteIF(self.__arg1(f))
			elif type is C_CALL:
				self.fileWrite.WriteCall(self.__arg1(f), self.__arg2(f))
			elif type is C_FUNCTION:
				self.fileWrite.WriteFunction(self.__arg1(f), self.__arg2(f))
			elif type is C_RETURN:
				self.fileWrite.WriteReturn()
			
	# boot strap the VM		
	def __init__(self):
		# get the files to open to
		print "Getting files..."
		self.__getFile()
		# the file writer class
		self.fileWriter = CodeWriter(self.dir + ".asm")
		# need the boot write
		self.fileWriter.WriteBootstrap()
		# foreach file out
		print "Writing files..."
		for f in self.file:
			self.__outFile(f)
		# destroy the filewrite - to close the file
		print "Done"
		del self.fileWriter

# main execution of the code		
if __name__ == "__main__":
	aVM = VM()
	