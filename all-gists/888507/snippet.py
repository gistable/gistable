
class Helpers(object):
    """Contains various helper methods."""
    def __init__(self, arg):
        super(Helpers, self).__init__()
    
    @staticmethod
    def readConfig(filepath=None):
        """
        Read settings from a configuration file.
            
        Returns None if config file at filepath doesn't exist.
        Returns the config object on success.
        """
        result = None
        if filepath is None:
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res/", "config.ini")
        if os.path.exists(filepath):
            config = ConfigParser.ConfigParser()
            config.read(filepath)
            result = config
        return result
    
    @staticmethod
    def saveConfig(config, filepath=None):
        """
        Save settings to a configuration file.
        
        If filepath is None, it will be assumed to point to res/config.ini.
        Returns True if successful, False otherwise.
        """
        result = False
        if filepath is None:
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res/", "config.ini")
        try:
            with open(filepath, 'wb') as configfile:
                config.write(configfile)
            result = True
        except Exception, e:
            print "*** Caught Exception: %r ***" % e
        return result
    
    @staticmethod
    def initConfig(defaults, filepath=None):
        """
        Initialize configuration file by writing the defaults.
            
        Returns True if config file was created, 
        False if config file already exists or otherwise.
        """
        result = False
        if filepath is None:
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res/", "config.ini")
        if not os.path.exists(filepath):
            config = ConfigParser.ConfigParser(defaults)
            result = Helpers.saveConfig(config, filepath)
        return result
    
    @staticmethod
    def vDeg(v, ishpb=False):
        """Convert each component of vector v to degrees"""
        if v is None:
            raise ValueError("v can't be None")
        if not isinstance(v, c4d.Vector): 
            raise TypeError("Expected vector, got %s" % type(v))
        if ishpb:
            res = c4d.Vector(0,0,0)
            res.x = Deg(v.x)
            res.y = Deg(v.y)
            res.z = Deg(v.z)
            if res.x >= 180:
                res.x -= 360
            if res.y >= 180:
                res.y -= 360
            if res.z >= 180:
                res.z -= 360
            return res
        else:
            return c4d.Vector(Deg(v.x), Deg(v.y), Deg(v.z))
    
    @staticmethod
    def vRad(v, ishpb=False):
        """Convert each component of vector v to radians"""
        if v is None:
            raise ValueError("v can't be None")
        if not isinstance(v, c4d.Vector): 
            raise TypeError("Expected vector, got %s" % type(v))
        if ishpb:
            if v.x >= 180:
                v.x -= 360
            if v.y >= 180:
                v.y -= 360
            if v.z >= 180:
                v.z -= 360
        return c4d.Vector(Rad(v.x), Rad(v.y), Rad(v.z))
    
    @staticmethod
    def vAvg(lst):
        """Calculate the average of a list of vectors"""
        if lst is None:
            raise ValueError("List lst can't be None")
        if not isinstance(lst, list): 
            raise TypeError("Expected list of vectors, got %s" % type(lst))
        lstlen = len(lst)
        res = c4d.Vector(0,0,0)
        if lstlen == 0: return res
        for l in lst:
            res.x += l.x
            res.y += l.y
            res.z += l.z
        res.x = res.x / float(lstlen)
        res.y = res.y / float(lstlen)
        res.z = res.z / float(lstlen)
        return res
    
    @staticmethod
    def select(op):
        if not op.GetBit(c4d.BIT_ACTIVE):
            op.ToggleBit(c4d.BIT_ACTIVE)
        return op.GetBit(c4d.BIT_ACTIVE)
    
    @staticmethod
    def selectAdd(op):
        """
        Same as select(op) but uses a slightly different mechanism.
            
        See also BaseDocument.SetSelection(sel, mode).
        """
        doc = op.GetDocument()
        doc.SetActiveObject(op, c4d.SELECTION_ADD)
    
    @staticmethod
    def selectGroupMembers(grp):
        doc = documents.GetActiveDocument()
        for obj in grp:
            # add each group member to the selection 
            # so we can group them in the object manager
            #doc.AddUndo(UNDO_BITS, obj)
            doc.SetActiveObject(obj, c4d.SELECTION_ADD)
    
    @staticmethod
    def selectObjects(objs):
        for op in objs:
            Helpers.select(op)
    
    @staticmethod
    def deselectAll(inObjMngr=False):
        """
        Not the same as BaseSelect.DeselectAll().
            
        inObjMngr  bool  if True, run the deselect command from Object Manager, 
                         else the general one for editor viewport
        """
        if inObjMngr is True:
            c4d.CallCommand(100004767) # deselect all (Object Manager)
        else:
            c4d.CallCommand(12113) # deselect all
    
    @staticmethod
    def groupObjects(objs, name="Group"):
        """
        CallCommand based grouping of objects from a list. 
            
        Generally unreliable, because selection state matters.
        Use insertUnderNull for better effect.
        """
        Helpers.deselectAll(True)
        result = None
        if objs is None: 
            return result
        if not isinstance(objs, list):
            objs = [objs]
        else:
            return result
        for o in objs:
            Helpers.select(o)
        if DEBUG: print "creating group %s" % name
        c4d.CallCommand(100004772) # group objects
        doc = documents.GetActiveDocument()
        grp = doc.GetActiveObject()
        grp.SetName(name)
        result = grp
        return result
    
    @staticmethod
    def groupSelected(name="Group"):
        """
        CallCommand based grouping of selected objects. 
            
        Generally unreliable, because selection state matters.
        Use insertUnderNull for better effect.
        """
        result = None
        if DEBUG: print "creating group %s" % name
        c4d.CallCommand(100004772) # group objects
        doc = documents.GetActiveDocument()
        grp = doc.GetActiveObject()
        grp.SetName(name)
        result = grp
        return result
    
    @staticmethod
    def recurseBranch(obj):
        child = obj.GetDown()
        while child:
            child = child.GetNext()
            return Helpers.recurseBranch(child)
    
    @staticmethod
    def getNextObject(op, stopobj=None):
        if op == None: return None
        if op.GetDown(): return op.GetDown()
        if stopobj is None:
            while not op.GetNext() and op.GetUp():
                    op = op.GetUp()
        else:
            while (not op.GetNext() and 
                       op.GetUp() and 
                       op.GetUp() != stopobj):
                op = op.GetUp()
        return op.GetNext()
    
    @staticmethod
    def getActiveObjects(doc):
        """
        Same as BaseDocument.GetSelection(), where GetSelection also selects tags and materials.
        """
        lst = list()
        op = doc.GetFirstObject()
        while op:
            if op.GetBit(c4d.BIT_ACTIVE) == True: 
                lst.append(op)
            op = Helpers.getNextObject(op)
        return lst
    
    @staticmethod
    def findObject(name):
        """Find object with name 'name'"""
        if name is None: return None
        if not isinstance(name, basestring):
            raise TypeError("Expected string, got %s" % type(name))
        doc = documents.GetActiveDocument()
        if not doc: return None
        result = None
        op = doc.GetFirstObject()
        if not op: return None
        curname = op.GetName()
        if curname == name: return op
        op = Helpers.getNextObject(op)
        while op:
            curname = op.GetName()
            if curname == name: 
                return op
            else:
                op = Helpers.getNextObject(op)
        return result
    
    @staticmethod
    def findObjects(name):
        """Find objects with name 'name'"""
        if name is None: return None
        if not isinstance(name, basestring):
            raise TypeError("Expected string, got %s" % type(name))
        doc = documents.GetActiveDocument()
        if not doc: return None
        result = []
        op = doc.GetFirstObject()
        if not op: return result
        while op:
            curname = op.GetName()
            if curname == name: 
                result.append(op)
            op = Helpers.getNextObject(op)
        return result
    
    @staticmethod
    def createObject(typ, name, undo=True):
        obj = None
        try:
            doc = documents.GetActiveDocument()
            if doc is None: return None
            obj = c4d.BaseObject(typ)
            obj.SetName(name)
            c4d.StopAllThreads()
            doc.InsertObject(obj)
            if undo is True:
                doc.AddUndo(c4d.UNDOTYPE_NEW, obj)
            c4d.EventAdd()
        except Exception, e:
            print "*** Caught Exception: %r ***" % e
        return obj
    
    @staticmethod
    def insertUnderNull(objs, grp=None, name="Group", copy=False):
        """
        Inserts objects under a group (null) object, optionally creating the group.
        
        objs  BaseObject      can be a single object or a list of objects
        grp   BaseObject      the group to place the objects under 
                              (if None a new null object will be created)
        name  str             name for the new group
        copy  bool            copy the objects if True
            
        Returns the modyfied/created group on success, None on failure.
        """
        if grp is None:
            grp = Helpers.createObject(c4d.Onull, name)
        if copy == True: 
            objs = [i.GetClone() for i in objs]
        if DEBUG: print "inserting objs into group '%s'" % grp.GetName()
        if isinstance(objs, list):
            for obj in objs:
                obj.Remove()
                obj.InsertUnder(grp)
        else:
            objs.Remove()
            objs.InsertUnder(grp)
        c4d.EventAdd()
        return grp
    
    @staticmethod
    def togglePolySelection(op):
        result = False
        totalpolys = op.GetPolygonCount()
        psel = op.GetPolygonS()
        while psel.HostAlive() == 1:
            for poly in xrange(totalpolys):
                psel.Toggle(poly)
                result = True
            break
        return result
    
    @staticmethod
    def selectAllPolys(op):
        result = False
        totalpolys = op.GetPolygonCount()
        psel = op.GetPolygonS()
        while psel.HostAlive() == 1:
            for poly in xrange(totalpolys):
                psel.Select(poly)
            result = True
            break
        return result
    
    @staticmethod
    def polyToList(p):
        if not isinstance(p,c4d.CPolygon):
            raise TypeError, "CPolygon expected"
        if p.c == p.d: return [p.a,p.b,p.c]
        return [p.a,p.b,p.c,p.d]
    
    @staticmethod
    def listToPoly(l):
        if not isinstance(l, list): 
            raise TypeError, "list or dict expected"
        ln = len(l)
        if ln < 3:
            raise IndexError, "lst must have at least 3 indieces"
        elif ln == 3:
            return c4d.CPolygon(l[0],l[1],l[2])
        else:
            return c4d.CPolygon(l[0],l[1],l[2],l[3])
    
    @staticmethod
    def calcPolyNormal(p, op):
        """
        Calculate the orientation of face normal by using Newell's method.
        See calcVertexNormal for an example of usage within the calling context.
        """
        if not p: raise ValueError("p can't be None")
        if not isinstance(p, c4d.CPolygon):
            raise TypeError("Expected CPolygon, got %s" % type(p))
        N = c4d.Vector(0,0,0)
        lst = Helpers.polyToList(p)
        llen = len(lst)
        #print "lst = %r" % lst
        allp = op.GetAllPoints()
        for i in range(llen):
            x = i
            n = ((i+1) % llen)
            #print x, n
            vtx = allp[lst[x]]
            vtn = allp[lst[n]]
            #print "vtx%d = %r (%s)" % (x, vtx, type(vtx))
            #print "vtn%d = %r (%s)" % (n, vtn, type(vtn))
            N.x += (vtx.y - vtn.y) * (vtx.z + vtn.z)
            N.y += (vtx.z - vtn.z) * (vtx.x + vtn.x)
            N.z += (vtx.x - vtn.x) * (vtx.y + vtn.y)
        return N.GetNormalized()
    
    @staticmethod
    def calcVertexNormal(v, idx, op):
        """
        Calculate the vertex normal by averaging surrounding face normals.
        Usually called from a construct like the following:
        
        for i, point in enumerate(op.GetAllPoints()):
            vn = calcVertexNormal(point, i, op):
        """
        if not v: raise ValueError("v can't be None")
        if not isinstance(v, c4d.Vector):
            raise TypeError("Expected Vector, got %s" % type(v))
        N = c4d.Vector(0,0,0)
        nb = Neighbor()
        nb.Init(op)
        pntpolys = nb.GetPointPolys(idx)
        polys = []
        normals = []
        allp = op.GetAllPolygons()
        for poly in pntpolys:
            x = poly
            poly = allp[poly]
            #print "poly %d = %r (%s)" % (x, poly, type(poly))
            polys.append(poly)
            normal = Helpers.calcPolyNormal(poly, op)
            normals.append(normal)
        ln = len(normals)
        if ln == 0: return N # beware of div by zero
        for n in normals:
            N += n
        N = c4d.Vector(N.x/ln, N.y/ln, N.z/ln)
        return N.GetNormalized()
    
    @staticmethod
    def calcThreePointNormal(v1, v2, v3):
        """
        Calculate the surface normal of a three point plane.
        Doesn't take orientation of neighboring polygons into account.
        """
        try:
            d1 = - v1 + v3
            d2 = - v2 + v3
            result = d1.Cross(d2).GetNormalized()
        except Exception, e:
            raise ValueError("Surface normal calculation failed. The error message was: %r" % e)
        return result
    
    @staticmethod
    def getGlobalPosition(obj):
        return obj.GetMg().off
    
    @staticmethod
    def getGlobalRotation(obj):
        return MatrixToHPB(obj.GetMg())
    
    @staticmethod
    def getGlobalScale(obj):
        m = obj.GetMg()
        return c4d.Vector(m.v1.GetLength(),
                          m.v2.GetLength(),
                          m.v3.GetLength())
    
    @staticmethod
    def setGlobalPosition(obj, pos):
        m = obj.GetMg()
        m.off = pos
        obj.SetMg(m)
    
    @staticmethod
    def setGlobalRotation(obj, rot):
        """
        Please remember, CINEMA 4D handles rotation in radians.
            
        Example for H=10, P=20, B=30:
            
        import c4d
        from c4d import utils
        #...
        hpb = c4d.Vector(utils.Rad(10), utils.Rad(20), utils.Rad(30))
        SetGlobalRotation(obj, hpb) #object's rotation is 10, 20, 30
        """
        m = obj.GetMg()
        pos = m.off
        scale = c4d.Vector( m.v1.GetLength(),
                            m.v2.GetLength(),
                            m.v3.GetLength())
                            
        m = HPBToMatrix(rot)
        
        m.off = pos
        m.v1 = m.v1.GetNormalized() * scale.x
        m.v2 = m.v2.GetNormalized() * scale.y
        m.v3 = m.v3.GetNormalized() * scale.z
        
        obj.SetMg(m)
    
    @staticmethod
    def setGlobalScale(obj, scale):
        m = obj.GetMg()
        
        m.v1 = m.v1.GetNormalized() * scale.x
        m.v2 = m.v2.GetNormalized() * scale.y
        m.v3 = m.v3.GetNormalized() * scale.z
        
        obj.SetMg(m)
    
    @staticmethod
    def setAxisRotation(op, rot, local=False):
        """
        Set the rotation of the object axis (i.e. keeping points in place).
        
        obj   object
        rot   vector
        
        Courtesy of Scott Ayers, source:
        http://www.plugincafe.com/forum/forum_posts.asp?TID=5663&PID=23480#23480
        """
        if op is None: return False
        if not isinstance(rot, c4d.Vector):
            raise TypeError("expected c4d.Vector, got %s" % type(rot))
        currot = op.GetRelRot()
        if VectorEqual(currot, rot): return
        op.SetRelRot(rot)
        if local is True:
            mat = op.GetMl()
        else:
            mat = op.GetMg()
        inv = ~mat  
        points = op.GetAllPoints()
        for i in range(len(points)):    
          points[i] = points[i] * inv
        op.SetAllPoints(points)
        op.Message(c4d.MSG_UPDATE)
        c4d.EventAdd()
    
    @staticmethod
    def centerObjectAxis(obj):
        # check object type
        if obj is None or not isinstance(obj, c4d.PointObject):
            return True
        
        maxpoints = obj.GetPointCount()
        if maxpoints == 0:
            return False
        
        # get center of gravity of object vertices in parent's coordinates
        cg = c4d.Vector(0,0,0)
        scale = 1.0 / maxpoints
        for c in xrange(0, maxpoints):
            cg += (obj.GetPoint(c) * scale)
        ml = obj.GetMl()
        cg = ml * cg # GetMulP
        
        # get inverse of matrix of object and the translation vector to new position
        inv = ml.__invert__()
        trans = inv * (cg - obj.GetRelPos()) # GetMulV
        
        # move object to new position and compensate vertex positions
        obj.SetRelPos(cg)
        for c in xrange(0, maxpoints):
            obj.SetPoint(c, obj.GetPoint(c) - trans)
        obj.Message(c4d.MSG_UPDATE)
        
        # compensate positions of child objects
        child = obj.GetDown()
        while child:
            child = child.GetNext()
            child.SetRelPos(child.GetRelPos() - trans)
        
        return True
    

