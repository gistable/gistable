# -*- coding: utf-8 -*-


import re
import anyconfig

from maya.api import OpenMaya as OpenMaya2

##############################################################################


PARENT_CONS_TYPE_ID = OpenMaya2.MTypeId(0x44504152)
##############################################################################


def get_node(x):

    try:
        y = OpenMaya2.MGlobal.getSelectionListByName("{}*".format(x))
    except RuntimeError:
        return ''

    try:
        return y.getDagPath(0)
    except:
        return y.getDependNode(0)


def get_rotation(dag_path, space=OpenMaya2.MSpace.kWorld):

    tra = OpenMaya2.MFnTransform(dag_path)
    return tra.rotation(space, True)  # as quat


def set_rotation(dag_path, v, space=OpenMaya2.MSpace.kWorld):

    tra = OpenMaya2.MFnTransform(dag_path)
    return tra.setrotation(v, space)


def get_translation(dag_path, space=OpenMaya2.MSpace.kWorld):

    tra = OpenMaya2.MFnTransform(dag_path)
    return tra.translation(space)


def set_translation(dag_path, v, space=OpenMaya2.MSpace.kWorld):

    tra = OpenMaya2.MFnTransform(dag_path)
    return tra.setTranslation(v, space)


def match(def_file_name="test.yaml", domain="match_guide_on_bone"):

    map = anyconfig.load(def_file_name)

    for m in map[domain]:
        do_match(m)


def do_match(entry):

    d = get_node(entry['dst'])
    s = get_node(entry['src'])

    if not d or not s:
        print('nothing todo with {}'.format(entry))
        return

    v_s = get_translation(s)
    set_translation(d, v_s)


def connect_on_deformer(def_file_name="test.yaml", domain="bone_on_deformer"):

    map = anyconfig.load(def_file_name)

    for m in map[domain]:
        do_connect(m)


plug_exp = re.compile(
    "(?P<parent_name>\w+)\[(?P<parent_idx>\d+)\]\.(?P<target_name>\w+)")


def _get_plug(node, name):

    if '.' in name:

        m = plug_exp.match(name)
        container_plug = node.findPlug(m.group('parent_name'), False)

        if container_plug.isArray:

            # mind glitch, setting connection index
            #  with "selectAncestorLogicalIndex"
            kid_attr = container_plug.attribute()
            kid_plug = node.findPlug(m.group('target_name'), False)
            kid_plug.selectAncestorLogicalIndex(
                int(m.group('parent_idx')), kid_attr)

    else:
        kid_plug = node.findPlug(name, False)

    return kid_plug


