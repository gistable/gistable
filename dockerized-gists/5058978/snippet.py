import sys

"""
Resolve the DNS/IP address of a given domain
data returned is in the format:
(name, aliaslist, addresslist)
@filename resolveDNS.py
@version 1.01 (python ver 2.7.3)
@author LoanWolffe
"""

def getIP(d):
    """
    This method returns the first IP address string
    that responds as the given domain name
    """
    try:
        data = socket.gethostbyname(d)
        ip = repr(data)
        return ip
    except Exception:
        # fail gracefully!
        return False
#
def getIPx(d):
    """
    This method returns an array containing
    one or more IP address strings that respond
    as the given domain name
    """
    try:
        data = socket.gethostbyname_ex(d)
        ipx = repr(data[2])
        return ipx
    except Exception:
        # fail gracefully!
        return False
#
def getHost(ip):
    """
    This method returns the 'True Host' name for a
    given IP address
    """
    try:
        data = socket.gethostbyaddr(ip)
        host = repr(data[0])
        return host
    except Exception:
        # fail gracefully
        return False
#
def getAlias(d):
    """
    This method returns an array containing
    a list of aliases for the given domain
    """
    try:
        data = socket.gethostbyname_ex(d)
        alias = repr(data[1])
        #print repr(data)
        return alias
    except Exception:
        # fail gracefully
        return False



if __name__ == "__main__":
    for f in sys.stdin:
        f = f.strip()
        try:
            result = socket.inet_aton(f)
            print f,
            hostname = getHost(f)
            if hostname: print " " + hostname.replace('\'', '' )
        except socket.error:
            print f,
            ip = getIP(f)
            if ip: print " " + ip.replace('\'', '' )



