#!/usr/bin/env python

'''
WRF2VTK.py
Jonathan Beezley
April 27, 2011

This is a python script to convert WRF-Fire output files into a series
of vts (vtk structured grid) files.  This script depends on the following
python modules:

vtk
netCDF4

All variables are interpolated (linearly) to cell centered coordinates.  At
most three files will be output at each time step.  One for 3D atmospheric
arrays, and one for 2D atmospheric and fire grid surface arrays.  All time
steps are numbered sequentially and a *.pvd file is created containing a 
list of all files created as well as the simulation time created from the 
DT attribute of the wrfout files.  The pvd file can be used with paraview
to generate an animation.

Common usage:

python WRF2VTK.py -v FGRNHFX,GRNHFX,NFUEL_CAT -w surface_wind:UF:VF,atm_wind:U:V:W wrfout_d01*

Try `python WRF2VTK.py -h` for a complete list of options.
'''

from netCDF4 import Dataset
import numpy as np
import optparse

import vtk
from vtk.util import numpy_support

import sys

global current_output_time
current_output_time=0

def getGridInfo(file,varname):
    var=file.variables[varname]
    dims=var.dimensions[1:]
    if 'south_north_subgrid' in dims:
        return 'fire'
    elif len(dims) == 2:
        return 'surface'
    elif len(dims) == 3:
        return 'atm'
    else:
        raise Exception('Unsupported variable type %s'%varname)

def getSRatio(f):
    try:
        srx=len(f.dimensions['west_east_subgrid'])/(len(f.dimensions['west_east'])+1)
        sry=len(f.dimensions['south_north_subgrid'])/(len(f.dimensions['south_north'])+1)
    except:
        print >> sys.stderr, "WARNING: could not determine subgrid ratio, using 1."
        srx=1
        sry=1
    return srx,sry

def readGrid(file,gridname,itime=0):
    print 'Creating %s grid'%gridname
    try:
        dx=file.DX
        dy=file.DY
    except:
        print >> sys.stderr, "Could not read spatial resolution, setting to 1."
        dx=1
        dy=1
    if gridname == 'fire':
        srx,sry=getSRatio(file)
        dx=dx/float(srx)
        dy=dy/float(sry)
        nx=len(file.dimensions['west_east_subgrid'])-srx
        ny=len(file.dimensions['south_north_subgrid'])-sry
    else:
        nx=len(file.dimensions['west_east'])
        ny=len(file.dimensions['south_north'])
    x=(np.arange(nx,dtype=np.float32)+.5)*dx
    y=(np.arange(ny,dtype=np.float32)+.5)*dy
    X,Y=np.meshgrid(x,y)
    X.shape=(1,)+X.shape
    Y.shape=(1,)+Y.shape
    X=transposeVar(X)
    Y=transposeVar(Y)
    #print X.shape,Y.shape
    if gridname == 'atm':
        c=readFromNC(file,itime,('PH','PHB'))
        ph=c['PH']
        phb=c['PHB']
        Z=(ph+phb)/9.81
        X=np.repeat(X,Z.shape[0],0)
        Y=np.repeat(Y,Z.shape[0],0)
        #print X.shape,Y.shape
    else:
        if gridname == 'fire':
            Z=readFromNC(file,0,('ZSF',))['ZSF']
        else:
            Z=readFromNC(file,0,('HGT',))['HGT']
        Z.shape=X.shape
    return vectorize([X,Y,Z])

def openNCFile(filename):
    return Dataset(filename,'r')

def transposeVar(var):
    #dims=np.arange(var.ndim-1,-1,-1)
    return var#.transpose(dims)

