'''
rename_selected_relation_box.py
Written by Alex Forsythe (awforsythe.com)

When executed, attempts to locate any selected box within any relation
constraint in the scene. If a selected relation box is found, prompts the user
to enter a new name for that box. Allows relation boxes to be given more
descriptive names. I'd recommend binding this script to a keyboard shortcut
(see MotionBuilder/bin/config/Scripts/ActionScript.txt) for quick access.
'''

from pyfbsdk import *

def get_first(f, xs):
    '''
    Returns the first x in xs for which f returns True, or else None.
    '''
    for x in xs:
        if f(x):
            return x
    return None
   
def get_selected_relation_box():
    '''
    Returns a relation constraint box which has been selected by the user, or
    None if no relation boxes are selected.
    '''
    for relation in [c for c in FBSystem().Scene.Constraints if c.Is(FBConstraintRelation_TypeInfo())]:
        box = get_first(lambda box: box.Selected, relation.Boxes)
        if box:
            return box
    return None

def get_new_box_name(box):
    '''
    Prompts the user to enter a new name for the given box. Returns the new
    name if the user confirms the rename operation, or None if the user
    cancels.
    '''    
    button, string = FBMessageBoxGetUserValue(
        'Rename Box?',
        'Current name: %s' % box.Name,
        box.Name,
        FBPopupInputType.kFBPopupString,
        'Rename',
        'Cancel')
    return string if button == 1 else None

def rename_selected_relation_box():
    '''
    Prompts the user to enter a new name for a selected relation constraint
    box. If no boxes are selected, has no effect.
    '''    
    box = get_selected_relation_box()
    if box:
        name = get_new_box_name(box)
        if name:
            box.Name = name  

if __name__ in ('__main__', '__builtin__'):
    rename_selected_relation_box()
