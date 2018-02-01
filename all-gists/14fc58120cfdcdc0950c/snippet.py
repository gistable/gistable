"""
Script to sort edge list of a simple polygon with 1 face in Blender with Python.
Something like this:
      0_________3
      /         \
    4/           \2
     \           /
     5\_________/1
becomes sorted as {[4,5],[5,1],...,[0,4]}.
Tested with Blender v2.67.
##! Make sure to be in Edit Mode !##

The MIT License (MIT)

Copyright (c) 2014 Francis Laclé

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import bpy
import os

#clear screen (command for windows)
os.system('cls')

scn = bpy.context.scene           
obj = bpy.context.object

#get mesh data from object                
mesh = obj.data

edge_count = mesh.total_edge_sel
print("number of elements in m:", edge_count)
                         
if(edge_count &gt; 0):
    
    e = []
    e.append(mesh.edges[0])
    flip = []
    
    #main loop for edge e
    for e_iter in mesh.edges:
        eb = e[-1].vertices[1] #end vertex of last edge of e
        found = False
        
        #first search
        for m in mesh.edges:
            ma = m.vertices[0] #begin vertex of edge m
            mb = m.vertices[1] #end vertex of edge m
            if(eb == ma):
                flipFound = False
                for n in e:
                    if(n.vertices[0] == mb and n.vertices[1] == ma):
                        flipFound = True
                        break
                if(flipFound == True):
                    continue
                else:         
                    e.append(m)
                    found = True
                    break
            
        #check for reverse direction in case first search failed
        if(found == False):
            for m in mesh.edges:
                ma = m.vertices[0] #begin vertex of edge e
                mb = m.vertices[1] #end vertex of edge e
                
                #...also exclude existing m's in e
                if(mb == eb and m not in e):
                    #create duplicate to reverse vertex indices
                    m_dup = mesh.copy()
                    f = m_dup.edges[m.index]
                    f.vertices[0] = mb
                    f.vertices[1] = ma
                    e.append(f)
                else:
                    continue
    
    #remove last element (was added twice)
    del e[-1]

    print("number of elements in e:",len(e))
    print()
    print("--- sorted edge list ---")     
    for idx, val in enumerate(e):
        print("[",val.vertices[0],",",val.vertices[1],"]")
    print()
    print("--- original edge list ---")
    for i in mesh.edges:
        print("[",i.vertices[0],",",i.vertices[1],"]")   