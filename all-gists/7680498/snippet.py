from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList
from Products.CMFCore.utils import getToolByName

FAVBY = "collective.favoriting.favoritedby"


def setupAnnotations(context):
    """
    set up the annotations if they haven't been set up
    already. The rest of the functions in here assume that
    this has already been set up
    """
    annotations = IAnnotations(context)

    if not FAVBY in annotations:
        annotations[FAVBY] = PersistentList()

    return annotations


def add_to_favorites(context, userid=None):
    """
    """
    annotations = setupAnnotations(context)
    if userid is None:
        mtool = getToolByName(context, 'portal_membership')
        userid = mtool.getAuthenticatedMember().id

    if userid not in annotations[FAVBY]:
        annotations[FAVBY].append(userid)


def remove_from_favorites(context, userid=None):
    """
    """
    annotations = IAnnotations(context)
    if userid is None:
        mtool = getToolByName(context, 'portal_membership')
        userid = mtool.getAuthenticatedMember().id

    if userid in annotations.get(FAVBY, []):
        annotations[FAVBY].remove(userid)


def is_in_favorites(context, userid=None):
    """
    """
    userids = who_favorites(context)
    if userid is None:
        mtool = getToolByName(context, 'portal_membership')
        userid = mtool.getAuthenticatedMember().id

    return userid in userids


def how_many_favorites(context):
    userids = who_favorites(context)
    return len(userids)


def who_favorites(context):
    annotations = IAnnotations(context)
    return annotations.get(FAVBY, [])