def readFromNC(f,itime,vars):
    out={}
    for vname in vars:
        print 'Reading %s at timestep %i'%(vname,itime)
        var=f.variables[vname]
        vardata=var[itime,:].squeeze()
        if vardata.ndim != 2 and vardata.ndim != 3:
            raise Exception('Only 2 or 3 dimensional variables are supported (%s).'%vname)
        if 'west_east_stag' in var.dimensions:
            vardata=0.5*(vardata[...,1:]+vardata[...,:-1])
        if 'south_north_stag' in var.dimensions:
            vardata=0.5*(vardata[...,1:,:]+vardata[...,:-1,:])
        if 'bottom_top_stag' in var.dimensions:
            vardata=0.5*(vardata[...,1:,:,:]+vardata[...,:-1,:,:])
        if 'south_north_subgrid' in var.dimensions:
            if not 'west_east_subgrid' in var.dimensions or vardata.ndim != 2:
                raise Exception('Invalid fire grid variable (%s).'%vname)
            srx,sry=getSRatio(f)
            #print srx,sry,vardata.shape
            vardata=vardata[...,:-sry,:-srx]
            #print vardata.shape
        vardata=transposeVar(vardata)
        if vardata.ndim == 2:
            vardata.shape=(1,)+vardata.shape
        out[vname]=vardata
    return out

def vectorize(vars):
    if len(vars) == 2 and vars[0].shape == vars[1].shape:
        vars.append(np.zeros(vars[0].shape))
    elif len(vars) == 3 and vars[0].shape == vars[1].shape == vars[2].shape:
        pass
    else:
        print vars[0].shape,vars[1].shape#,vars[2].shape
        raise Exception('Invalid vector.')
    v=np.ndarray(vars[0].shape+(3,),dtype=vars[0].dtype)
    v[...,0]=vars[0]
    v[...,1]=vars[1]
    v[...,2]=vars[2]
    return v

def parseVectors(vectors):
    if isinstance(vectors,str):
        vectors=vectors.split(',')
    out={}
    for v in vectors:
        vec=v.strip().split(':')
        out[vec[0].strip()]=[w.strip() for w in vec[1:]]
    return out

def parseVariables(variables):
    if isinstance(variables,str):
        variables=variables.split(',')
    return [v.strip() for v in variables]

def parseFiles(files):
    if isinstance(files,str):
        files=files.split(',')
    return [f.strip() for f in files]

def numpy_to_vtk(vdata,vname=None,vector=False):
    #print 'Converting %s to vtk array'%vname
    shp=vdata.shape
    if not vdata.flags['C_CONTIGUOUS']:
        deep=1
    else:
        deep=0
    #print 'deep=%i'%deep
    vdata=np.ascontiguousarray(vdata,dtype=vdata.dtype)
    if vector:
        vdata.shape=vdata.size/3,3
    else:
        vdata.shape=vdata.size
    vtkdata=numpy_support.numpy_to_vtk(vdata, deep=deep)
    if vname:
        vtkdata.SetName(vname)
    vdata.shape=shp
    return vtkdata

def getVTKsgrid(grid):
    shape=[i for i in reversed(grid.shape[:-1])]
    print 'Creating vtk structured grid with shape %s'%str(shape)
    pts=getVTKpoints(grid)
    sgrid=vtk.vtkStructuredGrid() #@UndefinedVariable
    sgrid.SetPoints(pts)
    sgrid.SetExtent(0,shape[0]-1,0,shape[1]-1,0,shape[2]-1)
    return sgrid

def addVTKvariable(sgrid,varname,vardata,vector=False):
    shape=[i for i in reversed(vardata.shape[:3])]
    if len(vardata.shape) == 4:
        shape.append(vardata.shape[3])
    print 'Adding variable %s with shape %s'%(varname,str(shape))
    vdata=numpy_to_vtk(vardata,varname,vector)
    sgrid.GetPointData().AddArray(vdata)

def getVTKpoints(grid):
    shape=grid.shape
    #nlen=np.prod(shape[:-1])
    #grid.shape=(nlen,shape[-1])
    vgrid=numpy_to_vtk(grid,vector=True)
    pts=vtk.vtkPoints() #@UndefinedVariable
    pts.SetData(vgrid)
    return pts

def writeVTKsgrid(filename,sgrid,compress=True):
    w=vtk.vtkXMLStructuredGridWriter() #@UndefinedVariable
    print 'Writing VTK file %s'%filename
    w.SetFileName(filename)
    w.SetInput(sgrid)
    if compress:
        w.SetCompressorTypeToZLib()
    else:
        w.SetCompressorTypeToNone()
    w.Update()
    w.Write()

