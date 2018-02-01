#!/usr/bin/env python

freecadfunctions="""#!/usr/env/bin python
#python 2
import FreeCAD,Part
def pointstopoles1D(points):
    return zip(*[(FreeCAD.Vector(point[0:3]),point[3]) for point in points])

def pointstopoles(points,cu):
    poles=[]
    weights=[]
    for dontcare in xrange(cu):
        poles.append([])
        weights.append([])
    for i,point in enumerate(points):
        u = i % cu
        v = i // cu
        poles[u].append(FreeCAD.Vector(point[0:3]))
        weights[u].append(point[3])
    return poles,weights

def mults(npoles,degree,isperiodic=False,bezier=False,endpoint=False):
    if isperiodic: #and uniform
        multv = (1,) * (npoles +1)
    elif endpoint: #quasi-uniform
        multv=(degree+1,)+(1,)*(npoles - degree-1)+(degree+1,)
    elif bezier:
       #what OCC describes as picewise bezier
       k = 1 + (npoles -1) / degree
       multv=(degree+1,)+(degree,)*(k-2)+(degree+1,)
    else: #uniform
        multv=(1,)*(npoles+degree+1)
    #print '%s deg=%d pol=%d sum=%d' % (multv ,degree, npoles, (sum(multv)-degree-1))
    return multv

def importblenderspline(d1,doc=None,name=None,showpoles=False):
    import FreeCAD
    if name is None:
        name = 'Surface' if d1['order_v']>0 else 'Curve'
    doc = doc or FreeCAD.activeDocument() or FreeCAD.newDocument()
    obj = doc.addObject('Part::Spline',name)
    obj.Shape = blendersplinecurve(d1).toShape()
    if showpoles:
        obj.ViewObject.ControlPoints = True

def blendersplinecurve(d1):
    points=d1['points']
    cu=d1['point_count_u']
    cv=d1['point_count_v']
    degu=d1['order_u']-1
    degv=d1['order_v']-1
    uperiodic=d1['use_cyclic_u']
    vperiodic=d1['use_cyclic_v']
    if degv != -1:
        poles,weights= pointstopoles(points,cu)
        bss=Part.BSplineSurface()
        umults=mults(cu,degu,uperiodic,d1['use_bezier_u'],d1['use_endpoint_u'])
        vmults=mults(cv,degv,vperiodic,d1['use_bezier_v'],d1['use_endpoint_v'])
        if d1['use_bezier_u'] and (sum(umults)-degu-1) != cu or d1['use_bezier_v'] and (sum(vmults)-degv-1) != cv:
             raise ValueError#would fail later because of mults and points mismatch
        bss.buildFromPolesMultsKnots(poles,umults, vmults,uperiodic=uperiodic, vperiodic=vperiodic, udegree=degu, vdegree=degv, weights=weights)
        return bss
    else:
        poles,weights = pointstopoles1D(points)
        bsc=Part.BSplineCurve()
        if d1['use_bezier_u'] and degu==3: #blender is doing something very strange
            poles=poles[1:]
            weights=weights[1:]
            cu-=1
        umults=mults(cu,degu,uperiodic,d1['use_bezier_u'],d1['use_endpoint_u'])
        if d1['use_bezier_u'] and (sum(umults)-degu-1) != cu: #to many poles, 
            cu=sum(umults)-degu-1
            poles = poles[:cu]
            weights = weights[:cu]
        try:
            bsc.buildFromPolesMultsKnots(poles,umults,periodic=uperiodic,degree=degu,weights=weights)
        except:
            print umults,' ',len(poles)
            raise
        return bsc

"""
def spline2dict(spline):
    d1={}
    for attr in ('order_u', 'order_v', 'point_count_u', 'point_count_v',\
        'use_bezier_u', 'use_bezier_v', 'use_cyclic_u', 'use_cyclic_v', \
        'use_endpoint_u', 'use_endpoint_v'):
        d1[attr]=spline.__getattribute__(attr)
    d1['points']=tuple((tuple(p.co) for p in spline.points))
    return d1

def selection2dictionary():
    import bpy
    nurbslist=[]
    for ob in bpy.context.selected_objects:
        if ob.type == 'SURFACE':
            name = ob.name
            data = ob.data
            if len(data.splines) == 1:
                nurbslist.append((name,spline2dict(data.splines[0])))
            else:
                raise ValueError("Not one spline")
    return nurbslist

def writeFreeCADMacro(nurbslist,filename):
    outfile=open(filename,'w')
    outfile.write(freecadfunctions)
    for name,d1 in nurbslist:
        outfile.write('importblenderspline(%s,name="%s")\n' % (repr(d1),name))
    outfile.close()

if __name__ == '__main__':
    writeFreeCADMacro(selection2dictionary(),'importnurbstofreecad.py')
