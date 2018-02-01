"""
Example of how calculations on the secp256k1 curve work.

secp256k1 is the name of the elliptic curve used by bitcoin

see http://bitcoin.stackexchange.com/questions/25382

"""
p = 2**256 - 2**32 - 977

def inverse(x, p):
    """
    Calculate the modular inverse of x ( mod p )
    
    the modular inverse is a number such that:
    
    (inverse(x, p) * x) % p  ==  1 
    
    you could think of this as: 1/x
    """
    inv1 = 1
    inv2 = 0
    while p != 1 and p!=0:
        inv1, inv2 = inv2, inv1 - inv2 * (x / p)
        x, p = p, x % p

    return inv2


def dblpt(pt, p):
    """
    Calculate pt+pt = 2*pt
    """
    if pt is None:
        return None
    (x,y)= pt
    if y==0:
        return None 
        
    # Calculate 3*x^2/(2*y)  modulus p
    slope= 3*pow(x,2,p)*inverse(2*y,p)
    
    xsum= pow(slope,2,p)-2*x
    ysum= slope*(x-xsum)-y
    return (xsum%p, ysum%p)

def addpt(p1,p2, p):
    """
    Calculate p1+p2
    """
    if p1 is None or p2 is None:
        return None
    (x1,y1)= p1
    (x2,y2)= p2
    if x1==x2:
        return dblpt(p1, p)
        
    # calculate (y1-y2)/(x1-x2)  modulus p
    slope=(y1-y2)*inverse(x1-x2, p)
    xsum= pow(slope,2,p)-(x1+x2)
    ysum= slope*(x1-xsum)-y1
    return (xsum%p, ysum%p)

def ptmul(pt,a, p):
    """
    Scalar multiplication: calculate pt*a
    
    basically adding pt to itself a times
    """
    scale= pt
    acc=None
    while a:
        if a&1:
            if acc is None:
                acc= scale
            else:
                acc= addpt(acc,scale, p)
        scale= dblpt(scale, p)
        a >>= 1
    return acc


def isoncurve(pt,p):
    """
    returns True when pt is on the secp256k1 curve
    """
    (x,y)= pt
    return (y**2 - x**3 - 7)%p == 0

# (Gx,Gy)  is the secp256k1 generator point
Gx=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
g= (Gx,Gy)
g2=dblpt(g, p)
print "    2*G= (%x,%x)" % g2
print "  G+2*G= (%x,%x)" % addpt(g, g2, p)
print "2*G+2*G= (%x,%x)" % addpt(g2, g2, p)

privkey= 0xf8ef380d6c05116dbed78bfdd6e6625e57426af9a082b81c2fa27b06984c11f3
print " -> pubkey= (%x,%x)" % ptmul(g, privkey, p)

"""
for reference, the numbers printed should be:

    2*G= (c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5,1ae168fea63dc339a3c58419466ceaeef7f632653266d0e1236431a950cfe52a)
  G+2*G= (f9308a019258c31049344f85f89d5229b531c845836f99b08601f113bce036f9,388f7b0f632de8140fe337e62a37f3566500a99934c2231b6cb9fd7584b8e672)
2*G+2*G= (e493dbf1c10d80f3581e4904930b1404cc6c13900ee0758474fa94abe8c4cd13,51ed993ea0d455b75642e2098ea51448d967ae33bfbdfe40cfe97bdc47739922)
 -> pubkey= (71ee918bc19bb566e3a5f12c0cd0de620bec1025da6e98951355ebbde8727be3,37b3650efad4190b7328b1156304f2e9e23dbb7f2da50999dde50ea73b4c2688)
"""
