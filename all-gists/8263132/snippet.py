#!/usr/bin/env python

"""Convert UnstructuredGrid in .vtk files to STL files."""

import sys
import vtk

if len(sys.argv) < 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
    print('Usage: vtk-unstructuredgrid-to-stl.py <input.vtk> <output.stl>')
    sys.exit(1)

reader = vtk.vtkUnstructuredGridReader()
reader.SetFileName(sys.argv[1])

surface_filter = vtk.vtkDataSetSurfaceFilter()
surface_filter.SetInputConnection(reader.GetOutputPort())

triangle_filter = vtk.vtkTriangleFilter()
triangle_filter.SetInputConnection(surface_filter.GetOutputPort())

writer = vtk.vtkSTLWriter()
writer.SetFileName(sys.argv[2])
writer.SetInputConnection(triangle_filter.GetOutputPort())
writer.Write()
