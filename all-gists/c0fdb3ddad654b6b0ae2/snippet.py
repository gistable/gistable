from collections import deque

class hashabledict(dict):
	def __hash__(self):
		return hash(tuple(sorted(self.items())))

def dictFromChar2D(c2d=[], filtr=lambda _:True):
	return {
		(x,y):c
		for y,c1d in zip(range(len(c2d)),c2d)
		for x,c in zip(range(len(c1d)),c1d)
		if filtr(c)
	}

offsets = {">":(1,0), "<":(-1,0), "^":(0,-1), "v":(0,1)}
def nextStates(state,arrowDict):
	for (x,y),bd in state.items(): # pick a block to move
		s2 = hashabledict(state)
		del s2[(x,y)]
		b, d = bd
		dx, dy = offsets[d]
		while bd: # push all adjacent blocks
			x,y = x+dx,y+dy
			bd2 = s2.get((x,y))
			s2[(x,y)] = (bd[0], arrowDict.get((x,y)) or bd[1])
			bd = bd2
		yield b,s2 # (chosen block, next state)

def isDone(state,targets):
	return all(p in state and state[p][0]==b for p,b in targets.items())

def solve(blocks, startDir, targets, arrows):
	prune = lambda state: not all(
		-numBlocks<x<width+numBlocks-1 and 
		-numBlocks<y<height+numBlocks-1 
		for (x,y) in state)

	blockDict  = dictFromChar2D(blocks,  lambda c:c!=' ')
	arrowDict  = dictFromChar2D(arrows,  lambda c:c!=' ')
	targetDict = dictFromChar2D(targets, lambda c:c!=' ')

	numBlocks = len(blockDict)
	width  = max(x for d in [blockDict,arrowDict,targetDict] for (x,y) in d)
	height = max(y for d in [blockDict,arrowDict,targetDict] for (x,y) in d)

	state0 = hashabledict({p:(b,startDir[b]) for p,b in blockDict.items() })

	trace = dict()
	frontier = deque()
	frontier.append(state0)
	trace[state0] = None
	while frontier:
		s = frontier.popleft()
		ns = nextStates(s,arrowDict)
		lastC = trace[s][1] if trace[s] else None # last clicked block
		ns = sorted(ns, key=lambda t: t[0]!=lastC) # we prefer clicking the same block immediately
		for c,s2 in ns:
			if s2 not in trace and not prune(s2):
				trace[s2] = (s,c) # store previous state and chosen block to reconstruct solution
				frontier.append(s2)
				if isDone(s2,targetDict):
					ssc = (s2,'!')
					tr = []
					while ssc:
						tr += [ssc]
						ssc = trace.get(ssc[0])
					tr.reverse()
					print len(trace),"states explored"
					return tr
	return [] # no solution

solution = solve(
	startDir = {
		"Y":">",
		"R":">",
		"B":">"
	},
	blocks = [
		"     ",
		"     ",
		"     ",
		"     ",
		"YRB  "
	],
	targets = [
		"  BRY",
		"     ",
		"     ",
		"     ",
		"     "
	],
	arrows = [
		" v   ",
		"    <",
		"     ",
		">    ",
		"   ^ "
	]
)

# for state, move in solution:
# 	print state, move
print ''.join(c for ss,c in solution)
print len(solution)-1,"moves"