#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright (C) 2011 by Jiang Yio <http://inportb.com/>
## The latest code is available at <https://gist.github.com/962122>
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.

import diff_match_patch

class Operation(object):
	pass
class OperationModel(object):
	pass

class TextOperation(object):
	def patch(self,doc,index):
		raise NotImplemented
	def copy(self,value):
		raise NotImplemented
	def split(self,size):
		raise NotImplemented
	def extend(self,value):
		raise NotImplemented
	def jsonify(self):
		return []
	def __repr__(self):
		return u'?'
	def __eq__(self,op):
		return self.__class__ is op.__class__ and self.value == op.value
class InsertTextOperation(TextOperation):
	def __init__(self,value):
		self.value = unicode(value)
		self.size = len(self.value)
	def patch(self,doc,index):
		return self.value,0
	def compose_RetainTextOperation(self,op):
		return self,
	def compose_DeleteTextOperation(self,op):
		return ()
	def copy(self):
		return self.__class__(self.value)
	def split(self,size):
		if 0 < size < self.size:
			return self.__class__(self.value[:size]),self.__class__(self.value[size:])
		raise ValueError
	def extend(self,value):
		self.value += unicode(value)
		self.size = len(self.value)
	def jsonify(self):
		return [1,self.value]
	def __repr__(self):
		return u'+%d'%self.size
class RetainTextOperation(TextOperation):
	def __init__(self,value):
		self.value = self.size = int(value)
	def patch(self,doc,index):
		return doc[index:index+self.value],self.value
	def compose_RetainTextOperation(self,op):
		return self,
	def compose_DeleteTextOperation(self,op):
		return ()	# op
	def copy(self):
		return self.__class__(self.value)
	def split(self,size):
		if 0 < size < self.size:
			return self.__class__(size),self.__class__(self.size-size)
		raise ValueError
	def extend(self,value):
		self.value = self.size = self.value+int(value)
	def jsonify(self):
		return [0,self.value]
	def __repr__(self):
		return u'=%d'%self.size
class DeleteTextOperation(TextOperation):
	def __init__(self,value):
		self.value = self.size = int(value)
	def patch(self,doc,index):
		return None,self.value
	def copy(self):
		return self.__class__(self.value)
	def split(self,size):
		if 0 < size < self.size:
			return self.__class__(size),self.__class__(self.size-size)
		raise ValueError
	def extend(self,value):
		self.value = self.size = self.value+int(value)
	def jsonify(self):
		return [-1,self.value]
	def __repr__(self):
		return u'-%d'%self.size

