>>>import re
>>>list = ['a', '1', 'bc', '-b', '2a','100']
>>>r = re.compile("[a-z]")
>>>[x for x in list if r.mathch(x)]
['a','bc']