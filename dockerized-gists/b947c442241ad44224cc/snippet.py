def ip2hex(cidr, router):
    addr, mask = cidr.split("/")
    mask = int(mask)
    addr = [("%2s" % hex(int(i))[2:]).replace(" ", "0") for i in addr.split(".") if i != "0"]
    parts = mask/8 - len(addr)
    if mask%8 > 0:
        parts += 1
    if parts > 0:
        for i in range(int(parts)):
            addr.append("00")

    r = []
    for i in router.split("."):
        r.append(("%2s" % hex(int(i))[2:]).replace(" ", "0"))

    addr.insert(0, hex(mask)[2:])
    return "".join(addr), "".join(r)


def routes2hex(routes):
    routers = []
    for cidr, router in routes.items():
        a,r = ip2hex(cidr, router)
        routers.append(a)
        routers.append(r)

    return "0x%s" % ("".join(routers).upper())

# print routes2hex({
#  "192.168.6.0/24": "192.168.5.4",
#  "10.128.0.0/20": "192.168.5.2",
#  "192.168.192.0/24": "192.168.5.3"
#})
# 0x18C0A8C0C0A80503140A8000C0A8050218C0A806C0A80504