from zope.component import getUtility
from zope.interface import Interface
from zope.interface import alsoProvides

from plone.registry.interfaces import IRegistry
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm

from plone.z3cform import layout

from z3c.form import field
from z3c.form import group


class IGeneralSettings(Interface):
    """Some general settings.

    These fields will appear on the 'Default' tab.
    """

    # schema fields ...


class ILessGeneralSettings1(Interface):
    """Some less general settings."""

    # schema fields ...


class ILessGeneralSettings2(Interface):
    """Some other less general settings."""

    # schema fields ...


class IFormSchema(IGeneralSettings,
                  ILessGeneralSettings1,
                  ILessGeneralSettings2):
    """The form schema contains all settings."""


class FormGroup1(group.Group):
    label = u"Less general 1"
    fields = field.Fields(ILessGeneralSettings1)


class FormGroup2(group.Group):
    label = u"Less general 2"
    fields = field.Fields(ILessGeneralSettings2)


class MyForm(RegistryEditForm):
    schema = IFormSchema
    fields = field.Fields(IGeneralSettings)
    groups = FormGroup1, FormGroup2

    label = u"Settings"

    def getContent(self):
        return AbstractRecordsProxy(self.schema)


ControlPanel = layout.wrap_form(MyForm, ControlPanelFormWrapper)


class AbstractRecordsProxy(object):
    """Multiple registry schema proxy.

    This class supports schemas that contain derived fields. The
    settings will be stored with respect to the individual field
    interfaces.
    """

    def __init__(self, schema):
        state = self.__dict__
        state["__registry__"] = getUtility(IRegistry)
        state["__proxies__"] = {}
        state["__schema__"] = schema
        alsoProvides(self, schema)

    def __getattr__(self, name):
        try:
            field = self.__schema__[name]
        except KeyError:
            raise AttributeError(name)
        else:
            proxy = self._get_proxy(field.interface)
            return getattr(proxy, name)

    def __setattr__(self, name, value):
        try:
            field = self.__schema__[name]
        except KeyError:
            self.__dict__[name] = value
        else:
            proxy = self._get_proxy(field.interface)
            return setattr(proxy, name, value)

    def __repr__(self):
        return "<AbstractRecordsProxy for %s>" % self.__schema__.__identifier__

    def _get_proxy(self, interface):
        proxies = self.__proxies__
        return proxies.get(interface) or \
               proxies.setdefault(interface, self.__registry__.\
                                  forInterface(interface))
