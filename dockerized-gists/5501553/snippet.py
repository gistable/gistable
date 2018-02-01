"""
(c) 2013 Marius Retegan

License: BSD-2-Clause

Description: Create a .cube file of the electrostatic potential using ORCA.

Run: python mep.py basename npoints (e.g. python mep.py water 40)

Arguments: basename - file name without the extension;
                      this should be the same for the .gbw and .scfp.
           npoints  - number of grid points per side
                      (80 should be fine)
Dependencies: numpy
"""

#!/usr/bin/env python
import sys
import subprocess
import numpy as np


def read_xyz(xyz):
    atoms = []
    x = []
    y = []
    z = []
    f = open(xyz, "r")
    f.next()
    f.next()
    for line in f:
        data = line.split()
        atoms.append(data[0])
        x.append(float(data[1]))
        y.append(float(data[2]))
        z.append(float(data[3]))
    f.close()
    return atoms, np.array(x), np.array(y), np.array(z)


def read_vpot(vpot):
    v = []
    f = open(vpot, "r")
    f.next()
    for line in f:
        data = line.split()
        v.append(float(data[3]))
    f.close()
    return np.array(v)

if __name__ == "__main__":

    basename = sys.argv[1]
    npoints = int(sys.argv[2])

    ang_to_au = 1.0 / 0.5291772083

    elements = [None,
         "H", "He",
         "Li", "Be",
         "B", "C", "N", "O", "F", "Ne",
         "Na", "Mg",
         "Al", "Si", "P", "S", "Cl", "Ar",
         "K", "Ca",
         "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
         "Ga", "Ge", "As", "Se", "Br", "Kr",
         "Rb", "Sr",
         "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
         "In", "Sn", "Sb", "Te", "I", "Xe",
         "Cs", "Ba",
         "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
         "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
         "Tl", "Pb", "Bi", "Po", "At", "Rn",
         "Fr", "Ra",
         "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No",
         "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Uub"]

    atoms, x, y, z = read_xyz(basename + ".xyz")
    natoms = len(atoms)

    extent = 7.0
    xmin = x.min() * ang_to_au - extent
    xmax = x.max() * ang_to_au + extent
    ymin = y.min() * ang_to_au - extent
    ymax = y.max() * ang_to_au + extent
    zmin = z.min() * ang_to_au - extent
    zmax = z.max() * ang_to_au + extent

    mep_inp = open(basename + "_mep.inp", "w")
    mep_inp.write("{0:d}\n".format(npoints**3))
    for ix in np.linspace(xmin, xmax, npoints, True):
        for iy in np.linspace(ymin, ymax, npoints, True):
            for iz in np.linspace(zmin, zmax, npoints, True):
                mep_inp.write("{0:12.6f} {1:12.6f} {2:12.6f}\n".format(ix, iy, iz))
    mep_inp.close()

    subprocess.check_call(["orca_vpot", basename + ".gbw", basename + ".scfp",
            basename + "_mep.inp", basename + "_mep.out"])

    vpot = read_vpot(basename + "_mep.out")

    cube = open(basename + "_mep.cube", "w")
    cube.write("Generated with ORCA\n")
    cube.write("Electrostatic potential for " + basename + "\n")
    cube.write("{0:5d}{1:12.6f}{2:12.6f}{3:12.6f}\n".format(
        len(atoms), xmin, ymin, zmin))
    cube.write("{0:5d}{1:12.6f}{2:12.6f}{3:12.6f}\n".format(
        npoints, (xmax - xmin) / float(npoints - 1), 0.0, 0.0))
    cube.write("{0:5d}{1:12.6f}{2:12.6f}{3:12.6f}\n".format(
        npoints, 0.0, (ymax - ymin) / float(npoints - 1), 0.0))
    cube.write("{0:5d}{1:12.6f}{2:12.6f}{3:12.6f}\n".format(
        npoints, 0.0, 0.0, (zmax - zmin) / float(npoints - 1)))
    for i, atom in enumerate(atoms):
        index = elements.index(atom)
        cube.write("{0:5d}{1:12.6f}{2:12.6f}{3:12.6f}{4:12.6f}\n".format(
            index, 0.0, x[i] * ang_to_au, y[i] * ang_to_au, z[i] * ang_to_au))

    m = 0
    n = 0
    vpot = np.reshape(vpot, (npoints, npoints, npoints))
    for ix in range(npoints):
        for iy in range(npoints):
            for iz in range(npoints):
                cube.write("{0:14.5e}".format(vpot[ix][iy][iz]))
                m += 1
                n += 1
                if (n > 5):
                    cube.write("\n")
                    n = 0
            if n != 0:
                cube.write("\n")
                n = 0
    cube.close()