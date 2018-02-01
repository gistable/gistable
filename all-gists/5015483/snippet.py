import sys, getopt, os, string
import math
from odbAccess import *
from abaqusConstants import *
import numpy as np
from numpy import linalg as LA

def get_p1_vector(s):
    '''
    11, 22, 33, 12, 13, 23
    '''
    s = np.array([[s[0],s[3],s[4]],[s[3],s[1],s[5]],[s[4],s[5],s[2]]])
    w, v = LA.eigh(s)
    return v[:,np.argsort(w)[-1]]

def norm(vector):
    """ Returns the norm (length) of the vector."""
    # note: this is a very hot function, hence the odd optimization
    # Unoptimized it is: return np.sqrt(np.sum(np.square(vector)))
    return np.sqrt(np.dot(vector, vector))

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if math.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        else:
            return np.pi
    return angle

def upgrade_if_necessary(job_id):
    odbPath = job_id + '.odb'
    new_odbPath = None
    print odbPath
    if isUpgradeRequiredForOdb(upgradeRequiredOdbPath=odbPath):
        print "Upgrade required"
        path,file = os.path.split(odbPath)
        file = 'upgraded_'+file
        new_odbPath = os.path.join(path,file)
        upgradeOdb(existingOdbPath=odbPath, upgradedOdbPath=new_odbPath)
        odbPath = new_odbPath
    else:
        print "Upgrade not required"
    return odbPath

def odbPrinStressAngle(job_id):
    odbPath = upgrade_if_necessary(job_id) 
    odb = openOdb(path=odbPath)
        
    # retrieve steps from the odb
    grout_instance = odb.rootAssembly.instances['GROUT-1']
    keys = odb.steps.keys()
    for key in keys:
        step = odb.steps[key]
           
        frameRepository = step.frames
        if len(frameRepository):
            for frame in frameRepository:
                print 'Id = %d, Time = %f\n'%(frame.frameId,frame.frameValue)
                fo = frame.fieldOutputs
                S  = fo['S']
                S_grout = S.getSubset(region=grout_instance)
                angle_data = {}
                for value in S_grout.values:                
                    v = get_p1_vector(value.data)
                    # Angle between the first principal stress eigenvector and the
                    # negative z-axis
                    a = angle_between(v, np.array([0.,0.,-1.]))
                    angle_data.setdefault(value.elementLabel,[]).append(a)
                elementLabels = []
                elementData = []
                for key in sorted(angle_data.iterkeys()):
                    elementLabels.append(key)
                    elementData.append(angle_data[key])
                angleField = frame.FieldOutput(name='ANGLE',
                                               description='Principle Stress angle to -Z', 
                                               type=SCALAR)
                angleField.addData(position=INTEGRATION_POINT, 
                                   instance=grout_instance, 
                                   labels=elementLabels, 
                                   data=elementData) 
    odb.save()
    odb.close()
        
if __name__ == '__main__':
        # Get command line arguments.
        usage = "usage: abaqus python odbPrinStressAngle.py <job name>"
        optlist, args = getopt.getopt(sys.argv[1:],'')
        JobID = args[0]
        odbPath = JobID + '.odb'
        print JobID
        print odbPath
        if not odbPath:
                print usage
                sys.exit(0)
        if not os.path.exists(odbPath):
                print "odb %s does not exist!" % odbPath
                sys.exit(0)
        odbPrinStressAngle(JobID)