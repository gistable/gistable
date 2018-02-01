'''
FBXWrapper

This module provides a python wrapper for every method exposed in the FBX plugin.

The arguments for the calls are the same as for the equivalent mel calls, however they can be passed with typical
python syntax, which is translated to mel-style flags and arguments under the hood.  The actual flags and arguments
are documented here:

usage:

    import 
    FBXWrapper.FBXExport(

http://download.autodesk.com/us/fbx/20112/Maya/_index.html

Legalese:

Copyright (c) 2014 Steve Theodore
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

'''

import maya.cmds as cmds
import maya.mel

PLUGIN = 'fbxmaya.mll'


def load_fbx(version_string):
    cmds.loadPlugin(PLUGIN, quiet=True),
    plugin_is_loaded = cmds.pluginInfo(PLUGIN, q=True, v=True) == version_string
    assert plugin_is_loaded


def assert_property(prop_name, value):
    assert FBXProperty(prop_name, q=True) == value


def _FBXCmd(_CMD, *args, **kwargs):
    '''
    Format the arguments into mel-style strings
    '''
    quoted = lambda p: '"%s"' % p if str(p) == p else str(p)  # format strings with quotes
    arg_string = " ".join(map(quoted, args))

    kwarg_fmt = lambda k: "-" + k[0] + " " + quoted(k[1]) if k[0] != 'q' else "-q"
    # special case -q for compatibility with python API

    kwargs_string = " ".join(map(kwarg_fmt, kwargs.items()))

    return maya.mel.eval(_CMD + " " + kwargs_string + " " + arg_string + ";")


def FBXImport(*args, **kwargs):
    return _FBXCmd("FBXImport", *args, **kwargs)


def FBXExport(*args, **kwargs):
    return _FBXCmd("FBXExport", *args, **kwargs)


def FBXResetImport(*args, **kwargs):
    return _FBXCmd("FBXResetImport", *args, **kwargs)


def FBXResetExport(*args, **kwargs):
    return _FBXCmd("FBXResetExport", *args, **kwargs)


def FBXLoadImportPresetFile(*args, **kwargs):
    return _FBXCmd("FBXLoadImportPresetFile", *args, **kwargs)


def FBXLoadExportPresetFile(*args, **kwargs):
    return _FBXCmd("FBXLoadExportPresetFile", *args, **kwargs)


def FBXImportShowUI(*args, **kwargs):
    return _FBXCmd("FBXImportShowUI", *args, **kwargs)


def FBXImportGenerateLog(*args, **kwargs):
    return _FBXCmd("FBXImportGenerateLog", *args, **kwargs)


def FBXImportMode(*args, **kwargs):
    return _FBXCmd("FBXImportMode", *args, **kwargs)


def FBXImportMergeBackNullPivots(*args, **kwargs):
    return _FBXCmd("FBXImportMergeBackNullPivots", *args, **kwargs)


def FBXImportConvertDeformingNullsToJoint(*args, **kwargs):
    return _FBXCmd("FBXImportConvertDeformingNullsToJoint", *args, **kwargs)


def FBXImportHardEdges(*args, **kwargs):
    return _FBXCmd("FBXImportHardEdges", *args, **kwargs)


def FBXImportUnlockNormals(*args, **kwargs):
    return _FBXCmd("FBXImportUnlockNormals", *args, **kwargs)


def FBXImportProtectDrivenKeys(*args, **kwargs):
    return _FBXCmd("FBXImportProtectDrivenKeys", *args, **kwargs)


def FBXImportMergeAnimationLayers(*args, **kwargs):
    return _FBXCmd("FBXImportMergeAnimationLayers", *args, **kwargs)


def FBXImportResamplingRateSource(*args, **kwargs):
    return _FBXCmd("FBXImportResamplingRateSource", *args, **kwargs)


def FBXImportSetMayaFrameRate(*args, **kwargs):
    return _FBXCmd("FBXImportSetMayaFrameRate", *args, **kwargs)


def FBXImportQuaternion(*args, **kwargs):
    return _FBXCmd("FBXImportQuaternion", *args, **kwargs)


def FBXImportSetLockedAttribute(*args, **kwargs):
    return _FBXCmd("FBXImportSetLockedAttribute", *args, **kwargs)


def FBXImportAxisConversionEnable(*args, **kwargs):
    return _FBXCmd("FBXImportAxisConversionEnable", *args, **kwargs)


def FBXImportScaleFactorEnable(*args, **kwargs):
    return _FBXCmd("FBXImportScaleFactorEnable", *args, **kwargs)


def FBXImportScaleFactor(*args, **kwargs):
    return _FBXCmd("FBXImportScaleFactor", *args, **kwargs)


