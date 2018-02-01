>>> import re
>>> array = ["1test", "2test", "notanumber", "3bananas"]

>>> re.match("^[1-9]", "1testing")
<_sre.SRE_Match object at 0x1004743d8>

#a synonym for [1-9] is \d
>>> re.match("^\d", "1testing")
<_sre.SRE_Match object at 0x100474440>

#here's one way
>>> 1 if re.match("^\d", "1testing") else 0
1
>>> 1 if re.match("^\d", "testing") else 0
0
>>> [1 if re.match("^\d", i) else 0 for i in array]
[1, 1, 0, 1]
>>> sum(1 if re.match("^\d", i) else 0 for i in array)
3

#here's another way
>>> n = 0
>>> for i in array:
...   if re.match("^\d", i): n+=1
... 
>>> n
3