class TextOperationModel(OperationModel):
	dmp = diff_match_patch.diff_match_patch()
	composition = {
		(InsertTextOperation,RetainTextOperation):	(lambda op1,op2: op1),
		(InsertTextOperation,DeleteTextOperation):	(lambda op1,op2: None),
		(RetainTextOperation,RetainTextOperation):	(lambda op1,op2: op1),
		(RetainTextOperation,DeleteTextOperation):	(lambda op1,op2: op2)
	}
	transformation = {
		(InsertTextOperation,InsertTextOperation):	(lambda op1,op2: ((RetainTextOperation(op1.size),op2),(op1,RetainTextOperation(op2.size))) if op1.value <= op2.value else ((op2,RetainTextOperation(op1.size)),(RetainTextOperation(op2.size),op1))),
		(InsertTextOperation,RetainTextOperation):	(lambda op1,op2: ((RetainTextOperation(op1.size+op2.size),),(op1,op2))),
		(InsertTextOperation,DeleteTextOperation):	(lambda op1,op2: ((RetainTextOperation(op1.size),op2),(op1,))),
		(RetainTextOperation,InsertTextOperation):	(lambda op1,op2: ((op2,op1),(RetainTextOperation(op2.size+op1.size),))),
		(RetainTextOperation,RetainTextOperation):	(lambda op1,op2: ((op2,),(op1,))),
		(RetainTextOperation,DeleteTextOperation):	(lambda op1,op2: ((op2,),())),
		(DeleteTextOperation,InsertTextOperation):	(lambda op1,op2: ((op2,),(RetainTextOperation(op2.size),op1))),
		(DeleteTextOperation,RetainTextOperation):	(lambda op1,op2: ((),(op1,))),
		(DeleteTextOperation,DeleteTextOperation):	(lambda op1,op2: ((op2,),(op1,)))
	}
	@classmethod
	def compare(cls,doc1,doc2,semantic=True):
		d = cls.dmp.diff_main(doc1,doc2)	# invoke google-diff-match-patch
		if semantic:
			cls.dmp.diff_cleanupSemantic(d)
		patch = cls.dmp.patch_make(doc1,d)
		x = 0								# keep track of current offset
		for p in patch:
			if p.start1 != x:				# if the patch starts at a different offset, retain
				yield RetainTextOperation(p.start1-x)
				x = p.start1
			for pd in p.diffs:				# for each edit in the patch
				pdop = pd[0]
				if pdop == -1:
					yield DeleteTextOperation(len(pd[1]))
				elif pdop == 0:
					l = len(pd[1])
					yield RetainTextOperation(l)
					x += l
				elif pdop == 1:
					yield InsertTextOperation(pd[1])
					x += len(pd[1])
		delta = len(doc2)-x
		if delta > 0:						# if operation does not affect whole document, retain
			yield RetainTextOperation(delta)
	@classmethod
	def patch(cls,doc,ops):
		ret = []
		x = 0
		for op in ops:
			data,index = op.patch(doc,x)
			if data is not None:
				ret.append(data)
			x += index
		return u''.join(ret)
	@classmethod
	def compose(cls,ops1,ops2):
		ops1 = ops1.__iter__()
		ops2 = ops2.__iter__()
		op1 = op2 = None
		while True:
			if op1 is None:
				try:
					op1 = ops1.next()
				except StopIteration:
					if op2 is not None:
						yield op2.copy()
					for op in ops2:
						yield op.copy()
					return
			if op2 is None:
				try:
					op2 = ops2.next()
				except StopIteration:
					yield op1.copy()
					for op in ops1:
						yield op.copy()
					return
			op1cls = op1.__class__
			op2cls = op2.__class__
			if op1cls is DeleteTextOperation:
				op = op1
				op1 = None
			elif op2cls is InsertTextOperation:
				op = op2
				op2 = None
			else:
				op1size = op1.size
				op2size = op2.size
				if op1size > op2size:
					op,op1 = op1.split(op2size)
					op = cls.composition[op1cls,op2cls](op,op2)
					op2 = None
				elif op1size < op2size:
					op,op2 = op2.split(op1size)
					op = cls.composition[op1cls,op2cls](op1,op)
					op1 = None
				else:
					op = cls.composition[op1cls,op2cls](op1,op2)
					op1 = op2 = None
			if op is not None:
				yield op.copy()
	@classmethod
	def transform(cls,ops1,ops2):
		ops1 = ops1.__iter__()
		ops2 = ops2.__iter__()
		op1 = op2 = None
		ret1 = []
		ret2 = []
		while True:
			if op1 is None:
				try:
					op1 = ops1.next()
				except StopIteration:
					if op2 is not None:
						ret1.append(op2.copy())
						if op2.__class__ != DeleteTextOperation:
							ret2.append(RetainTextOperation(op2.size))
					for op in ops2:
						ret1.append(op.copy())
						if op.__class__ != DeleteTextOperation:
							ret2.append(RetainTextOperation(op.size))
					break
			if op2 is None:
				try:
					op2 = ops2.next()
				except StopIteration:
					ret2.append(op1.copy())
					if op1.__class__ != DeleteTextOperation:
						ret1.append(RetainTextOperation(op1.size))
					for op in ops1:
						ret2.append(op.copy())
						if op.__class__ != DeleteTextOperation:
							ret1.append(RetainTextOperation(op.size))
					break
			op1cls = op1.__class__
			op2cls = op2.__class__
			op1size = op1.size
			op2size = op2.size
			if op1size > op2size:
				op,op1 = op1.split(op2size)
				res1,res2 = cls.transformation[op1cls,op2cls](op,op2)
				op2 = None
			elif op1size < op2size:
				op,op2 = op2.split(op1size)
				res1,res2 = cls.transformation[op1cls,op2cls](op1,op)
				op1 = None
			else:
				res1,res2 = cls.transformation[op1cls,op2cls](op1,op2)
				op1 = op2 = None
			ret1.extend(res1)
			ret2.extend(res2)
		return ret1,ret2
	@classmethod
	def collect(cls,ops):
		ret = []
		last = lastcls = lastinsert = lastdelete = None
		for op in ops:
			cls = op.__class__
			if cls is lastcls:
				last.extend(op.value)
			elif cls is lastinsert.__class__:
				lastinsert.extend(op.value)
			elif cls is lastdelete.__class__:
				lastdelete.extend(op.value)
			else:
				if cls is RetainTextOperation:
					lastinsert = lastdelete = None
				elif cls is InsertTextOperation:
					lastinsert = op
				elif cls is DeleteTextOperation:
					lastdelete = op
				ret.append(op)
		return ret
	@classmethod
	def jsonify(cls,ops):
		return (op.jsonify() for op in ops)
	@classmethod
	def unjsonify(cls,ops):
		for op in ops:
			cls = op[0]
			if cls == -1:
				yield DeleteTextOperation(op[1])
			elif cls == 0:
				yield RetainTextOperation(op[1])
			elif cls == 1:
				yield InsertTextOperation(op[1])

