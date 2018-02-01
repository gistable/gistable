# Jumps to every event in turn, optionally doing work at each point

import time
import random

do_vert_debug = 1
do_pixel_debug = 1
action_chance = 0.333

x = 0
y = 0
lastmod = None

def vert_debug(r):
	# todo, pick a random but valid vertex. Need to fetch index buffer data
	trace = r.DebugVertex(0, 0, 0, pyrenderdoc.CurDrawcall.instanceOffset, pyrenderdoc.CurDrawcall.vertexOffset)
	print "Vertex debugged in %d cycles" % len(trace.states)

def pixel_history(r):
	global lastmod, x, y
	viewport = pyrenderdoc.CurPipelineState.GetViewport(0)

	# todo, query for some pixel this drawcall actually touched.
	x = int(random.random()*viewport.width + viewport.x)
	y = int(random.random()*viewport.height + viewport.y)

	target = renderdoc.ResourceId.Null

	outputs = pyrenderdoc.CurPipelineState.GetOutputTargets()

	if len(outputs) > 0:
		target = outputs[0].Id
	
	if target == renderdoc.ResourceId.Null:
		target = pyrenderdoc.CurPipelineState.GetDepthTarget().Id

	if target == renderdoc.ResourceId.Null:
		print "No targets bound! Can't history"
		return
		
	print "Fetching history for %d,%d on target %s" % (x, y, str(target))
	
	history = r.PixelHistory(target, x, y, 0, 0, 0xffffffff, renderdoc.FormatComponentType.None)
	
	print "Pixel %d,%d has %d history events" % (x, y, len(history))
	
	for i in range(len(history)-1, 0, -1):
		mod = history[i]
		draw = pyrenderdoc.GetDrawcall(mod.eventID)

		print "  hit %d at %d is %s (%s)" % (i, mod.eventID, draw.name, str(draw.flags))

		if draw == None or not draw.flags.HasFlag(renderdoc.DrawcallFlags.Drawcall):
			continue

		lastmod = history[i]

		print "Got a hit on a drawcall at event %d" % lastmod.eventID

		break

def pixel_debug(r):
	trace = r.DebugPixel(x, y, 0xffffffff, 0xffffffff)

	print "Pixel %d,%d debugged in %d cycles" % (x, y, len(trace.states))

lastDraw = pyrenderdoc.CurDrawcalls[len(pyrenderdoc.CurDrawcalls) - 1]
while len(lastDraw.children) > 0:
	lastDraw = lastDraw.children[len(lastDraw.children) - 1]

for eventID in range(0, lastDraw.eventID):
	curdraw = pyrenderdoc.GetDrawcall(eventID)

	if curdraw == None:
		continue

	pyrenderdoc.SetEventID(None, curdraw.eventID)
	print ""
	print "%d - %s" % (curdraw.eventID, curdraw.name)

	if do_vert_debug and curdraw.flags.HasFlag(renderdoc.DrawcallFlags.Drawcall) and random.random() < action_chance:
		pyrenderdoc.Renderer.Invoke(vert_debug)

	if do_pixel_debug and curdraw.flags.HasFlag(renderdoc.DrawcallFlags.Drawcall) and random.random() < action_chance:
		lastmod = None
		pyrenderdoc.Renderer.Invoke(pixel_history)
		if lastmod != None:
			pyrenderdoc.SetEventID(None, lastmod.eventID)
			pyrenderdoc.Renderer.Invoke(pixel_debug)
			pyrenderdoc.SetEventID(None, curdraw.eventID)
