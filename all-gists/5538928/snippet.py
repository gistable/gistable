def match(pattern,text):
    if pattern[0] == '^':
       return match_here(pattern[1:], text)

    if match_here(pattern,text):
          return 1

    while text:
       if match_here(pattern,text):
          return 1
       text = text[1:]
    return 0

def match_here(pattern,text):
    if not pattern:
       return 1
    if len(pattern) > 1 and pattern[1] == '*':
       return match_star(pattern[0], pattern[2:],text)
    if pattern[0] == '$' and len(pattern) == 1:
       return text == ''
    if text and (pattern[0] == '.' or pattern[0] == text[0]):
       return match_here(pattern[1:],text[1:])
    return 0

def match_star(char,pattern,text):
    if (match_here(pattern, text)):
        return 1
    while text and (text[0] == char or char == '.'):
        if match_here(pattern,text):
           return 1
        text = text[1:]

if __name__ == "__main__":
   print match('.*', 'a')
   print match('a*b', 'aab')
   print match('a*c', 'aab')
