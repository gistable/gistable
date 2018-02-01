import commands
def getmac(iface):
    mac = commands.getoutput("ifconfig " + iface + "| grep HWaddr | awk '{ print $5 }'")
    if len(mac)==17:
        return mac

getmac('eth0')