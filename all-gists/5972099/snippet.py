class CustomCollection():
	def __init__(self):
		super().__init__()
		self.items = []
		
	def __setitem__(self, key, value):
		if key == '_':
			self.items.append(value)
		else:
			self.items.append((key, value))
	
	def __getitem__(self, key):
		if key == '_':
			raise KeyError('_')
		return dict(self.items)[key]
		

class _MetaStruct(type):
	""" metaclass for use by magic struct"""

	@classmethod
	def __prepare__(metacls, name, bases):
		return CustomCollection()

	def __new__(cls, name, bases, classdict):
		if bases:
			return Struct(*classdict.items())
		else:
			return super().__new__(name, bases, classdict.items())

class MagicStruct(metaclass=_MetaStruct):
	""" syntactic sugar for making Structs"""
	pass

class ExampleStruct(MagicStruct)
	named = uint64l
	_ = Embedded(Flags(uint64l,
		flag1=0x01,
		flag2=0x20,
	))
