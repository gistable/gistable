# http://afni.nimh.nih.gov/pub/dist/src/pkundu/meica.libs/nibabel/eulerangles.py
import eulerangles
import c4d

threeMat = c4d.Matrix().Scale(c4d.Vector(1, 1, -1))

def mat2quat(mat):
    mt = threeMat * m
    v1, v2, v3 = mat.v1, mat.v2, mat.v3
    rotMat = [
        [v1.x, v1.y, v1.z],
        [v2.x, v2.y, v2.z],
        [v3.x, v3.y, v3.z]
    ]
    euler = eulerangles.mat2euler(rotMat)
    quat = eulerangles.euler2quat(euler.z, euler.y, euler.x)
    
    return [quat[1], quat[2], quat[3], quat[0]]