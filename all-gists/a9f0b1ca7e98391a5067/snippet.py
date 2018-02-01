# -*- coding: utf-8 -*-

import maya.OpenMaya as om
import maya.cmds as cmds

def _findFlippedUVs(nodesOnly=True):

	ret = []

	selList = om.MSelectionList()
	om.MGlobal.getActiveSelectionList(selList)

	dpath = om.MDagPath()
	u = om.MFloatArray()
	v = om.MFloatArray()

	cmds.progressWindow(t='findFlippedUVs...', pr=0, st='', isInterruptable=True)

	try:
		for i in xrange(selList.length()):
			if cmds.progressWindow(q=True, isCancelled=True): break

			skip=False
			selList.getDagPath(i, dpath)
			dpath.extendToShape()
			node = dpath.node()
			if node.apiType() != om.MFn.kMesh: continue

			n = dpath.partialPathName()
			fn = om.MFnMesh(node)
			it = om.MItMeshPolygon(node)

			maps = []
			fn.getUVSetNames(maps)

			for m in maps:

				if cmds.progressWindow(q=True, isCancelled=True): break
				cmds.progressWindow(e=True, pr=100*i/selList.length(), st=n + '.' + m)

				if skip: break

				IDs = []
				it.reset()
				while not it.isDone():
					if skip: break
					if not it.hasUVs(m):
						it.next()
						continue

					it.getUVs(u, v, m)
					s = 0
					for k in xrange(1, u.length()-1):
						v1 = [u[k] - u[0], v[k] - v[0]]
						v2 = [u[k+1] - u[0], v[k+1] - v[0]]
						s += v1[0] * v2[1] - v1[1] * v2[0]
					if s < 0: IDs += [it.index()]
					if s < 0 and nodesOnly:
						skip = True
						break

					it.next()

				if len(IDs) < 1: continue

				if nodesOnly: ret += [n]
				else: ret += [('%s.f[%d]' % (n, id)) for id in IDs]
				#if nodesOnly: ret += ['%s    (%s)' % (n, m)]
				#else: ret += [('%s.f[%d]    (%s)' % (n, id, m)) for id in IDs]

	except:
		pass

	finally:
		cmds.progressWindow(endProgress=True)

	return(ret)

if __name__ == "__main__":
	#-- nodesOnly
	#ret = _findFlippedUVs()
	#print(ret)

	#-- getFaceIDs
	ret = _findFlippedUVs(nodesOnly=False)
	print(ret)