if __name__ == '__main__':
	import unittest, random, string
	from operationengine import *
	class TestStructure(unittest.TestCase):
		def setUp(self):
			self.doc1 = u'AABBCCDDEEFFGGIIJJMMOOPP'
			self.doc2 = u'AABBDDEEGGIIJJKKLLMMOO'
			self.doc3 = u'AAEEGGHHIILLMMNNOO'
			self.doc4 = u''.join(random.choice(string.letters) for i in xrange(random.randint(25,50)))
			self.doc5 = u''.join(random.choice(string.letters) for i in xrange(random.randint(25,50)))
		def roundtrip(self,doc1,doc2):
			ops = tuple(TextOperationModel.jsonify(TextOperationModel.compare(doc1,doc2)))
			self.assertEqual(ops,tuple(TextOperationModel.jsonify(TextOperationModel.unjsonify(ops))))
		def test_roundtrip(self):
			self.roundtrip(self.doc1,self.doc1)
			self.roundtrip(self.doc2,self.doc2)
			self.roundtrip(self.doc3,self.doc3)
			self.roundtrip(self.doc1,self.doc2)
			self.roundtrip(self.doc2,self.doc3)
			self.roundtrip(self.doc3,self.doc1)
			self.roundtrip(self.doc2,self.doc1)
			self.roundtrip(self.doc3,self.doc2)
			self.roundtrip(self.doc1,self.doc3)
			self.roundtrip(self.doc4,self.doc4)
			self.roundtrip(self.doc5,self.doc5)
			self.roundtrip(self.doc4,self.doc5)
			self.roundtrip(self.doc5,self.doc4)
	class TestDiffPatch(TestStructure):
		def roundtrip(self,doc1,doc2):
			self.assertEqual(TextOperationModel.patch(doc1,TextOperationModel.compare(doc1,doc2)),doc2)
	class TestComposition(unittest.TestCase):
		def setUp(self):
			self.doc1 = u'AABBCCDDEEFFGGIIJJMMOOPP'
			self.doc2 = u'AABBDDEEGGIIJJKKLLMMOO'
			self.doc3 = u'AAEEGGHHIILLMMNNOO'
			self.doc4 = u''.join(random.choice(string.letters) for i in xrange(random.randint(25,50)))
			self.doc5 = u''.join(random.choice(string.letters) for i in xrange(random.randint(25,50)))
			self.patch12 = tuple(TextOperationModel.compare(self.doc1,self.doc2))
			self.patch23 = tuple(TextOperationModel.compare(self.doc2,self.doc3))
			self.patch34 = tuple(TextOperationModel.compare(self.doc3,self.doc4))
			self.patch45 = tuple(TextOperationModel.compare(self.doc4,self.doc5))
			self.patch51 = tuple(TextOperationModel.compare(self.doc5,self.doc1))
		def roundtrip(self,doc1,doc2):
			ops = tuple(TextOperationModel.jsonify(TextOperationModel.compare(doc1,doc2)))
			self.assertEqual(ops,tuple(TextOperationModel.jsonify(TextOperationModel.unjsonify(ops))))
		def test_roundtrip(self):
			op = self.patch12
			self.assertEqual(TextOperationModel.patch(self.doc1,op),self.doc2)
			op = TextOperationModel.collect(TextOperationModel.compose(op,self.patch23))
			self.assertEqual(TextOperationModel.patch(self.doc1,op),self.doc3)
			op = TextOperationModel.collect(TextOperationModel.compose(op,self.patch34))
			self.assertEqual(TextOperationModel.patch(self.doc1,op),self.doc4)
			op = TextOperationModel.collect(TextOperationModel.compose(op,self.patch45))
			self.assertEqual(TextOperationModel.patch(self.doc1,op),self.doc5)
			op = TextOperationModel.collect(TextOperationModel.compose(op,self.patch51))
			self.assertEqual(TextOperationModel.patch(self.doc1,op),self.doc1)
	class TestTransformation(unittest.TestCase):
		def setUp(self):
			self.doc1 = u'Macs had the original point and click UI.'
			self.doc2 = u'Macintoshes had the original point and click interface.'
			self.doc3 = u'Smith & Wesson had the original point and click UI.'
			self.patch12 = tuple(TextOperationModel.compare(self.doc1,self.doc2))
			self.patch13 = tuple(TextOperationModel.compare(self.doc1,self.doc3))
		def test_transformation(self):
			patch123,patch132 = TextOperationModel.transform(self.patch12,self.patch13)
			self.assertEqual(TextOperationModel.transform(self.patch13,self.patch12),(patch132,patch123))
			print self.doc1
			print TextOperationModel.collect(TextOperationModel.jsonify(self.patch12))
			print TextOperationModel.collect(TextOperationModel.jsonify(self.patch13))
			print TextOperationModel.collect(TextOperationModel.jsonify(self.patch12)),self.doc2
			print TextOperationModel.collect(TextOperationModel.jsonify(patch123))
			print TextOperationModel.patch(self.doc2,patch123)
			print TextOperationModel.collect(TextOperationModel.jsonify(self.patch13)),self.doc3
			print TextOperationModel.collect(TextOperationModel.jsonify(patch132))
			print TextOperationModel.patch(self.doc3,patch132)
			self.assertEqual(TextOperationModel.patch(self.doc2,patch123),TextOperationModel.patch(self.doc3,patch132))
			print TextOperationModel.patch(self.doc2,patch123)
			print TextOperationModel.patch(self.doc3,patch132)
	unittest.main()
