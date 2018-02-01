# INCORRECT! DON'T DO THIS!
>>> x = "www.Alliancefrançaise.nu"  # This is the problematic line. Forgot to make this a Unicode string.
>>> print x
www.Alliancefrançaise.nu
>>> x.encode('punycode')
'www.Alliancefranaise.nu-h1a31e'
>>> x.encode('punycode').decode('punycode')
u'www.Alliancefran\xc3\xa7aise.nu'
>>> print x.encode('punycode').decode('punycode')
www.AlliancefranÃ§aise.nu
>>> print x
www.Alliancefrançaise.nu
>>> x == x.encode('punycode').decode('punycode')
/usr/bin/ipython:1: UnicodeWarning: Unicode equal comparison failed to convert both arguments to Unicode - interpreting them as being unequal
  #!/usr/bin/env python
False

# CORRECT FOR PUNYCODE (ALMOST THE BEST):
>>> x = u"www.Alliancefrançaise.nu"  # The difference! The Unicode string (decoded) string must be Unicode type
>>> print x
www.Alliancefrançaise.nu
>>> x.encode('punycode')
'www.Alliancefranaise.nu-dbc'
>>> x.encode('punycode').decode('punycode')
u'www.Alliancefran\xe7aise.nu'
>>> print x.encode('punycode').decode('punycode')
www.Alliancefrançaise.nu
>>> x == x.encode('punycode').decode('punycode')
True

# BEST ('idna' is preferable to 'punycode', see http://en.wikipedia.org/wiki/Punycode and https://docs.python.org/2/library/codecs.html#module-encodings.idna ) :
>>> x = u"www.Alliancefrançaise.nu"
>>> print x
www.Alliancefrançaise.nu
>>> x.encode('idna')
www.xn--alliancefranaise-npb.nu
>>> x.encode('idna').decode('idna')
u'www.alliancefran\xe7aise.nu'
>>> print x.encode('idna').decode('idna')
www.alliancefrançaise.nu
>>> x == x.encode('idna').decode('idna')
True