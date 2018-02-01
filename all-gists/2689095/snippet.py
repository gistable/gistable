#!/usr/bin/env python

class Node( object ):
	def __init__( self, end_node = False ):
		self.end_node = end_node
		self.prefix_count = 0
		self.children = {}
	


class Trie( object ):
	def __init__( self ):
		self.root = Node()
	
	def insert( self, key ):
		current = self.root
		for k in key:
			if k not in current.children:
				current.children[k] = Node()
			current = current.children[k]
			current.prefix_count += 1
		current.end_node = True
	
	def search( self, key ):
		current = self.root
		
		for k in key:
			if k not in current.children:
				return False
			current = current.children[k]
		return current.end_node
	
	def count( self, key ):
		current = self.root
		for k in key:
			if k not in current.children:
				return 0
			current = current.children[k]
		return current.prefix_count

	def _walk( self, root, prefix ):
		out = []
		if root.end_node:
			out.append( prefix )
		
		for ch in root.children:
			if isinstance( prefix, tuple ):
				tmp = self._walk( root.children[ch], prefix + (ch,) )
			elif isinstance( prefix, list ):
				tmp = self._walk( root.children[ch], prefix + [ch] )
			else:
				tmp = self._walk( root.children[ch], prefix + ch )
			out.extend( tmp )
		return out

	def enumerate( self, key ):
		current = self.root
		for k in key:
			if k not in current.children:
				return []
			current = current.children[k]
		
		return self._walk( current, key )	



db = Trie()

db.insert( "apple" )
db.insert( "apples" )
db.insert( "banana" )
db.insert( "applet" )

print db.search( "apple" )
print db.search( "app" )
print db.search( "bananaa" )
print db.search( "" )
print db.count( "app" )
db.insert( "apple" )
print db.count( "app" )
print db.count( "b" )
print "*******"
print ""
print db.enumerate( "app" )
print ""
print ""

db = Trie()
db.insert( (1,) )
db.insert( (2, ) )
db.insert( (1,2) )
db.insert( (1,2,2) )
db.insert( (2,1,1) )

print db.search( (1,2,2) )
print db.search( "moi" )
print db.enumerate( (1,) )
