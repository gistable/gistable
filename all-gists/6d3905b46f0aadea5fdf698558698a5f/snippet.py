#!/bin/env/python3

##########################################
# Subclassing API. The factory will be able
# to deal with two types of features:
# renderers and processors. You would extend
# this class by adding 'has_<feature>' and
# corresponding 'get_type_<feature>' for
# additional feature needing subclassing.
class subclass_api():
    def has_renderer(self):
        """Does the module overrides renderer"""
        return False
    def get_type_renderer():
        """Return the renderer default type"""
        raise Exception("get_type_renderer not subclassed")

    def has_processor(self):
        return False
    def get_type_processor():
        raise Exception("get_type_renderer not subclassed")

##########################################
# Default implementation for main features
# These are the features you may want to override
# depending on circumstances.
class renderer():
    def render_scene(self):
        print ("    render_scene    default")

    def render_object(self):
        print ("    render_object   default")

    def delete_scene(self):
        print ("    delete_scene    default")

class processor():
    def resolve(self):
        print ("    resolve         default")

    def compute(self):
        print ("    compute         default")

    def clear(self):
        print ("    clear           default")

##########################################
# Specialized modules overriding default behavior
# in special circumstances.

class intensive_scene(subclass_api):
    class power_renderer():
        def render_scene(self):
            print ("    render_scene    power")

    def has_renderer(self):
        return True
    def get_type_renderer(self):
        return intensive_scene.power_renderer

    class power_processor():
        def resolve(self):
            print ("    resolve         power")

    def has_processor(self):
        return True
    def get_type_processor(self):
        return intensive_scene.power_processor

class simple_scene(subclass_api):

    class light_processor():
        def clear(self):
            print ("    clear           light")
        def resolve(self):
            print ("    resolve         light")

    def has_processor(self):
        return True
    def get_type_processor(self):
        return simple_scene.light_processor

##########################################
# Factory

class factory():
    """
    This factory will specialize default behavior classes by subclassing
    them with the ones contained in the module loaded, if available for
    the requested type.

    Of course, these modules must respect and implement the subclass_api.
    """
    def __init__(self):
        self.modules = []

    def add_module(self, module):
        if not isinstance(module, subclass_api):
            raise Exception("Overloading modules must be subclassed from 'subclass api'")
        self.modules.append(module)

    def get_object(self, obj_class):
        """
        You get a new object by just specifying the class of the object you want. It must be
        supported by the loaded modules though. In this example, it could be 'renderer' or 'processor'.
        """
        if len(self.modules) == 0:
            return obj_class()
        else:
            # obj_class is base default behavior class
            subclasses     = [obj_class]
            classname      = obj_class.__name__
            typename       = classname.lower()

            for module in self.modules:

                hasobj = getattr(module, "has_%s" % classname)
                getobj = getattr(module, "get_type_%s" % classname)

                # Does the module override this feature so we can sub class it?
                if hasobj():
                    # Yes!, add it to the list of subclasses at the front, so that the last added module
                    # has priority on overloading.
                    subclasses.insert(0, getobj())
                    typename = "%s_%s" % (typename, subclasses[0].__name__)

            newtype = type(typename, tuple(subclasses), {})

            print("Created new type: %s" % typename)
            return newtype()

##########################################
# Demo

def show(header_str, factory):
    print("-----------------------------------")
    print(header_str)
    print("")
    r = factory.get_object(renderer)
    p = factory.get_object(processor)

    r.render_scene()
    r.render_object()
    r.delete_scene()

    p.resolve()
    p.compute()
    p.clear()
    print("")

if __name__ == "__main__":
    # Our modules
    big_engine    = intensive_scene()
    little_engine = simple_scene()

    # Case 1, default
    f = factory()
    show("All default", f)

    # Case 2, override with power renderer
    f = factory()
    f.add_module(big_engine)
    show("Render scene and resolve overridden with power", f)

    # Case 3, override with power renderer, then light renderer
    f = factory()
    f.add_module(big_engine)
    f.add_module(little_engine)
    show("Render scene and resolve overridden, then, 'clear' and 'resolve' are overridden in a light manner, superseding power module for 'resolve'!", f)

    # Case 4, 3 with modules reversed, module loading order matters!
    f = factory()
    f.add_module(little_engine)
    f.add_module(big_engine)
    show("'clear' and 'resolve' are overridden in a light manner, then Render scene and resolve are overridden with power", f)