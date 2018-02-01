"""

This is an EXPERIMENTAL password hash with time and memory parameters,
such that the time parameter does not affect the memory required (but
does affect the number of memory accesses).

This was quickly designed, with no real test, so it's probably a silly
design and the code may be broken. Therefore, please:
- Do not use it to hash real passwords! 
- Attack it! (circumvent the time/memory requirements, find biases...)


Parameters:
  h      Hash function with the hashlib common interface 
         (at least digest() and hexdigest() should be implemented)
  pwd    Password, a string 
  salt   Salt, a string 
  ptime  Time parameter, an integer > 0
  pmem   Memory parameter, an integer > 0


Back-of-the-enveloppe time and space requirements: 

  Time: ~ 1.5*ptime*pmem compression evaluations, for any of the functions
  in hashlib; for other functions, it depends on the hash and block
  lengths and on the padding rule

  Memory: ~ hlen*pmem bytes, where hlen is the byte length of a digest 
  

Examples with approximate timings measured on an Ivy Bridge:

  phs( hashlib.sha256, 'password', 'salt', 2, 2**16 )
  uses ~2MB, runs in ~250ms

  phs( hashlib.sha256, 'password', 'salt', 1, 2**17 )
  uses ~4MB, runs in ~250ms 

  (An optimized C implementation would probably be much faster.)


  JP Aumasson / @veorq / jeanphilippe.aumasson@gmail.com
  2013
"""

def phs( h, pwd, salt, ptime, pmem ):
  s = h( h( pwd + salt ).digest() + salt ).digest()
  hlen = len(s)
  for t in xrange(ptime):  
    for m in xrange(pmem):
      s = s + h( s[-hlen:] ).digest()
    s = h( s[::-1] ).digest()
  return h(s).hexdigest()

import hashlib