def FBXImportUpAxis(*args, **kwargs):
    return _FBXCmd("FBXImportUpAxis", *args, **kwargs)


def FBXImportAutoAxisEnable(*args, **kwargs):
    return _FBXCmd("FBXImportAutoAxisEnable", *args, **kwargs)


def FBXImportForcedFileAxis(*args, **kwargs):
    return _FBXCmd("FBXImportForcedFileAxis", *args, **kwargs)


def FBXImportCacheFile(*args, **kwargs):
    return _FBXCmd("FBXImportCacheFile", *args, **kwargs)


def FBXImportSkins(*args, **kwargs):
    return _FBXCmd("FBXImportSkins", *args, **kwargs)


def FBXImportShapes(*args, **kwargs):
    return _FBXCmd("FBXImportShapes", *args, **kwargs)


def FBXImportCameras(*args, **kwargs):
    return _FBXCmd("FBXImportCameras", *args, **kwargs)


def FBXImportLights(*args, **kwargs):
    return _FBXCmd("FBXImportLights", *args, **kwargs)


def FBXImportFillTimeline(*args, **kwargs):
    return _FBXCmd("FBXImportFillTimeline", *args, **kwargs)


def FBXImportConstraints(*args, **kwargs):
    return _FBXCmd("FBXImportConstraints", *args, **kwargs)


def FBXImportCharacter(*args, **kwargs):
    return _FBXCmd("FBXImportCharacter", *args, **kwargs)


def FBXExportShowUI(*args, **kwargs):
    return _FBXCmd("FBXExportShowUI", *args, **kwargs)


def FBXExportGenerateLog(*args, **kwargs):
    return _FBXCmd("FBXExportGenerateLog", *args, **kwargs)


def FBXExportFileVersion(*args, **kwargs):
    return _FBXCmd("FBXExportFileVersion", *args, **kwargs)


def FBXExportApplyConstantKeyReducer(*args, **kwargs):
    return _FBXCmd("FBXExportApplyConstantKeyReducer", *args, **kwargs)


def FBXExportQuaternion(*args, **kwargs):
    return _FBXCmd("FBXExportQuaternion", *args, **kwargs)


def FBXExportSkins(*args, **kwargs):
    return _FBXCmd("FBXExportSkins", *args, **kwargs)


def FBXExportShapes(*args, **kwargs):
    return _FBXCmd("FBXExportShapes", *args, **kwargs)


def FBXExportCameras(*args, **kwargs):
    return _FBXCmd("FBXExportCameras", *args, **kwargs)


def FBXExportLights(*args, **kwargs):
    return _FBXCmd("FBXExportLights", *args, **kwargs)


def FBXExportInstances(*args, **kwargs):
    return _FBXCmd("FBXExportInstances", *args, **kwargs)


def FBXExportReferencedContainersContent(*args, **kwargs):
    return _FBXCmd("FBXExportReferencedContainersContent", *args, **kwargs)


def FBXExportBakeComplexStart(*args, **kwargs):
    return _FBXCmd("FBXExportBakeComplexStart", *args, **kwargs)


def FBXExportBakeComplexEnd(*args, **kwargs):
    return _FBXCmd("FBXExportBakeComplexEnd", *args, **kwargs)


def FBXExportBakeComplexStep(*args, **kwargs):
    return _FBXCmd("FBXExportBakeComplexStep", *args, **kwargs)


def FBXExportEmbeddedTextures(*args, **kwargs):
    return _FBXCmd("FBXExportEmbeddedTextures", *args, **kwargs)


def FBXExportConvert2Tif(*args, **kwargs):
    return _FBXCmd("FBXExportConvert2Tif", *args, **kwargs)


def FBXExportInAscii(*args, **kwargs):
    return _FBXCmd("FBXExportInAscii", *args, **kwargs)


def FBXExportBakeComplexAnimation(*args, **kwargs):
    return _FBXCmd("FBXExportBakeComplexAnimation", *args, **kwargs)


def FBXExportBakeResampleAnimation(*args, **kwargs):
    return _FBXCmd("FBXExportBakeResampleAnimation", *args, **kwargs)


def FBXExportUseSceneName(*args, **kwargs):
    return _FBXCmd("FBXExportUseSceneName", *args, **kwargs)


def FBXExportAnimationOnly(*args, **kwargs):
    return _FBXCmd("FBXExportAnimationOnly", *args, **kwargs)


def FBXExportHardEdges(*args, **kwargs):
    return _FBXCmd("FBXExportHardEdges", *args, **kwargs)


def FBXExportTangents(*args, **kwargs):
    return _FBXCmd("FBXExportTangents", *args, **kwargs)


def FBXExportSmoothMesh(*args, **kwargs):
    return _FBXCmd("FBXExportSmoothMesh", *args, **kwargs)


