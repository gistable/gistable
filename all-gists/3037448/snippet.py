#!BPY

"""
Name: 'FaceGen TRI (.tri)...'
Blender: 249
Group: 'Import'
Tooltip: 'Load a FaceGen TRI file.'
"""

__author__= "himika"
__version__= "0.2"

__bpydoc__= """\
This script imports a FaceGen TRI file to Blender.

Usage:
Run this script from "File->Import" menu and then load the desired TRI file
"""

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Copyright (C) 2012 himika
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

import bpy
import Blender
from Blender import Mesh, Draw, Window, Texture, Material, sys
import BPyMessages
from pyffi.formats.tri import TriFormat



def importMenu():
	global ROTATE_X90, INPORT_MORPH_SHAPE, INPORT_MODIFIER_SHAPE
	ROTATE_X90 = Blender.Draw.Create(1)
	INPORT_MORPH_SHAPE = Blender.Draw.Create(1)
	INPORT_MODIFIER_SHAPE = Blender.Draw.Create(1)
	
	# Get USER Options
	pup_block = [\
	('Rotate X90', ROTATE_X90, 'Rotate X -90'),\
	('TRI Morph',  INPORT_MORPH_SHAPE, 'Include TRI Morph'),\
	('TRI Modifier', INPORT_MODIFIER_SHAPE, 'Include TRI Modifier')\
	]
	
	if not Blender.Draw.PupBlock('Import TRI...', pup_block):
		return
	
	Blender.Window.WaitCursor(1)
	
	ROTATE_X90 = ROTATE_X90.val
	INPORT_MORPH_SHAPE = INPORT_MORPH_SHAPE.val
	INPORT_MODIFIER_SHAPE = INPORT_MODIFIER_SHAPE.val



def loadTri(filename):
	if BPyMessages.Error_NoFile(filename):
		return
	
	importMenu()
	
	print('\nImporting tri: "%s"' % (Blender.sys.expandpath(filename)))
	istrm = open(filename, 'rb')
	data = TriFormat.Data()
	data.inspect(istrm)
	data.read(istrm)
	istrm.close()
	print("\nTRI version 0x%x |  Ve:%d | Fa:%d | UV:%d |" % (data.version, data.num_vertices, data.num_tri_faces, data.num_uvs))
	print("Num Morphs:%d | Num Modifiers:%d\n" % (data.num_morphs, data.num_modifiers))

	name = filename.split('\\')[-1].split('/')[-1]
	scn  = bpy.data.scenes.active
	mesh = Mesh.New()
	
	# vertex
	verts_list = [(v.x, v.y, v.z) for v in data.vertices]
	if ROTATE_X90:
		verts_list[:] = [(v[0], -v[2], v[1]) for v in verts_list]
	mesh.verts.extend(verts_list)
	
	# face
	face_list = [(f.v_1, f.v_2, f.v_3) for f in data.tri_faces]
	mesh.faces.extend(face_list)
	del face_list
	
	# UV
	if data.num_uvs > 0:
		mesh.faceUV = True
		for i, face in enumerate(mesh.faces):
			utf = data.uv_tri_faces[i]
			idx = [utf.v_1, utf.v_2, utf.v_3]
			for ii, j in enumerate(face):
				uv = data.uvs[idx[ii]]
				face.uv[ii].x = uv.u
				face.uv[ii].y = uv.v
	
	ob = scn.objects.new(mesh, name)
	
	# Shape Keys
	if (data.num_morphs > 0 and INPORT_MORPH_SHAPE) or (data.num_modifiers > 0 and INPORT_MODIFIERS_SHAPE):
		mesh.insertKey(1, 'relative')
		
		if INPORT_MORPH_SHAPE:
			for morph in data.morphs:
				morphName = str(morph.name.decode("ascii"))
				scale = morph.scale
				print("... Morhph:" + morphName)
				for i, nv in enumerate(mesh.verts):
					verts_morph = morph.vertices[i]
					v3 = [verts_morph.x, verts_morph.y, verts_morph.z]
					if ROTATE_X90:
						v3 = [v3[0], -v3[2], v3[1]]
					nv.co[0] = verts_list[i][0] + v3[0] * scale
					nv.co[1] = verts_list[i][1] + v3[1] * scale
					nv.co[2] = verts_list[i][2] + v3[2] * scale
				mesh.insertKey(1, 'relative')
				mesh.key.blocks[-1].name = morphName
		
		if INPORT_MODIFIER_SHAPE:
			for modifier in data.modifiers:
				modifierName = str(modifier.name.decode("ascii"))
				print("... Modifier:" + modifierName)
				for i, nv in enumerate(mesh.verts):
					nv.co[0] = verts_list[i][0]
					nv.co[1] = verts_list[i][1]
					nv.co[2] = verts_list[i][2]
				for i, n in enumerate(modifier.vertices_to_modify):
					nv = mesh.verts[n]
					mv = modifier.modifier_vertices[i]
					v3 = [mv.x, mv.y, mv.z]
					if ROTATE_X90:
						v3 = [v3[0], -v3[2], v3[1]]
					nv.co[0] = v3[0]
					nv.co[1] = v3[1]
					nv.co[2] = v3[2]
				mesh.insertKey(1, 'relative')
				mesh.key.blocks[-1].name = modifierName
		
		for i, nv in enumerate(mesh.verts):
			nv.co[0] = verts_list[i][0]
			nv.co[1] = verts_list[i][1]
			nv.co[2] = verts_list[i][2]
	
	del verts_list
	print("done.")

#============================
# main
if __name__=='__main__':
	Blender.Window.FileSelector(loadTri, 'Import tri', '*.tri')
