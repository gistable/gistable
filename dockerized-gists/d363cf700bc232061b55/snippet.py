from functools import partial
from collections import Iterable

def component(Component):
    """
    {
        label = gtk.Label('label')
        label.set_size_request(640, 480)
        label.set_justify(gtk.JUSTIFY_FILL)
    } =>
    {
        Label = component(gtk.Label)
        label = Label(
            'label',
            size_request=(640, 480),
            justify=gtk.JUSTIFY_FILL
        )
    }
    """
    def new_style_component(*args, **kwargs):
        component = Component(*args)

        def set_property(name, values):
            getattr(
                component,
                "set_{name}".format(name=name)
            )(
                *(values if isinstance(values, Iterable) else (values, ))
            )

        map(partial(apply, set_property), kwargs.iteritems())

        return component

    return new_style_component