import maya.cmds as mc
import pymel.core as pm

class ProgressBar:
    def __init__ (self,title,steps):
        #self.step = 0
        self.title=title
        self.steps = steps
        self.progressControls = []
        self.progressbar = self.makeProgressBarWindow()
        self.increment(0)
        self.increment(1)
        self.increment(2)

    def makeProgressBarWindow(self):
        self.window = pm.window(title=self.title, sizeable=False)
        pm.columnLayout()
        
    	self.progressControls.append( pm.progressBar(maxValue=self.steps, width=300) )
    	self.progressControls.append( pm.progressBar(maxValue=self.steps, width=300) )
    	self.progressControls.append( pm.progressBar(maxValue=self.steps, width=300) )
    	pm.showWindow( self.window )
    	return [self.progressControls[0], self.progressControls[1], self.progressControls[2], self.window]

    def kill(self):
        pm.deleteUI(self.window)

    def increment(self, i):
        #self.step = self.step + 1
        self.progressControls[i].step(1)

class Friend:
    def __init__(self,point,distance):
        self.point = point
        self.distance = distance
        self.dirty = False

class Point:
    def __init__(self, t):
        '''
        t=PyNode
        '''
        self.node = t
        self.pos = t.getTranslation(space='world')
        self.friends = [] # [Friend]
    
    def getFriends(self, points):
        for p in points:
            if p == self: continue
            self.friends.append(Friend(p,self.getDistance(p)))
    
    def getDistance(self, point):
         Ax, Ay, Az = point.pos
         Bx, By, Bz = self.pos
         return (  (Ax-Bx)**2 + (Ay-By)**2 + (Az-Bz)**2  )**0.5
    
    def getChain(self, progressBar, chain=[], dirty=[]):
        chain.append(self)
        
        friends = []
        for x in self.friends:
            cond1 = x.point not in chain
            cond2 = x.point not in dirty
            if cond1 and cond2:
                friends.append(x)
        
        if len(friends) == 0:
            return chain
        
        # skip the really close friends.
        friend = friends[0].point
        for f in friends:
            if f.distance < 0.1:
                dirty.append(f.point)
                continue
            friend = f.point
            break
        
        if friend not in chain:
            progressBar.increment(1)
            return friend.getChain(progressBar, chain, dirty)
        else:
            return chain

transforms = mc.ls(selection=True)
points = [Point(pm.PyNode(t)) for t in transforms]

progressBar = ProgressBar('Creating Racespline', len(points))

for point in points:
    point.getFriends(points)
    point.friends.sort(key=lambda x: x.distance)
    progressBar.increment(0)

chain = points[-1].getChain(progressBar)

chain.reverse()
c = pm.curve(point=[x.pos for x in chain])
g = pm.createNode('transform', name='newnode')

i=0
for x in chain:
    name = 'node_'+"%04d" % (i,)
    i=i+1
    l = pm.spaceLocator(position=x.pos, absolute=True)
    pm.rename(l,name)
    pm.parent(pm.PyNode(l),g)
    progressBar.increment(2)

progressBar.kill()