def writeVTK(grids,variables,vectors,vardata,output,filefmt,nocompress,**kwdargs):
    global current_output_time
    current_output_time=current_output_time+1
    files={}
    for gridname in grids:
        g,vars=grids[gridname]
        sgrid=getVTKsgrid(g)
        for vname in set(vars).intersection(variables):
            addVTKvariable(sgrid,vname,vardata[vname])
        for vecname in vectors:
            vector=vectors[vecname]
            if vector and vector[0] in vars:
                if not all([(iv in vars) for iv in vector]):
                    raise Exception('Not all variables in vector %s are on the same grid.'%vecname)
                vecdata=vectorize([vardata[v] for v in vector])
                addVTKvariable(sgrid,vecname,vecdata,vector=True)
        files[gridname]=filefmt%{'grid':gridname,'time':current_output_time}+'.vts'
        writeVTKsgrid(files[gridname],sgrid,not nocompress)
    return files

def writePVD(filename,files,dt=1,compression=True):
    outfile=open(filename,'w')
    if sys.byteorder == 'little':
        byteorder='LittleEndian'
    else:
        byteorder='BigEndian'
    if compression:
        compressor=' compressor="vtkZLibDataCompressor"'
    else:
        compressor=''
    header='<?xml version="1.0"?>\n'+ \
           '<VTKFile type="Collection" version="0.1" byte_order="%s"%s>\n' % (byteorder,compressor) + \
           '<Collection>\n'
    footer='</Collection>\n'+'</VTKFile>'
    filefm='<DataSet timestep="%f" group="" part="" file="%s"/>\n'
    outfile.write(header)
    print 'Creating group file %s'%filename
    for i in xrange(len(files)):
        outfile.write(filefm % (i*dt,files[i]))
    outfile.write(footer)

def main(files,variables,vectors,time=-1,nocompress=False,output='wrfout'):
    time=int(time)
    variables=parseVariables(variables)
    vectors=parseVectors(vectors)
    files=parseFiles(files)
    ofiles=[]
    atime=time
    otime=0
    for f in files:
        print 'Reading from %s'%f
        file=openNCFile(f)
        if time == -1:
            time = np.arange(len(file.dimensions['Time']))
        else:
            time=[time]
        allvars=sum(vectors.values(),[])
        allvars=set(allvars).union(variables)
        for t in time:
            grids={}
            for var in allvars:
                gridname=getGridInfo(file,var)
                try:
                    g=grids[gridname]
                except KeyError:
                    g=(readGrid(file,gridname,t),[])
                    grids[gridname]=g
                g[1].append(var)
            vardata=readFromNC(file,t,allvars)
            otime=otime+1
            ofile=writeVTK(variables=variables,vardata=vardata,vectors=vectors,
                           output=output,filefmt='%(grid)s_%(time)05i',
                           nocompress=nocompress,grids=grids,itime=otime)
            ofiles.append(ofile)
        time=atime
    gridnames=ofiles[0].keys()
    try:
        dt=file.DT
    except:
        dt=1
    for n in gridnames:
        writePVD('%s.pvd'%n,[ofiles[i][n] for i in xrange(len(ofiles))],
                 compression=not nocompress,dt=dt)


if __name__ == '__main__':
    parser=optparse.OptionParser(usage='usage: %prog [options] filename')
    
    parser.add_option('-v','--variables',action="store",type="string",dest='variables',
                    default='',help='A comma separated list of variables')
    parser.add_option('-w','--vectors',action='store',type='string',dest='vectors',
                      default='',help='A comma separated list of vectors (i.e. -w wind1:U:V:W,wind2:UF:VF)')
    parser.add_option('-t','--time',action="store",type="string",dest="time",
                      default="-1",help='The time slice to convert [default convert all time steps]')
    parser.add_option('-n','--nocompress',action='store_true',dest='nocompress',
                      default=False,help='Do not save as a compressed file')
    #parser.add_option('-s','--scale',action="store",type="float",dest="scale",
    #                  default=scale_degree,help="vertical to horizontal scaling factor")
    
    (options,args)= parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        raise Exception('NetCDF file name required.')
    
    opt={'variables':options.variables,'vectors':options.vectors,
         'time':options.time,'nocompress':options.nocompress}
    main(args,**opt)