def FBXExportSmoothingGroups(*args, **kwargs):
    return _FBXCmd("FBXExportSmoothingGroups", *args, **kwargs)


def FBXExportFinestSubdivLevel(*args, **kwargs):
    return _FBXCmd("FBXExportFinestSubdivLevel", *args, **kwargs)


def FBXExportInputConnections(*args, **kwargs):
    return _FBXCmd("FBXExportInputConnections", *args, **kwargs)


def FBXExportConstraints(*args, **kwargs):
    return _FBXCmd("FBXExportConstraints", *args, **kwargs)


def FBXExportCharacter(*args, **kwargs):
    return _FBXCmd("FBXExportCharacter", *args, **kwargs)


def FBXExportCacheFile(*args, **kwargs):
    return _FBXCmd("FBXExportCacheFile", *args, **kwargs)


def FBXExportQuickSelectSetAsCache(*args, **kwargs):
    return _FBXCmd("FBXExportQuickSelectSetAsCache", *args, **kwargs)


def FBXExportColladaTriangulate(*args, **kwargs):
    return _FBXCmd("FBXExportColladaTriangulate", *args, **kwargs)


def FBXExportColladaSingleMatrix(*args, **kwargs):
    return _FBXCmd("FBXExportColladaSingleMatrix", *args, **kwargs)


def FBXExportColladaFrameRate(*args, **kwargs):
    return _FBXCmd("FBXExportColladaFrameRate", *args, **kwargs)


def FBXResamplingRate(*args, **kwargs):
    return _FBXCmd("FBXResamplingRate", *args, **kwargs)


def FBXRead(*args, **kwargs):
    return _FBXCmd("FBXRead", *args, **kwargs)


def FBXGetTakeCount(*args, **kwargs):
    return _FBXCmd("FBXGetTakeCount", *args, **kwargs)


def FBXGetTakeIndex(*args, **kwargs):
    return _FBXCmd("FBXGetTakeIndex", *args, **kwargs)


def FBXGetTakeName(*args, **kwargs):
    return _FBXCmd("FBXGetTakeName", *args, **kwargs)


def FBXGetTakeComment(*args, **kwargs):
    return _FBXCmd("FBXGetTakeComment", *args, **kwargs)


def FBXGetTakeLocalTimeSpan(*args, **kwargs):
    return _FBXCmd("FBXGetTakeLocalTimeSpan", *args, **kwargs)


def FBXGetTakeReferenceTimeSpan(*args, **kwargs):
    return _FBXCmd("FBXGetTakeReferenceTimeSpan", *args, **kwargs)


def FBXConvertUnitString(*args, **kwargs):
    return _FBXCmd("FBXConvertUnitString", *args, **kwargs)


def FBXImportConvertUnitString(*args, **kwargs):
    return _FBXCmd("FBXImportConvertUnitString", *args, **kwargs)


def FBXExportConvertUnitString(*args, **kwargs):
    return _FBXCmd("FBXExportConvertUnitString", *args, **kwargs)


def FBXExportAxisConversionMethod(*args, **kwargs):
    return _FBXCmd("FBXExportAxisConversionMethod", *args, **kwargs)


def FBXExportUpAxis(*args, **kwargs):
    return _FBXCmd("FBXExportUpAxis", *args, **kwargs)


def FBXExportScaleFactor(*args, **kwargs):
    return _FBXCmd("FBXExportScaleFactor", *args, **kwargs)


def FBXProperties(*args, **kwargs):
    return _FBXCmd("FBXProperties", *args, **kwargs)


def FBXProperty(*args, **kwargs):
    '''
    Wraps the FBXProperty command, which is unusually useful but needs special argument formatting
    '''
    if kwargs.get('q', False):
        # special case query here because FBX is stupid
        args = (args[0], "-q")
        return _FBXCmd("FBXProperty", *args)
    elif not kwargs.get("v", None) is None:
        quoted = lambda p: '"%s"' % p if str(p) == p else str(p)  # format strings with quotes
        # args = (quoted(args[0]) +  (" -v %s" % quoted(kwargs.get('v')) ), )
        #kwargs[''] = quoted(args[0])

        return _FBXCmd('FBXProperty  "%s"' % args[0], **kwargs)


def FBXExportUseTmpFilePeripheral(*args, **kwargs):
    return _FBXCmd("FBXExportUseTmpFilePeripheral", *args, **kwargs)


def FBXUICallBack(*args, **kwargs):
    return _FBXCmd("FBXUICallBack", *args, **kwargs)


def FBXUIShowOptions(*args, **kwargs):
    return _FBXCmd("FBXUIShowOptions", *args, **kwargs)
