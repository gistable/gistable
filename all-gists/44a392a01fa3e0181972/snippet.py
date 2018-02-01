#!/usr/bin/env python

import os
import numpy as np
import vtk
import matplotlib.pyplot as plt


def load_velocity(filename):
    if not os.path.exists(filename):
        return None
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(filename)
    reader.ReadAllVectorsOn()
    reader.Update()

    data = reader.GetOutput()

    # Extracting triangulation information
    triangles = data.GetPolys().GetData()
    points = data.GetPoints()

    # Mapping data: cell -> point
    mapper = vtk.vtkCellDataToPointData()
    mapper.AddInputData(data)
    mapper.Update()
    mapped_data = mapper.GetOutput()

    # Extracting interpolate point data
    udata = mapped_data.GetPointData().GetArray(0)

    ntri = triangles.GetNumberOfTuples()/4
    npts = points.GetNumberOfPoints()
    nvls = udata.GetNumberOfTuples()

    tri = np.zeros((ntri, 3))
    x = np.zeros(npts)
    y = np.zeros(npts)
    ux = np.zeros(nvls)
    uy = np.zeros(nvls)

    for i in xrange(0, ntri):
        tri[i, 0] = triangles.GetTuple(4*i + 1)[0]
        tri[i, 1] = triangles.GetTuple(4*i + 2)[0]
        tri[i, 2] = triangles.GetTuple(4*i + 3)[0]

    for i in xrange(npts):
        pt = points.GetPoint(i)
        x[i] = pt[0]
        y[i] = pt[1]

    for i in xrange(0, nvls):
        U = udata.GetTuple(i)
        ux[i] = U[0]
        uy[i] = U[1]

    return (x, y, tri, ux, uy)

plt.clf()
x, y, tri, ux, uy = load_velocity('U_test-plane.vtk')
plt.tricontour(x, y, tri, ux, 16, linestyles='-',
               colors='black', linewidths=0.5)
plt.tricontourf(x, y, tri, ux, 16)
plt.rc('text', usetex=True)
plt.xlim([0, 0.1])
plt.ylim([0, 0.1])
plt.gca().set_aspect('equal')
plt.gca().tick_params(direction='out', which='both')
plt.minorticks_on()
plt.gca().set_xticklabels([])
plt.gca().set_yticklabels([])
plt.title('$\mathsf{Cavity\ tutorial,\ u_x}$')
plt.savefig("cavity-ux.png", dpi=300, bbox_inches='tight')
plt.savefig("cavity-ux.pdf", bbox_inches='tight')