def do_connect(entry):

    d = get_node(entry['dst'])
    s = get_node(entry['src'])

    if not d or not s:
        print('nothing todo with {}'.format(entry))
        return

    cons_name = "{}_parentConstraint".format(d)

    cons_node = OpenMaya2.MFnDependencyNode()
    cons_node.create(PARENT_CONS_TYPE_ID, cons_name)
    x = get_node(cons_name).node()

    dag_mod = OpenMaya2.MDagModifier()
    dag_mod.reparentNode(x, d.node())
    dag_mod.doIt()

    src_node = OpenMaya2.MFnDependencyNode().setObject(s.node())
    dst_node = OpenMaya2.MFnDependencyNode().setObject(d.node())

    d2c = [
        ["jointOrient", "constraintJointOrient"],
        ["rotatePivot", "constraintRotatePivot"],
        ["parentInverseMatrix[0].parentInverseMatrix",
            "constraintParentInverseMatrix"],
        ["rotateOrder", "constraintRotateOrder"],
        ["rotatePivotTranslate", "constraintRotateTranslate"]
    ]

    s2c = [

        ["translate",              "target[0].targetTranslate"],
        ["rotate",                 "target[0].targetRotate"],
        ["scale",                  "target[0].targetScale"],
        ["parentMatrix[0].parentMatrix", "target[0].targetParentMatrix"],
        # ["instObjGroups[0]",       ""],
        ["rotatePivot",            "target[0].targetRotatePivot"],
        ["rotatePivotTranslate",   "target[0].targetRotateTranslate"],
        ["rotateOrder",            "target[0].targetRotateOrder"],
        ["jointOrient",            "target[0].targetJointOrient"],
        ["segmentScaleCompensate", "target[0].targetScaleCompensate"],
        ["inverseScale",           "target[0].targetInverseScale"]

    ]

    c2d = [
        # "inverseScale",
        # "drawOverride",
        # "scale",
        # "worldMatrix[0]",
        # "lockInfluenceWeights",
        # "objectColorRGB",
        # "message",
        # "bindPose",
        ["constraintTranslateX", "translateX"],
        ["constraintTranslateY", "translateY"],
        ["constraintTranslateZ", "translateZ"],
        ["constraintRotateX", "rotateX"],
        ["constraintRotateY", "rotateY"],
        ["constraintRotateZ", "rotateZ"]
        # ["rotateOrder]"
        # "parentInverseMatrix[0]",
        # "rotatePivot",
        # "rotatePivotTranslate",
        # "jointOrient"
    ]

    def _conn(map_array, src, dst):
        for a in map_array:
            # print a[0], a[1]
            src_plug = _get_plug(src, a[0])
            dst_plug = _get_plug(dst, a[1])

            dg_mod.connect(src_plug, dst_plug)

    def offset(node, pos, rot):
        offset_plug_p_x = _get_plug(node, "target[0].targetOffsetTranslateX")
        offset_plug_p_y = _get_plug(node, "target[0].targetOffsetTranslateY")
        offset_plug_p_z = _get_plug(node, "target[0].targetOffsetTranslateZ")

        offset_plug_r_x = _get_plug(node, "target[0].targetOffsetRotateX")
        offset_plug_r_y = _get_plug(node, "target[0].targetOffsetRotateY")
        offset_plug_r_z = _get_plug(node, "target[0].targetOffsetRotateZ")

        offset_plug_p_x.setDouble(pos[0])
        offset_plug_p_y.setDouble(pos[1])
        offset_plug_p_z.setDouble(pos[2])

        if (not rot[0]):
            rot[0] = 0
        if (not rot[1]):
            rot[1] = 0
        if (not rot[2]):
            rot[2] = 0

        offset_plug_r_x.setDouble(rot[0])
        offset_plug_r_y.setDouble(rot[1])
        offset_plug_r_z.setDouble(rot[2])

        print rot

    # dg_mod, must call doIt() later.
    dg_mod = OpenMaya2.MDGModifier()

    # dst to cns, for some settings
    _conn(d2c, dst_node, cons_node)

    # src to cos
    _conn(s2c, src_node, cons_node)

    # cons to dst
    _conn(c2d, cons_node, dst_node)

    print d

    ####################################################################
    # store transforms for offset
    posspace = OpenMaya2.MSpace.kTransform
    rotspace = OpenMaya2.MSpace.kTransform

    original_pos = get_translation(d, posspace)
    original_rot = get_rotation(d, rotspace)

    joint_orient_x = _get_plug(dst_node, "jointOrientX").asFloat()
    joint_orient_y = _get_plug(dst_node, "jointOrientY").asFloat()
    joint_orient_z = _get_plug(dst_node, "jointOrientZ").asFloat()
    joint_orient_eul = OpenMaya2.MEulerRotation(
        joint_orient_x, joint_orient_y, joint_orient_z)

    joint_orient = OpenMaya2.MQuaternion().setValue(joint_orient_eul)

    dg_mod.doIt()

    # maintain offset
    _pos = get_translation(d, posspace)
    _rot = get_rotation(d, rotspace)

    diff_pos = original_pos - _pos
    diff_rot = original_rot * _rot.invertIt()
    diff_pos = diff_pos.rotateBy(joint_orient.invertIt()).rotateBy(diff_rot)

    offset(cons_node, diff_pos, diff_rot.asEulerRotation())
