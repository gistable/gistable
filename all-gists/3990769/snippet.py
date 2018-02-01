"""Per instance behaviors for Plone's Dexterity.

  <adapter
      for=".interfaces.IBasetype"
      factory=".instancebehaviors.DexterityInstanceBehaviorAssignable" />

Also see:
http://opkode.net/media/blog/plone-and-dexterity-enable-behaviors-per-content-type-instance

"""
from plone.behavior.interfaces import IBehavior
from plone.dexterity.behavior import DexterityBehaviorAssignable
from zope.annotation import IAnnotations
from zope.component import queryUtility
from zope.interface import alsoProvides, noLongerProvides

INSTANCE_BEHAVIORS_KEY = KEY = 'g24.elements.instance_behaviors'

class DexterityInstanceBehaviorAssignable(DexterityBehaviorAssignable):
    """ Support per instance specification of plone.behavior behaviors
    """

    def __init__(self, context):
        super(DexterityInstanceBehaviorAssignable, self).__init__(context)
        annotations = IAnnotations(context)
        self.instance_behaviors = annotations.get(KEY, ())

    def enumerateBehaviors(self):
        self.behaviors = self.fti.behaviors + self.instance_behaviors
        for name in self.behaviors:
            behavior = queryUtility(IBehavior, name=name)
            if behavior is not None:
                yield behavior


def enable_behaviors(obj, behaviors, ifaces):
    """ Enable behaviors on an object.

    :param obj: The Dexterity content object to enable behaviors on.
    :type obj: object
    :param behaviors: Behaviors to be enabled on the object. This is a list of
                      dotted names of behavior schema interfaces.
    :type behaviors: list
    :param ifaces: Behavior marker interfaces belonging to the behaviors to be
                   enabled. This is a list of interface classes.
    :type ifaces: class

    Use it like so:
    >>> from plone.app.event.dx.interfaces import IDXEvent
    >>> enable_behaviors(obj, ['plone.app.event.dx.behaviors.IEventBasic',],
    ...                       [IDXEvent,])

    """
    annotations = IAnnotations(obj)
    instance_behaviors = annotations.get(KEY, ())
    instance_behaviors += behaviors
    annotations[KEY] = instance_behaviors

    for iface in ifaces:
        alsoProvides(obj, iface)

    obj.reindexObject(idxs=('object_provides'))


def disable_behaviors(obj, behaviors, ifaces):
    """ Disable behaviors on an object.

    :param obj: The Dexterity content object to disable behaviors on.
    :type obj: object
    :param behaviors: Behaviors to be disabled on the object. This is a list of
                      dotted names of behavior schema interfaces.
    :type behaviors: list
    :param ifaces: Behavior marker interfaces belonging to the behaviors to be
                   disabled. This is a list of interface classes.
    :type ifaces: class

    Use it like so:
    >>> from plone.app.event.dx.interfaces import IDXEvent
    >>> disable_behaviors(obj, ['plone.app.event.dx.behaviors.IEventBasic',],
    ...                        [IDXEvent,])

    """
    annotations = IAnnotations(obj)
    instance_behaviors = annotations.get(KEY, ())
    instance_behaviors = filter(lambda x: x not in behaviors,
                                instance_behaviors)
    annotations[KEY] = instance_behaviors

    for iface in ifaces:
        noLongerProvides(obj, iface)

    obj.reindexObject(idxs=('object_provides'))
