#http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
import re, string

table = string.maketrans("","")
regex = re.compile('[%s]' % re.escape(string.punctuation))

def test_re(s):  # From Vinko's solution, with fix.
    return regex.sub('', s)

def test_trans(s):
    return s.translate(table, string.punctuation)
    
#sets      : 19.8566138744
#regex     : 6.86155414581
#translate : 2.12455511093
#replace   : 28.4436721802
