"""
Original raw text:
http://sherlock-holm.es/ascii/

Trimmed Format:
- Each line is a complete paragraph.
- Each line is ended with two new line characters ('\n\n') (including the last line).
- Disclaimer at the end of the raw text is not deleted, you need to delete it yourself.
"""

input = open("cano.txt", "r")
output = open("cano-trim.txt", "w")

newParagraph = True
line = input.readline()

while line:
  n = len(line)
  if n > 5 and line[5] != ' ' and line[5] != '\n':
    if not(newParagraph):
      output.write(' ')
    else:
      newParagraph = False
    output.write(line.strip())
  elif n == 1 and line[0] == '\n' and not(newParagraph):
    output.write('\n\n')
    newParagraph = True
  line = input.readline()
