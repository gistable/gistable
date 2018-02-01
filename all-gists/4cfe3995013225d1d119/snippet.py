#
# A plugin to setup capture interfaces
# The plugin is off by default. To enable it, add "interfacesetup.enabled=1" to broctl.cfg.
#

import BroControl.plugin

class InterfaceSetupPlugin(BroControl.plugin.Plugin):
    def __init__(self):
        super(InterfaceSetupPlugin, self).__init__(apiversion=1)

    def name(self):
        return "InterfaceSetupPlugin"

    def prefix(self):
        return "interfacesetup"

    def pluginVersion(self):
        return 1

    def init(self):
        if self.getOption("enabled") == "0":
            return False

        return True

    def options(self):
        return [("mtu", "int", "9710", "Interface MTU"),
                ("enabled", "string", "0", "Set to enable plugin")]

    def cmd_start_pre(self, nodes):
        if not nodes:
            return
        
        mtu = self.getOption("mtu")
        self.message("InterfaceSetupPlugin: mtu=%s" % (mtu))

        host_nodes = {}
        for n in nodes:
            if n.interface:
                host_nodes[(n.host, n.interface)] = n

        cmds = []
        for n in host_nodes.values():
            cmd = "/sbin/ifconfig %s up mtu %s" % (n.interface, mtu)
            cmds.append((n, cmd))
            cmd = "/sbin/ethtool -K %s gro off lro off rx off tx off gso off" % (n.interface)
            cmds.append((n, cmd))

        self.executeParallel(cmds)
