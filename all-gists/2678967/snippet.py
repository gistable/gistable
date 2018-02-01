import re

def strip_margin(text):
    return re.sub('\n[ \t]*\|', '\n', text)

def strip_heredoc(text):
    indent = len(min(re.findall('\n[ \t]*(?=\S)', text) or ['']))
    pattern = r'\n[ \t]{%d}' % (indent - 1)
    return re.sub(pattern, '\n', text)

print strip_margin(
"""I was reading a book "Programming Scala" and
  |noticed that there is stripMargin method in
  |RichString class in Scala.
  |
  |It's damn useful.""")

print strip_heredoc(
"""
   And... 
   There is strip_heredoc in Ruby's String object.
   Now you don't need a leader "|".
   It does do a great job even if the string has
       multi
           level
               indention.
  
   It's damn useful too.
   especially for usage docs like:

      -h       This message

   yay or nay?""")