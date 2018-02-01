import Rhino

class DrainBoid(object):
    def __init__(self, point3d, surface, stepsize=0.5, maxsteps=None, tolerance=0.001):
        self.start = point3d
        self.pos = self.start
        result, self.u, self.v = surface.ClosestPoint(self.pos)
        self.surface = surface
        self.stepsize = stepsize
        self.points = [self.start]
        self.state = 'on'
        self.tolerance = tolerance
        self.maxsteps = maxsteps

    def makeDrainCurve(self):
        i = 0
        while self.state == 'on':
            i += 1
            if self.maxsteps:
                if i >= self.maxsteps:
                    self.state = 'finished'
            self.nextStep()
        return Rhino.Geometry.Curve.CreateControlPointCurve(self.points, 1)

    def nextStep(self):
        result, newFrame = self.surface.FrameAt(self.u, self.v)
        # create a vector from newFrame XAxis
        downVect = newFrame.XAxis
        # figure out hw far to rotate it.
        deltaAngle = Rhino.Geometry.Vector3d.VectorAngle( downVect, Rhino.Geometry.Vector3d(0.0, 0.0, -1.0), newFrame )
        # rotate it in the plane
        downVect.Rotate( deltaAngle, newFrame.ZAxis)
        # set the length
        downVect = downVect.Multiply( self.stepsize, downVect )
        spacePoint = Rhino.Geometry.Point3d.Add(self.pos, downVect)
        result, self.u, self.v = self.surface.ClosestPoint(spacePoint)
        out, newPoint, vects = self.surface.Evaluate(self.u, self.v, 0)
        if newPoint.Z >= self.pos.Z: # if higher
            self.state = 'finished'
        elif not self.checkTolerance(newPoint): # if too close
            self.state = 'finished'
        else:
            self.updatePos( newPoint )

    def updatePos(self, newPoint):
        self.points.append(newPoint)
        self.pos = newPoint

    def checkTolerance(self, other):
        # checks against another point
        # if it is outside of tolerance, returns True
        return self.pos.DistanceTo( other ) > self.tolerance

if terrainSurface:
    b = DrainBoid(startPoint, terrainSurface, stepSize, maxSteps, tol)
    a = b.makeDrainCurve()