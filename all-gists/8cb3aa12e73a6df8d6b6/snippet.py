from zope.schema import getFields
from zope.interface import providedBy
from zope.interface import implementedBy
from zope.component import getUtility
from zope.component import queryUtility
from plone.behavior.interfaces import IBehavior
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import resolveDottedName


def get_obj_schema(obj):
    for iface in providedBy(obj).flattened():
        for name, field in getFields(iface).items():
            yield name, field

    assignable = IBehaviorAssignable(obj, None)
    if assignable:
        for behavior in assignable.enumerateBehaviors():
            for name, field in getFields(behavior.interface).items():
                yield name, field


def getBehaviorsFor(context=None, portal_type=None):
    if context is None and portal_type is None:
        return
    if context is None:
        fti = getUtility(IDexterityFTI, name=portal_type)
        for behavior_name in fti.behaviors:
            behavior_interface = None
            behavior_instance = queryUtility(IBehavior, name=behavior_name)
            if not behavior_instance:
                try:
                    behavior_interface = resolveDottedName(behavior_name)
                except (ValueError, ImportError):
                    continue
            else:
                behavior_interface = behavior_instance.interface
            if behavior_interface is not None:
                yield behavior_interface
    else:
        behavior_assignable = IBehaviorAssignable(context, None)
        for behavior_reg in behavior_assignable.enumerateBehaviors():
            yield behavior_reg.interface


def getInterfacesFor(context=None, portal_type=None):
    if context is None and portal_type is None:
        return
    if context is None:
        kwargs = { 'portal_type': portal_type }
        fti = queryUtility(IDexterityFTI, name=portal_type)
    else:
        kwargs = { 'context': context }
        fti = queryUtility(IDexterityFTI, name=context.portal_type)
    if fti is None:
        return

    for interface in implementedBy(resolveDottedName(fti.klass)):
        yield interface
    for schema in getBehaviorsFor(**kwargs):
        yield schema
    yield fti.lookupSchema()
