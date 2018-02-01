#!/usr/bin/env python

import argparse
import re

parser = argparse.ArgumentParser(description=
  'Create a KTouch lesson from a text file. Most white space will be stripped.')
parser.add_argument(
  'input_filename', help='Name of text file to read')
parser.add_argument(
  '-o --output-file', metavar='<name>', dest='output',
  default='text2.ktouch.xml', help='Name of KTouch lesson file to write')
parser.add_argument(
  '-m --max-line-length', metavar='<length>', type=int, default=80,
  dest='max_line_length', help='Maximum number of characters per line')
parser.add_argument(
  '-l --lines-per-level', metavar='<num-lines>', type=int, default=10,
  dest='lines_per_level', help='Number of lines in each level' )
parser.add_argument(
  '-n --number_of_levels', metavar='<num-levels>', type=int, default=1,
  dest='num_levels', help='Number of levels to create' )
#parser.add_argument(
#  '-p --preserve-line-breaks', action='store_const', const=True, dest='is_preserve_breaks', help=
#  'In KTouch, lines will end where newlines appear in the text file. Empty lines will still be removed.' )

args = parser.parse_args()

output_file = open( args.output, 'w' );
output_file.write( '<?xml version="1.0" encoding="UTF-8"?>\n' )
output_file.write( '<KTouchLecture>\n' )
output_file.write( ' <Title>User generated lesson</Title>\n' )
output_file.write( ' <Comment>Generated using text2ktouch.py</Comment>\n' )
output_file.write( ' <FontSuggestions>Monospace</FontSuggestions>\n' )
output_file.write( ' <Levels>\n' )

input_file = open( args.input_filename, 'r' );
buf = ""
eof = False
tgt_buf_len = 5 * args.max_line_length

for level in range(args.num_levels):
  output_file.write( '  <Level>\n' )
  output_file.write(
    '   <NewCharacters>Could be anything :S</NewCharacters>\n' )

  for line in range(args.lines_per_level):

    if len(buf) < tgt_buf_len:
      new_chars = input_file.read( tgt_buf_len )
      if new_chars == "":
        eof = True
      new_chars = re.sub( r'[\s]+', ' ', new_chars )
      buf += new_chars

    line_text = buf[:args.max_line_length].strip()
    line_text = line_text.replace( '&', '&amp;' )
    line_text = line_text.replace( '<', '&lt;' )
    buf = buf[args.max_line_length:].strip()
    output_file.write( '   <Line>' + line_text + '</Line>\n' )

    if buf == "" and eof:
      break

  output_file.write( '  </Level>\n' )

  if buf == "" and eof:
    break

input_file.close
output_file.write( ' </Levels>\n' )
output_file.write( '</KTouchLecture>\n' )
output_file.close

# TODO - split lines on whitespace
# TODO - implement newline preservation
