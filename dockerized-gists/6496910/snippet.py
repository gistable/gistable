#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  odbc_trace_parser.py
#
#  Copyright 2013 Spencer McIntyre <zeroSteiner@gmail.com>
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import argparse
import sys

SQL_SUCCESS_CODES = [0, 1]

def colorize(message, color, bold = False):
	color_map = {
		'black':30,
		'red':31,
		'green':32,
		'yellow':33,
		'blue':34,
		'magenta':35,
		'cyan':36,
		'white':37
	}
	return "\033[{0};{1}m{2}\033[1;m".format(int(bold), color_map[color], message)

class FunctionCall(object):
	def __init__(self):
		self.name = ''
		self.result = 0
		self.result_code = ''
		self.parameters = []
		self.handle = None

	def __str__(self):
		return self.pretty_print()

	def pretty_print(self, print_pointer_data = False, use_colors = False):
		if use_colors:
			log_line = colorize(self.name, 'blue', True) + '('
		else:
			log_line = self.name + '('
		for param in self.parameters:
			log_line += param['name'] + ' '
			if param['is_pointer']:
				log_line += '*'
			log_line += param['value']
			if param['pointer_data']:
				log_line += ' ' + param['pointer_data']
			log_line += ', '
		log_line = log_line[:-2] + ') '
		status_str = str(self.result) + ' ' + self.result_code
		if use_colors:
			if self.result in SQL_SUCCESS_CODES:
				log_line += colorize(status_str, 'green', True)
			else:
				log_line += colorize(status_str, 'red', True)
		else:
			log_line += status_str
		return log_line

	def add_parameter(self, name, value, is_pointer = False, pointer_data = None):
		if name == 'HSTMT' and self.handle == None:
			self.handle = value
		self.parameters.append({'name':name, 'is_pointer':is_pointer, 'value':value, 'pointer_data':pointer_data})

def main():
	parser = argparse.ArgumentParser(description = 'Parse ODBC Trace Logs', conflict_handler = 'resolve')
	status_filter = parser.add_mutually_exclusive_group()
	status_filter.add_argument('--success', dest = 'success_only', action = 'store_true', default = False, help = 'only show calls which returned successfully')
	status_filter.add_argument('--failure', dest = 'failure_only', action = 'store_true', default = False, help = 'only show calls which did not return successfully')
	function_name_filter = parser.add_mutually_exclusive_group()
	function_name_filter.add_argument('--ignore', dest = 'ignore_names', nargs = '*', default = [], help = 'a list of functions which should be ignored')
	function_name_filter.add_argument('--include', dest = 'include_names', nargs = '*', default = [], help = 'a list of functions which should be included')
	parser.add_argument('--handle', dest = 'handle', default = None, help = 'only show calls involving this handle')
	parser.add_argument('-c', '--colorize', dest = 'colorize', action = 'store_true', default = False, help = 'colorize the output')
	parser.add_argument('-o', '--out', dest = 'out_file', default = '-', type = argparse.FileType('w'), help = 'file to write the parsed data to')
	parser.add_argument('in_file', type = argparse.FileType('r'), help = 'path to the unparsed log file')
	arguments = parser.parse_args()

	in_f = arguments.in_file
	out_file = arguments.out_file
	in_exit = False
	function = FunctionCall()
	for line in in_f:
		is_param = line.startswith('\t\t')
		line = line.strip()
		line = line.split()
		if len(line) == 5 and line[3] == 'ENTER':
			in_exit = False
			function.name = line[4]
		elif len(line) == 10 and line[3] == 'EXIT':
			in_exit = True
			function.result = int(line[-2])
			function.result_code = line[-1][1:-1]
			log_this_call = True
			if arguments.success_only and function.result not in SQL_SUCCESS_CODES:
				log_this_call = False
			elif arguments.failure_only and function.result in SQL_SUCCESS_CODES:
				log_this_call = False
			if function.name in arguments.ignore_names:
				log_this_call = False
			elif len(arguments.include_names) and function.name not in arguments.include_names:
				log_this_call = False
			if arguments.handle and function.handle != arguments.handle:
				log_this_call = False
			if log_this_call:
				out_file.write(function.pretty_print(True, arguments.colorize) + '\n')
				out_file.flush()
			function = FunctionCall()
		elif is_param and not in_exit:
			if line[1] == '*':
				pointer_data = ''
				if len(line) > 4 and line[5].startswith('"'):
					pointer_data = ' '.join(line[5:])[1:-1]
				function.add_parameter(line[0], line[2], is_pointer = True, pointer_data = pointer_data)
			else:
				function.add_parameter(line[0], line[1])
	return 0

if __name__ == '__main__':
	main()
