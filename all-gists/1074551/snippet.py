import sys
import os
import odbAccess
import numpy as NP
import math

def open_odb(odbPath):
    base, ext = os.path.splitext(odbPath)
    odbPath = base + '.odb'
    new_odbPath = None
    if odbAccess.isUpgradeRequiredForOdb(upgradeRequiredOdbPath=odbPath):
        print('odb %s needs upgrading' % (odbPath,))
        path,file_name = os.path.split(odbPath)
        file_name = base + "_upgraded.odb"
        new_odbPath = os.path.join(path,file_name)
        odbAccess.upgradeOdb(existingOdbPath=odbPath, upgradedOdbPath=new_odbPath)
        odbPath = new_odbPath
    odb = odbAccess.openOdb(path=odbPath, readOnly=True)
    return odb

def max_result(odb, result):
    result_field, result_invariant = result
    _max = -1.0e20
    for step in odb.steps.values():
        print 'Processing Step:', step.name
        for frame in step.frames:
            if frame.frameValue > 0.0:
                allFields = frame.fieldOutputs
                if (allFields.has_key(result_field)):
                    stressSet = allFields[result_field]
                    for stressValue in stressSet.values:
                        if result_invariant:
                            if hasattr(stressValue, result_invariant.lower()):
                                val = getattr(stressValue,result_invariant.lower())
                            else:
                                raise ValueError('Field value does not have invariant %s' % (result_invariant,))
                        else:
                            val = stressValue.data
                        if ( val > _max):
                            _max = val
                else:
                    raise ValueError('Field output does not have field %s' % (results_field,))
    return _max

if __name__ == '__main__':
    odb_name = sys.argv[1]
    print odb_name
    odb = open_odb(odb_name)
    max_mises = max_result(odb,('S','mises'))
    max_peeq = max_result(odb,('PEEQ',''))
    print max_mises, max_peeq
