import os
import subprocess
import tempfile

import numpy as np

def processMatrix(in_, funcStr):
    """Process the given matrix with MATLAB.

    Uses temporary files to save the real and imaginary parts of the
    matrix, then invokes MATLAB from the commandline to process the
    matrix with the code given in funcStr.  The output is then saved
    into two other temporary files and loaded back into python.
    
    funcStr is a string of MATLAB code that will be executed.  In that
    code, the matrix to be operated on is called 'in' and the result should
    be stored into the variable 'out'.  The real and imaginary parts of
    'out' will then be saved into temporary files, loaded back into
    python, and returned as a numpy array.
    """
    in_re_file, in_re_name = tempfile.mkstemp(prefix='mlab_', text=True)
    in_im_file, in_im_name = tempfile.mkstemp(prefix='mlab_', text=True)
    out_re_file, out_re_name = tempfile.mkstemp(prefix='mlab_', text=True)
    out_im_file, out_im_name = tempfile.mkstemp(prefix='mlab_', text=True)

    os.close(in_re_file)
    os.close(in_im_file)
    os.close(out_re_file)
    os.close(out_im_file)

    print 'in_re:', in_re_name
    print 'in_im:', in_im_name
    print 'out_re:', out_re_name
    print 'out_im:', out_im_name

    np.savetxt(in_re_name, in_.real)
    np.savetxt(in_im_name, in_.imag)

    subprocess.call(["matlab",
                     "-nodesktop",
                     "-nosplash",
                     "-wait",
                     "-r",
                     
                     "in_re = load('%s'); "
                     "in_im = load('%s'); "
                     "in = in_re + 1i*in_im; "
                     "%s; "
                     "out_re = real(out); "
                     "out_im = imag(out); "
                     "save '%s' out_re -ascii -double; "
                     "save '%s' out_im -ascii -double; "
                     "quit" % (in_re_name, in_im_name, funcStr, out_re_name, out_im_name)
                     ])

    out_re = np.loadtxt(out_re_name)
    out_im = np.loadtxt(out_im_name)

    out = out_re + 1j*out_im
    return out


def getPhysical(rho):
    """An example of using processMatrix: compute a physical density matrix using semidefinite programming"""
    funcStr = (
        "rho = in; "
        "[m n] = size(rho); "
        "rhoVar = sdpvar(n, n, 'hermitian', 'complex'); "
        
        # constraints: unit trace and positive semidefinite
        "F = set(trace(rhoVar) == 1); "
        "F = F + set(rhoVar >= 0); "
        
        "solvesdp(F, trace((rhoVar-rho) * (rhoVar-rho))); "
    
        # twoNormDist = sqrt(double(real(trace((rhoVar-rho) * (rhoVar-rho)))));
        "out = double(rhoVar); "
    )
    return processMatrix(rho, funcStr)
