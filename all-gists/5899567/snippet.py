# a simple Python plugin loading system
# see http://stackoverflow.com/questions/14510286/plugin-architecture-plugin-manager-vs-inspecting-from-plugins-import

class PluginMount(type):
    """
    A plugin mount point derived from:
        http://martyalchin.com/2008/jan/10/simple-plugin-framework/
    Acts as a metaclass which creates anything inheriting from Plugin
    """

    def __init__(cls, name, bases, attrs):
        """Called when a Plugin derived class is imported"""

        if not hasattr(cls, 'plugins'):
            # Called when the metaclass is first instantiated
            cls.plugins = []
        else:
            # Called when a plugin class is imported
            cls.register_plugin(cls)

    def register_plugin(cls, plugin):
        """Add the plugin to the plugin list and perform any registration logic"""

        # create a plugin instance and store it
        # optionally you could just store the plugin class and lazily instantiate
        instance = plugin()

        # save the plugin reference
        cls.plugins.append(instance)

        # apply plugin logic - in this case connect the plugin to blinker signals
        # this must be defined in the derived class
        instance.register_signals()


class Plugin(object):
    """A plugin which must provide a register_signals() method"""
    __metaclass__ = PluginMount


class MyPlugin(Plugin):
    def register_signals(self):
        print "Class created and registering signals"

    def other_plugin_stuff(self):
        print "I can do other plugin stuff"


for plugin in Plugin.plugins:
    plugin.other_plugin_stuff()